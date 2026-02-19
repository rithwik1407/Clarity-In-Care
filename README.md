# Clarity in Care - Explainable AI for Diabetic Retinopathy Detection

A production-ready backend system for detecting and explaining diabetic retinopathy (DR) severity using Explainable AI (XAI) with Grad-CAM heatmap visualization.

## 🎯 Overview

**Clarity in Care** is a FastAPI-based REST API that:
- Detects 5 levels of diabetic retinopathy severity (No DR, Mild, Moderate, Severe, Proliferative)
- Provides explainability through Grad-CAM heatmap visualizations
- Stores patient data and scan history in SQLite/PostgreSQL
- Uploads images to AWS S3 for centralized storage
- Includes model training with ResNet-50 and PyTorch

## 📁 Project Structure

```
Clarity-In-Care/
├── backend/                    # Main backend application
│   ├── app/                   # FastAPI routes & schemas
│   ├── config/                # Configuration management
│   ├── database/              # SQLAlchemy ORM models
│   ├── preprocessing/         # Image preprocessing (CLAHE)
│   ├── models/                # DR detection model wrapper
│   ├── explainability/        # Grad-CAM implementation
│   ├── cloud_storage/         # AWS S3 integration
│   ├── scripts/               # Training scripts
│   ├── data/                  # Dataset folder (train/val)
│   ├── requirements.txt       # Python dependencies
│   ├── Dockerfile            # Docker containerization
│   ├── docker-compose.yml    # Docker Compose setup
│   └── README.md             # Detailed backend docs
└── README.md                  # This file
```

## 🚀 Quick Start

### Installation

1. **Clone the repository**
```bash
git clone https://github.com/yourusername/Clarity-In-Care.git
cd Clarity-In-Care/backend
```

2. **Create virtual environment**
```bash
python -m venv venv
# On Windows:
venv\Scripts\activate
# On Linux/Mac:
source venv/bin/activate
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
pip install torch torchvision torchaudio
```

4. **Configure environment**
```bash
cp .env.example .env
# Edit .env with your AWS S3 credentials
```

5. **Run the API server**
```bash
python main.py
```

Server starts at: `http://localhost:8000`
API docs: `http://localhost:8000/docs`

## 📊 Dataset Setup

### Download Dataset
Choose one of the following:
- [Messidor-2](https://www.adcis.net/en/third-party/messidor2/) (1,748 images)
- [EyePACS](https://www.kaggle.com/datasets/mariaherrerot/eyepacs) (35,000+ images)
- [Aptos 2019](https://www.kaggle.com/competitions/aptos2019-blindness-detection) (4,663 images)

### Organize Dataset

```
backend/data/
├── train/
│   ├── images/        # Training images (.png/.jpg)
│   └── labels.csv     # Format: image_name,label
├── val/
│   ├── images/        # Validation images
│   └── labels.csv
└── DATA_GUIDE.md      # Detailed instructions
```

### Train Model

```bash
python scripts/train_model.py
```

Expected output: `models/dr_detection_model.pth` (~100MB)

## 🔌 API Endpoints

### Health Check
```bash
GET /health
```

### Patient Management
```bash
POST /patients/              # Create patient
GET /patients/{id}          # Get patient details
GET /patients/              # List all patients
```

### Predictions
```bash
POST /predict/              # Upload image & get DR prediction
GET /predict/patient/{id}/history  # Get patient scan history
```

### Response Example
```json
{
  "patient_id": "123e4567",
  "dr_severity": "Moderate",
  "severity_class": 2,
  "confidence": 0.92,
  "heatmap_url": "https://s3.amazonaws.com/...",
  "processed_at": "2026-02-19T15:30:00Z"
}
```

## 🐳 Docker Setup

### Build & Run with Docker

```bash
docker-compose up --build
```

Server runs at: `http://localhost:8000`

### Push to Docker Hub

```bash
docker build -t yourusername/clarity-in-care:latest .
docker push yourusername/clarity-in-care:latest
```

## ☁️ AWS S3 Configuration

### Setup S3 Bucket

1. Create S3 bucket in AWS Console
2. Add IAM user with S3 permissions
3. Get Access Key and Secret Key

### Configure Credentials

Edit `.env`:
```env
AWS_ACCESS_KEY_ID=your_access_key
AWS_SECRET_ACCESS_KEY=your_secret_key
AWS_S3_BUCKET=your-bucket-name
AWS_REGION=us-east-1
```

## 🧠 Model Details

**Architecture**: ResNet-50 (pretrained on ImageNet)
**Input Size**: 224 × 224 pixels
**Classes**: 5 (DR severity levels 0-4)
**Preprocessing**: CLAHE + Normalization
**Explainability**: Grad-CAM attention maps

### DR Severity Levels
- **0**: No DR (Normal)
- **1**: Mild NPDR
- **2**: Moderate NPDR
- **3**: Severe NPDR
- **4**: Proliferative DR

## 📚 Documentation

- [Backend README](backend/README.md) - Complete API reference
- [Setup Guide](backend/SETUP_GUIDE.md) - 5-minute quick start
- [Deployment Guide](backend/DEPLOYMENT.md) - AWS deployment
- [File Structure](backend/FILE_STRUCTURE.md) - Module documentation
- [Checklist](backend/IMPLEMENTATION_CHECKLIST.md) - Development phases

## 🔧 Configuration

Edit `backend/config/settings.py` for:
- Model path and configuration
- Database connection
- S3 bucket settings
- CLAHE enhancement parameters
- API server settings

## 📦 Tech Stack

- **Framework**: FastAPI + Uvicorn
- **ML**: PyTorch + ResNet-50
- **Database**: SQLAlchemy + SQLite (PostgreSQL ready)
- **Image Processing**: OpenCV + PIL + Pillow
- **Enhancement**: CLAHE (Contrast Limited Adaptive Histogram Equalization)
- **Cloud Storage**: AWS S3
- **Containerization**: Docker + Docker Compose
- **XAI**: Grad-CAM (custom implementation)

## 📝 License

MIT License - See LICENSE file

## 📧 Support

For issues and questions:
1. Check [documentation](backend/README.md)
2. Review [troubleshooting](backend/SETUP_GUIDE.md#troubleshooting)
3. Open GitHub issue

## 🎓 Citation

If you use this project in research, please cite:

```bibtex
@software{clarity_in_care_2026,
  title = {Clarity in Care: Explainable AI for Diabetic Retinopathy Detection},
  author = {Your Name},
  year = {2026},
  url = {https://github.com/yourusername/Clarity-In-Care}
}
```

---

**Status**: ✅ Production Ready | **Last Updated**: February 19, 2026
