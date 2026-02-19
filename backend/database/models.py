from sqlalchemy import create_engine, Column, String, Float, DateTime, Text, Integer
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime
from config.settings import DATABASE_URL

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


class Patient(Base):
    """Patient model."""
    __tablename__ = "patients"
    
    id = Column(String, primary_key=True, index=True)
    name = Column(String, index=True)
    age = Column(Integer, nullable=True)
    email = Column(String, index=True, nullable=True)
    phone = Column(String, nullable=True)
    medical_history = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class Scan(Base):
    """Scan/Prediction model for storing DR detection results."""
    __tablename__ = "scans"
    
    id = Column(String, primary_key=True, index=True)
    patient_id = Column(String, index=True)
    image_s3_key = Column(String)  # S3 path to original image
    heatmap_s3_key = Column(String, nullable=True)  # S3 path to heatmap
    visit_type = Column(String)  # pre-treatment, follow-up, post-treatment
    dr_severity = Column(String)  # DR classification result
    confidence_score = Column(Float)  # Confidence of prediction
    scan_timestamp = Column(DateTime, default=datetime.utcnow)
    created_at = Column(DateTime, default=datetime.utcnow)
    notes = Column(Text, nullable=True)


def get_db():
    """Dependency to get database session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    """Initialize database tables."""
    Base.metadata.create_all(bind=engine)
