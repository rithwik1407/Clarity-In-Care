from fastapi import APIRouter, UploadFile, File, Depends, HTTPException
from sqlalchemy.orm import Session
from database.models import get_db, Patient, Scan
from app.schemas import PatientCreate, PatientResponse, ScanCreate, PredictionResponse, ScanHistoryResponse
import uuid
from datetime import datetime

router = APIRouter(prefix="/patients", tags=["patients"])


@router.post("/", response_model=PatientResponse)
def create_patient(patient: PatientCreate, db: Session = Depends(get_db)):
    """Create a new patient."""
    patient_id = str(uuid.uuid4())
    db_patient = Patient(
        id=patient_id,
        name=patient.name,
        age=patient.age,
        email=patient.email,
        phone=patient.phone,
        medical_history=patient.medical_history,
    )
    db.add(db_patient)
    db.commit()
    db.refresh(db_patient)
    return db_patient


@router.get("/{patient_id}", response_model=PatientResponse)
def get_patient(patient_id: str, db: Session = Depends(get_db)):
    """Get patient details."""
    patient = db.query(Patient).filter(Patient.id == patient_id).first()
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")
    return patient


@router.get("/", response_model=list[PatientResponse])
def list_patients(skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
    """List all patients."""
    patients = db.query(Patient).offset(skip).limit(limit).all()
    return patients
