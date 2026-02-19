# Backend File Structure & Documentation

## 📋 Quick Navigation

### Start Here
1. **[SETUP_GUIDE.md](SETUP_GUIDE.md)** - Quick 5-minute setup
2. **[README.md](README.md)** - Full documentation
3. **[DEPLOYMENT.md](DEPLOYMENT.md)** - Cloud deployment

---

## 📁 Directory Structure

### Core Application (`app/`)

#### `app/main.py` 
- **Purpose**: FastAPI application entry point
- **Contains**: 
  - App initialization
  - Router registration
  - Health check endpoint
  - CORS middleware

#### `app/schemas.py`
- **Purpose**: Pydantic models for request/response validation
- **Models**:
  - `PatientCreate`, `PatientResponse` - Patient data
  - `ScanCreate`, `PredictionResponse` - Scan/prediction data
  - `ScanHistoryResponse` - Historical data
  - `HealthResponse` - Health check

#### `app/api/patients.py`
- **Purpose**: Patient management endpoints
- **Endpoints**:
  - `POST /patients/` - Create patient
  - `GET /patients/{id}` - Get patient details
  - `GET /patients/` - List all patients

#### `app/api/predictions.py`
- **Purpose**: DR detection endpoints
- **Endpoints**:
  - `POST /predict/` - Upload image and predict
  - `GET /predict/patient/{id}/history` - Scan history

---

### Configuration (`config/`)

#### `config/settings.py`
- **Purpose**: Configuration management
- **Contains**:
  - API settings (title, version, description)
  - Server config (host, port, debug)
  - AWS S3 credentials
  - Database URL
  - Model paths
  - Image processing parameters (size, CLAHE)
  - DR classes and thresholds

#### `config/__init__.py`
- Module initialization

---

### Database (`database/`)

#### `database/models.py`
- **Purpose**: Database models and initialization
- **Models**:
  - `Patient` - Patient metadata
  - `Scan` - Scan results and predictions
- **Functions**:
  - `get_db()` - Session dependency for FastAPI
  - `init_db()` - Initialize tables

#### `database/__init__.py`
- Module initialization

---

### Image Preprocessing (`preprocessing/`)

#### `preprocessing/image_processor.py`
- **Purpose**: Image preprocessing pipeline
- **Classes**: `ImagePreprocessor`
- **Methods**:
  - `validate_image()` - Check format/size
  - `resize_image()` - Resize to standard size (224x224)
  - `apply_clahe()` - Enhance contrast
  - `normalize_image()` - Normalize pixel values
  - `preprocess()` - Complete pipeline
  - `load_image_for_visualization()` - Load for display

#### `preprocessing/__init__.py`
- Module initialization

---

### ML Models (`models/`)

#### `models/dr_model.py`
- **Purpose**: DR detection model wrapper
- **Class**: `DRDetectionModel`
- **Methods**:
  - `__init__()` - Load model from weights
  - `_load_model()` - Initialize ResNet-50
  - `predict()` - Get DR prediction
  - `get_target_layer()` - For Grad-CAM

#### `models/__init__.py`
- Module initialization

---

### Explainability (`explainability/`)

#### `explainability/grad_cam.py`
- **Purpose**: Grad-CAM implementation for XAI
- **Class**: `GradCAM`
- **Methods**:
  - `__init__()` - Initialize with model/layer
  - `generate_cam()` - Generate attention heatmap
  - `overlay_heatmap()` - Overlay on original image
- **Functions**:
  - `heatmap_to_bytes()` - Convert to JPEG bytes

#### `explainability/__init__.py`
- Module initialization

---

### Cloud Storage (`cloud_storage/`)

#### `cloud_storage/s3_storage.py`
- **Purpose**: AWS S3 integration
- **Class**: `S3Storage`
- **Methods**:
  - `upload_image()` - Upload retinal image
  - `upload_heatmap()` - Upload Grad-CAM heatmap
  - `get_presigned_url()` - Generate temporary access URL
  - `download_image()` - Retrieve image from S3

#### `cloud_storage/__init__.py`
- Module initialization

---

### Scripts (`scripts/`)

#### `scripts/train_model.py`
- **Purpose**: Model training script
- **Classes**:
  - `DRDataset` - PyTorch dataset loader
  - `DRDetectionTrainer` - Training orchestration
- **Methods**:
  - `train()` - Training loop
  - `validate()` - Validation
  - `save_model()` - Save weights
- **Usage**: `python scripts/train_model.py`

---

## 🔧 Configuration Files

### `main.py`
- **Purpose**: Application entry point
- **Usage**: `python main.py`
- **Starts**: FastAPI server on port 8000

### `requirements.txt`
- **Purpose**: Python dependencies
- **Key packages**:
  - `fastapi==0.104.1` - Web framework
  - `torch==2.0.1` - Deep learning
  - `torchvision==0.15.2` - Vision models
  - `opencv-python==4.8.1.78` - Image processing
  - `boto3==1.28.85` - AWS S3
  - `sqlalchemy==2.0.23` - Database ORM

### `.env.example`
- **Purpose**: Environment variables template
- **Copy to**: `.env` (never commit!)
- **Contains**:
  - AWS credentials
  - Database URL
  - Model path
  - API host/port

### `Dockerfile`
- **Purpose**: Docker image definition
- **Key steps**:
  - Python 3.10 base image
  - Install dependencies
  - Copy app code
  - Expose port 8000
  - Run FastAPI

### `docker-compose.yml`
- **Purpose**: Docker Compose orchestration
- **Services**: API service with volumes
- **Networking**: Internal network

### `.gitignore`
- **Purpose**: Git ignore patterns
- **Ignores**:
  - Environment files (.env)
  - Python cache (__pycache__)
  - Virtual environments
  - Models and data
  - IDE files

---

## 📖 Documentation Files

### `README.md`
- Complete documentation
- Project structure explanation
- Installation instructions
- API endpoints reference
- Docker usage
- Cloud deployment
- Troubleshooting guide
- **Pages**: 300+ lines

### `DEPLOYMENT.md`
- AWS cloud deployment guide
- Architecture diagrams
- Step-by-step deployment
- ECS/EC2 setup
- Security checklist
- Monitoring setup
- Cost optimization
- **Pages**: 250+ lines

### `SETUP_GUIDE.md`
- Quick start guide
- MVP feature set
- Next steps roadmap
- Architecture highlights
- Success criteria
- **Pages**: 150+ lines

### `example_usage.py`
- Practical API usage examples
- Patient creation
- Prediction workflow
- History retrieval
- Error handling
- Color-coded output

---

## 🔗 Relationships

```
main.py
├── Imports: FastAPI
├── Includes: app/api/patients.py
├── Includes: app/api/predictions.py
│   ├── Uses: database/models.py (for DB)
│   ├── Uses: preprocessing/image_processor.py (for image processing)
│   ├── Uses: models/dr_model.py (for prediction)
│   ├── Uses: explainability/grad_cam.py (for heatmap)
│   └── Uses: cloud_storage/s3_storage.py (for S3 upload)
├── Includes: app/schemas.py (for validation)
└── Uses: config/settings.py (for config)
```

---

## 📊 MVP API Flow

```
1. Client Request (image + patient_id)
   ↓
2. FastAPI (app/api/predictions.py)
   ├── Validation (app/schemas.py)
   ├── Image Processing (preprocessing/image_processor.py)
   │   └── Resize, CLAHE, Normalize
   ├── DR Prediction (models/dr_model.py)
   ├── Grad-CAM Heatmap (explainability/grad_cam.py)
   ├── S3 Upload (cloud_storage/s3_storage.py)
   ├── Database Save (database/models.py)
   └── Response with URLs
```

---

## 🚀 How to Use

### 1. Setup
```bash
cp .env.example .env
# Edit .env with AWS credentials
pip install -r requirements.txt
```

### 2. Run Locally
```bash
python main.py
# API at http://localhost:8000/docs
```

### 3. Train Model
```bash
# First, download a DR dataset
python scripts/train_model.py
```

### 4. Make API Calls
```bash
python example_usage.py
```

### 5. Deploy
```bash
# Docker
docker-compose up

# AWS (see DEPLOYMENT.md)
# AWS EC2 + ECS setup
```

---

## 📝 File Statistics

| Category | Files | Purpose |
|----------|-------|---------|
| API Code | 4 | Core application logic |
| Config | 2 | Settings management |
| Database | 2 | Data models |
| Processing | 2 | Image preprocessing |
| Models | 2 | ML model wrapper |
| XAI | 2 | Explainability |
| Storage | 2 | Cloud integration |
| Scripts | 1 | Training utilities |
| Documentation | 4 | Guides & examples |
| Config Files | 5 | Docker, env, git |
| **Total** | **26** | **Complete backend** |

---

## ✅ What's Ready

- ✅ FastAPI backend structure
- ✅ Image preprocessing pipeline
- ✅ DR detection model integration
- ✅ Grad-CAM explainability
- ✅ AWS S3 cloud storage
- ✅ SQLite database (PostgreSQL ready)
- ✅ RESTful API endpoints
- ✅ Docker deployment
- ✅ Complete documentation
- ✅ Training scripts
- ✅ Example usage code

---

## ⏳ What's Next

1. **Download dataset** (Messidor-2, EyePACS, or Aptos)
2. **Organize data** in `data/train/` and `data/val/`
3. **Train model**: `python scripts/train_model.py`
4. **Configure AWS**: Add credentials to `.env`
5. **Test API**: `python main.py` + `python example_usage.py`
6. **Deploy**: Follow DEPLOYMENT.md for AWS

---

**Created:** February 2026  
**Version:** 1.0 MVP  
**Status:** ✅ Ready for use
