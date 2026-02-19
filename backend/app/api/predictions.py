from fastapi import APIRouter, UploadFile, File, Depends, HTTPException
from sqlalchemy.orm import Session
from database.models import get_db, Scan
from app.schemas import PredictionResponse, ScanHistoryResponse
import uuid
import io
from datetime import datetime

# Lazy imports to handle missing optional dependencies
try:
    import numpy as np
    import torch
    from preprocessing.image_processor import ImagePreprocessor
    from models.dr_model import DRDetectionModel
    from explainability.grad_cam import GradCAM, heatmap_to_bytes
    TORCH_AVAILABLE = True
except ImportError as e:
    print(f"Warning: Neural network dependencies not available: {e}")
    TORCH_AVAILABLE = False

try:
    from cloud_storage.s3_storage import S3Storage
    S3_AVAILABLE = True
    s3_storage = None  # Will be initialized on first use
except ImportError as e:
    print(f"Warning: S3 not available: {e}")
    S3_AVAILABLE = False
    s3_storage = None

router = APIRouter(prefix="/predict", tags=["predictions"])

# Initialize model and storage (cached at startup)
dr_model = None
grad_cam = None


def get_model():
    """Lazy load model on first use."""
    global dr_model, grad_cam
    if dr_model is None:
        dr_model = DRDetectionModel()
        grad_cam = GradCAM(dr_model.model, dr_model.get_target_layer())
    return dr_model, grad_cam


def get_s3_storage():
    """Lazy load S3 storage on first use."""
    global s3_storage
    if s3_storage is None:
        s3_storage = S3Storage()
    return s3_storage


def get_s3_storage():
    """Lazy load S3 storage on first use."""
    global s3_storage
    if s3_storage is None:
        s3_storage = S3Storage()
    return s3_storage


@router.post("/", response_model=PredictionResponse)
async def predict_dr(
    patient_id: str,
    visit_type: str,
    file: UploadFile = File(...),
    notes: str = None,
    db: Session = Depends(get_db),
):
    """
    Upload retinal image and get DR prediction.
    
    Args:
        patient_id: Patient ID
        visit_type: pre-treatment, follow-up, or post-treatment
        file: Retinal fundus image
        notes: Optional clinical notes
        db: Database session
    
    Returns:
        Prediction with DR severity, confidence, and heatmap
    """
    if not TORCH_AVAILABLE:
        raise HTTPException(
            status_code=503,
            detail="Model not available. Install PyTorch dependencies: pip install torch torchvision"
        )
    
    if not S3_AVAILABLE:
        raise HTTPException(
            status_code=503,
            detail="S3 storage not available. Install boto3: pip install boto3"
        )
    
    try:
        # Read file
        file_content = await file.read()
        
        # Validate image
        if not ImagePreprocessor.validate_image(file_content, file.filename):
            raise HTTPException(
                status_code=400,
                detail="Invalid image format. Allowed: JPG, JPEG, PNG"
            )
        
        # Preprocess image
        preprocessed_image = ImagePreprocessor.preprocess(file_content, file.filename)
        
        # Get model
        dr_model_instance, grad_cam_instance = get_model()
        
        # Convert to tensor
        image_tensor = torch.from_numpy(preprocessed_image).float().unsqueeze(0)
        
        # Predict
        dr_severity, confidence, class_idx = dr_model_instance.predict(preprocessed_image)
        
        # Generate heatmap
        cam = grad_cam_instance.generate_cam(image_tensor, target_class=class_idx)
        
        # Overlay heatmap on original image
        original_image = ImagePreprocessor.load_image_for_visualization(file_content)
        overlayed_image = GradCAM.overlay_heatmap(original_image, cam)
        
        # Convert overlayed image to bytes
        heatmap_bytes = heatmap_to_bytes(overlayed_image)
        
        # Upload original image to S3
        storage = get_s3_storage()
        image_s3_key = storage.upload_image(file_content, patient_id, "original")
        
        # Upload heatmap to S3
        scan_id = str(uuid.uuid4())
        heatmap_s3_key = storage.upload_heatmap(heatmap_bytes, patient_id, scan_id)
        
        # Save to database
        scan = Scan(
            id=scan_id,
            patient_id=patient_id,
            image_s3_key=image_s3_key,
            heatmap_s3_key=heatmap_s3_key,
            visit_type=visit_type,
            dr_severity=dr_severity,
            confidence_score=confidence,
            scan_timestamp=datetime.utcnow(),
            notes=notes,
        )
        db.add(scan)
        db.commit()
        db.refresh(scan)
        
        # Generate presigned URLs
        image_url = storage.get_presigned_url(image_s3_key)
        heatmap_url = storage.get_presigned_url(heatmap_s3_key)
        
        return PredictionResponse(
            scan_id=scan.id,
            patient_id=scan.patient_id,
            dr_severity=scan.dr_severity,
            confidence_score=scan.confidence_score,
            heatmap_url=heatmap_url,
            image_url=image_url,
            scan_timestamp=scan.scan_timestamp,
            visit_type=scan.visit_type,
        )
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Prediction failed: {str(e)}"
        )


@router.get("/patient/{patient_id}/history", response_model=list[ScanHistoryResponse])
def get_scan_history(patient_id: str, db: Session = Depends(get_db)):
    """Get all scans for a patient."""
    if not S3_AVAILABLE:
        raise HTTPException(
            status_code=503,
            detail="S3 storage not available"
        )
    
    scans = db.query(Scan).filter(Scan.patient_id == patient_id).order_by(Scan.scan_timestamp.desc()).all()
    
    storage = get_s3_storage()
    result = []
    for scan in scans:
        try:
            image_url = storage.get_presigned_url(scan.image_s3_key)
        except:
            image_url = None
        
        result.append(ScanHistoryResponse(
            id=scan.id,
            patient_id=scan.patient_id,
            dr_severity=scan.dr_severity,
            confidence_score=scan.confidence_score,
            scan_timestamp=scan.scan_timestamp,
            visit_type=scan.visit_type,
            image_url=image_url,
        ))
    
    return result
