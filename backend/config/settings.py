import os
from dotenv import load_dotenv

load_dotenv()

# API Configuration
API_TITLE = "Clarity in Care - DR Detection API"
API_VERSION = "0.1.0"
API_DESCRIPTION = "Explainable AI system for Diabetic Retinopathy detection"

# Server Configuration
DEBUG = os.getenv("DEBUG", "False") == "True"
HOST = os.getenv("HOST", "0.0.0.0")
PORT = int(os.getenv("PORT", 8000))

# AWS S3 Configuration
AWS_ACCESS_KEY_ID = os.getenv("AWS_ACCESS_KEY_ID")
AWS_SECRET_ACCESS_KEY = os.getenv("AWS_SECRET_ACCESS_KEY")
AWS_REGION = os.getenv("AWS_REGION", "us-east-1")
S3_BUCKET_NAME = os.getenv("S3_BUCKET_NAME", "clarity-in-care-images")

# Database Configuration
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./clarity_in_care.db")

# Model Configuration
MODEL_PATH = os.getenv("MODEL_PATH", "./models/dr_detection_model.pth")
INPUT_IMAGE_SIZE = (224, 224)
DR_CLASSES = ["No DR", "Mild", "Moderate", "Severe", "Proliferative"]
CONFIDENCE_THRESHOLD = 0.5

# Image Processing Configuration
ALLOWED_IMAGE_FORMATS = {"jpeg", "jpg", "png"}
MAX_IMAGE_SIZE_MB = 10
CLAHE_CLIP_LIMIT = 2.0
CLAHE_TILE_GRID_SIZE = (8, 8)

# Preprocessing
NORMALIZE_MEAN = [0.485, 0.456, 0.406]
NORMALIZE_STD = [0.229, 0.224, 0.225]
