from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


# Patient Schemas
class PatientBase(BaseModel):
    name: str
    age: Optional[int] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    medical_history: Optional[str] = None


class PatientCreate(PatientBase):
    pass


class PatientResponse(PatientBase):
    id: str
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


# Scan/Prediction Schemas
class ScanCreate(BaseModel):
    patient_id: str
    visit_type: str = Field(..., description="pre-treatment, follow-up, or post-treatment")
    notes: Optional[str] = None


class PredictionResponse(BaseModel):
    scan_id: str
    patient_id: str
    dr_severity: str
    confidence_score: float
    heatmap_url: Optional[str] = None
    image_url: Optional[str] = None
    scan_timestamp: datetime
    visit_type: str
    
    class Config:
        from_attributes = True


class ScanHistoryResponse(BaseModel):
    id: str
    patient_id: str
    dr_severity: str
    confidence_score: float
    scan_timestamp: datetime
    visit_type: str
    image_url: Optional[str] = None
    
    class Config:
        from_attributes = True


# Health Check
class HealthResponse(BaseModel):
    status: str
    version: str
    model_loaded: bool
