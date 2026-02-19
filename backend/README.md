# Clarity in Care - Backend Documentation

## 🚀 Quick Start

### Prerequisites
- Python 3.9+
- pip or conda
- AWS S3 bucket (for image storage)
- CUDA-compatible GPU (recommended for model inference)

### Installation

1. **Clone and setup environment**
```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. **Install dependencies**
```bash
pip install -r requirements.txt
```

3. **Configure environment variables**
```bash
# Copy example and update with your values
cp .env.example .env

# Edit .env with your AWS credentials and configuration
# AWS_ACCESS_KEY_ID=your_key
# AWS_SECRET_ACCESS_KEY=your_secret
# S3_BUCKET_NAME=your-bucket-name
```

4. **Run the server**
```bash
python main.py
```

The API will be available at `http://localhost:8000`
- API Docs: `http://localhost:8000/docs`
- Health Check: `http://localhost:8000/health`

---

## 📊 Project Structure

```
backend/
├── app/                          # FastAPI application
│   ├── api/
│   │   ├── patients.py          # Patient management endpoints
│   │   └── predictions.py       # DR detection endpoints
│   ├── schemas.py               # Pydantic models for validation
│   └── __init__.py
├── config/                       # Configuration
│   └── settings.py              # App settings and env vars
├── database/                     # Database layer
│   └── models.py                # SQLAlchemy models
├── preprocessing/                # Image preprocessing
│   └── image_processor.py       # Image resizing, CLAHE, normalization
├── models/                       # ML model utilities
│   └── dr_model.py              # DR detection model wrapper
├── explainability/               # XAI components
│   └── grad_cam.py              # Grad-CAM implementation
├── cloud_storage/                # Cloud integration
│   └── s3_storage.py            # AWS S3 storage handler
├── scripts/                      # Utility scripts
│   └── train_model.py           # Model training script
├── main.py                       # FastAPI entry point
├── requirements.txt              # Python dependencies
├── .env.example                  # Environment variables template
├── Dockerfile                    # Docker configuration
└── docker-compose.yml            # Docker Compose setup
```

---

## 🧠 Model Training

### Step 1: Download Dataset

Choose one of the supported DR datasets:

**Option A: Messidor-2** (Open Access)
- Link: https://www.adcis.net/en/third-party/messidor2/
- Images: 1,474 retinal fundus images
- Classes: 0-4 (No DR to Proliferative)

**Option B: EyePACS** (Kaggle Dataset)
- Link: https://www.kaggle.com/datasets/mariaherrerot/eyepacs
- Images: 88,702 images
- Classes: 0-4 (No DR, Mild, Moderate, Severe, Proliferative)

**Option C: Aptos 2019** (Kaggle Competition)
- Link: https://www.kaggle.com/competitions/aptos2019-blindness-detection
- Images: 3,662 training images
- Classes: 0-4

### Step 2: Organize Data

```
backend/
└── data/
    ├── train/
    │   ├── images/          (training images)
    │   └── labels.csv       (image_name,label)
    └── val/
        ├── images/          (validation images)
        └── labels.csv       (image_name,label)
```

**labels.csv format:**
```csv
image1.jpg,0
image2.jpg,1
image3.jpg,2
...
```

### Step 3: Train Model

```bash
python scripts/train_model.py
```

The trained model weights will be saved to `models/dr_detection_model.pth`

**Training parameters** (edit in `train_model.py`):
- Epochs: 10
- Batch size: 32
- Learning rate: 0.001
- Optimizer: Adam

---

## 📡 API Endpoints (MVP)

### Health Check
```http
GET /health
```
Response:
```json
{
  "status": "ok",
  "version": "0.1.0",
  "model_loaded": true
}
```

### Create Patient
```http
POST /patients/
Content-Type: application/json

{
  "name": "John Doe",
  "age": 45,
  "email": "john@example.com",
  "phone": "+1234567890",
  "medical_history": "Type 2 Diabetes"
}
```

Response:
```json
{
  "id": "patient-uuid",
  "name": "John Doe",
  "age": 45,
  "email": "john@example.com",
  "phone": "+1234567890",
  "medical_history": "Type 2 Diabetes",
  "created_at": "2024-01-15T10:30:00",
  "updated_at": "2024-01-15T10:30:00"
}
```

### Get Patient
```http
GET /patients/{patient_id}
```

### List Patients
```http
GET /patients/?skip=0&limit=10
```

### DR Detection (Prediction)
```http
POST /predict/
Content-Type: multipart/form-data

- patient_id: patient-uuid (string)
- visit_type: pre-treatment (string: pre-treatment | follow-up | post-treatment)
- file: retinal_image.jpg (file)
- notes: Optional clinical notes (string)
```

Response:
```json
{
  "scan_id": "scan-uuid",
  "patient_id": "patient-uuid",
  "dr_severity": "Moderate",
  "confidence_score": 0.92,
  "heatmap_url": "https://s3.amazonaws.com/...",
  "image_url": "https://s3.amazonaws.com/...",
  "scan_timestamp": "2024-01-15T10:32:00",
  "visit_type": "pre-treatment"
}
```

### Get Patient Scan History
```http
GET /predict/patient/{patient_id}/history
```

Response:
```json
[
  {
    "id": "scan-uuid-1",
    "patient_id": "patient-uuid",
    "dr_severity": "Moderate",
    "confidence_score": 0.92,
    "scan_timestamp": "2024-01-15T10:32:00",
    "visit_type": "pre-treatment",
    "image_url": "https://s3.amazonaws.com/..."
  },
  ...
]
```

---

## 🐳 Docker Deployment

### Build Docker Image
```bash
docker build -t clarity-in-care:latest .
```

### Run with Docker Compose
```bash
# Create .env file with AWS credentials
docker-compose up -d
```

### View Logs
```bash
docker-compose logs -f api
```

### Stop Services
```bash
docker-compose down
```

---

## ☁️ Cloud Deployment

### Deploy to AWS EC2

1. **Create EC2 Instance**
   - AMI: Ubuntu 22.04
   - Instance type: t3.medium or larger
   - EBS: 50GB volume

2. **SSH into instance and setup**
```bash
# Update system
sudo apt-get update && sudo apt-get upgrade -y

# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# Clone repository and deploy
git clone <your-repo-url>
cd Clarity-In-Care/backend
docker-compose up -d
```

3. **Security**
   - Use API Gateway for authentication
   - Enable HTTPS with SSL/TLS
   - Restrict S3 bucket access
   - Set up VPC security groups

---

## 🔧 Configuration

### Settings (config/settings.py)

| Setting | Default | Description |
|---------|---------|-------------|
| INPUT_IMAGE_SIZE | (224, 224) | Model input dimensions |
| CLAHE_CLIP_LIMIT | 2.0 | CLAHE enhancement strength |
| DR_CLASSES | 5 classes | DR severity levels |
| BATCH_SIZE | 32 | Training batch size |
| DEVICE | cuda/cpu | GPU or CPU |

---

## 🐛 Troubleshooting

### Model not loading
- Check `MODEL_PATH` points to correct location
- Ensure model weights file exists: `models/dr_detection_model.pth`
- Verify PyTorch installation: `python -c "import torch; print(torch.cuda.is_available())"`

### S3 upload errors
- Verify AWS credentials in `.env`
- Check S3 bucket exists and is accessible
- Ensure IAM permissions: `s3:PutObject`, `s3:GetObject`

### Out of memory errors
- Reduce `BATCH_SIZE` in training
- Use smaller images
- Enable GPU if available

### Slow predictions
- Use GPU acceleration
- Batch multiple predictions
- Cache model in memory (already implemented)

---

## 📈 Next Steps (Phase 2)

After MVP validation:

1. **Patient History Tracking**
   - Longitudinal scan comparison
   - Disease progression analysis
   - Treatment progress tracking

2. **Advanced XAI**
   - SHAP values for feature importance
   - Attention mechanisms
   - Uncertainty quantification

3. **Analytics Dashboard**
   - Real-time monitoring
   - Population statistics
   - Treatment outcome trends

4. **Mobile App**
   - Patient mobile interface
   - Doctor app for review
   - Push notifications

---

## 📝 API Usage Examples

### Example 1: Upload and Predict (Python)
```python
import requests

# Authenticate and get patient ID
patient_data = {
    "name": "Jane Smith",
    "age": 52,
    "email": "jane@example.com"
}
patient_resp = requests.post(
    "http://localhost:8000/patients/",
    json=patient_data
)
patient_id = patient_resp.json()["id"]

# Upload image and get prediction
with open("retinal_image.jpg", "rb") as f:
    files = {"file": f}
    data = {
        "patient_id": patient_id,
        "visit_type": "pre-treatment",
        "notes": "Initial screening"
    }
    pred_resp = requests.post(
        "http://localhost:8000/predict/",
        files=files,
        data=data
    )

prediction = pred_resp.json()
print(f"DR Severity: {prediction['dr_severity']}")
print(f"Confidence: {prediction['confidence_score']:.2%}")
print(f"Heatmap: {prediction['heatmap_url']}")
```

### Example 2: Get Scan History (Python)
```python
history_resp = requests.get(
    f"http://localhost:8000/predict/patient/{patient_id}/history"
)
scans = history_resp.json()

for scan in scans:
    print(f"{scan['scan_timestamp']}: {scan['dr_severity']} ({scan['confidence_score']:.0%})")
```

---

## 📞 Support

For issues or questions:
1. Check troubleshooting section
2. Review API documentation at `/docs`
3. Check logs: `docker-compose logs api`
4. Open an issue on GitHub

---

**Version:** 0.1.0 (MVP)  
**Last Updated:** February 2026
