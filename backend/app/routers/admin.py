# backend/app/routers/admin.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
from decimal import Decimal
from .. import models
from ..database import get_db
from pydantic import BaseModel
from ..prompts import DEFAULT_MEDICAL_SYSTEM_PROMPT

router = APIRouter(prefix="/admin", tags=["Admin"])

# Response schemas
class PatientResponse(BaseModel):
    id: int
    name: str
    age: int
    gender: str
    contact: str
    patient_triage: str
    ambulance_type: str
    patient_status: str

    class Config:
        from_attributes = True

class AmbulanceResponse(BaseModel):
    ambulance_id: int
    type_of_ambulance: str
    vehicle_number: str
    no_of_staffs: int
    current_location: str
    latitude: float = None
    longitude: float = None
    status: str
    fuel_level: int
    last_updated: str = None

    class Config:
        from_attributes = True

class StaffResponse(BaseModel):
    staff_id: int
    ambulance_id: int = None
    role: str
    staff_status: str

    class Config:
        from_attributes = True

# Request schema for creating ambulance
class AmbulanceCreate(BaseModel):
    type_of_ambulance: str
    vehicle_number: str
    no_of_staffs: int
    current_location: str
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    status: str = "available"
    fuel_level: int


class SystemPromptResponse(BaseModel):
    prompt: str
    updated_at: Optional[str] = None


class SystemPromptUpdate(BaseModel):
    prompt: str


def _get_or_create_system_prompt(db: Session) -> models.SystemPrompt:
    prompt_entry = db.query(models.SystemPrompt).order_by(models.SystemPrompt.id.asc()).first()
    if not prompt_entry:
        prompt_entry = models.SystemPrompt(prompt=DEFAULT_MEDICAL_SYSTEM_PROMPT)
        db.add(prompt_entry)
        db.commit()
        db.refresh(prompt_entry)
    return prompt_entry

@router.get("/patients", response_model=List[PatientResponse])
async def get_all_patients(db: Session = Depends(get_db)):
    """Get all patients from the database."""
    patients = db.query(models.Patient).all()
    return patients

@router.get("/ambulances", response_model=List[AmbulanceResponse])
async def get_all_ambulances(db: Session = Depends(get_db)):
    """Get all ambulances from the database."""
    ambulances = db.query(models.Ambulance).all()
    result = []
    for ambulance in ambulances:
        ambulance_dict = {
            "ambulance_id": ambulance.ambulance_id,
            "type_of_ambulance": ambulance.type_of_ambulance,
            "vehicle_number": ambulance.vehicle_number,
            "no_of_staffs": ambulance.no_of_staffs,
            "current_location": ambulance.current_location,
            "latitude": float(ambulance.latitude) if ambulance.latitude else None,
            "longitude": float(ambulance.longitude) if ambulance.longitude else None,
            "status": ambulance.status,
            "fuel_level": ambulance.fuel_level,
            "last_updated": ambulance.last_updated.isoformat() if ambulance.last_updated else None
        }
        result.append(ambulance_dict)
    return result

@router.get("/staffs", response_model=List[StaffResponse])
async def get_all_staffs(db: Session = Depends(get_db)):
    """Get all staff members from the database."""
    staffs = db.query(models.Staff).all()
    return staffs

@router.post("/ambulances", response_model=AmbulanceResponse)
async def create_ambulance(ambulance: AmbulanceCreate, db: Session = Depends(get_db)):
    """Create a new ambulance in the database."""
    # Check if vehicle number already exists
    existing = db.query(models.Ambulance).filter(models.Ambulance.vehicle_number == ambulance.vehicle_number).first()
    if existing:
        raise HTTPException(status_code=400, detail="Vehicle number already exists")
    
    # Validate enum values
    valid_types = ["Basic", "Advanced", "ICU"]
    if ambulance.type_of_ambulance not in valid_types:
        raise HTTPException(status_code=400, detail=f"Invalid ambulance type. Must be one of: {valid_types}")
    
    valid_statuses = ["available", "dispatch", "out_of_services", "maintenance"]
    if ambulance.status not in valid_statuses:
        raise HTTPException(status_code=400, detail=f"Invalid status. Must be one of: {valid_statuses}")
    
    # Convert latitude/longitude to Decimal if provided
    latitude = Decimal(str(ambulance.latitude)) if ambulance.latitude is not None else None
    longitude = Decimal(str(ambulance.longitude)) if ambulance.longitude is not None else None
    
    # Create new ambulance
    db_ambulance = models.Ambulance(
        type_of_ambulance=ambulance.type_of_ambulance,
        vehicle_number=ambulance.vehicle_number,
        no_of_staffs=ambulance.no_of_staffs,
        current_location=ambulance.current_location,
        latitude=latitude,
        longitude=longitude,
        status=ambulance.status,
        fuel_level=ambulance.fuel_level
    )
    
    db.add(db_ambulance)
    db.commit()
    db.refresh(db_ambulance)
    
    # Return in the same format as GET endpoint
    return {
        "ambulance_id": db_ambulance.ambulance_id,
        "type_of_ambulance": db_ambulance.type_of_ambulance,
        "vehicle_number": db_ambulance.vehicle_number,
        "no_of_staffs": db_ambulance.no_of_staffs,
        "current_location": db_ambulance.current_location,
        "latitude": float(db_ambulance.latitude) if db_ambulance.latitude else None,
        "longitude": float(db_ambulance.longitude) if db_ambulance.longitude else None,
        "status": db_ambulance.status,
        "fuel_level": db_ambulance.fuel_level,
        "last_updated": db_ambulance.last_updated.isoformat() if db_ambulance.last_updated else None
    }


@router.get("/system-prompt", response_model=SystemPromptResponse)
async def get_system_prompt(db: Session = Depends(get_db)):
    prompt_entry = _get_or_create_system_prompt(db)
    return {
        "prompt": prompt_entry.prompt,
        "updated_at": prompt_entry.updated_at.isoformat() if prompt_entry.updated_at else None
    }


@router.put("/system-prompt", response_model=SystemPromptResponse)
async def update_system_prompt(payload: SystemPromptUpdate, db: Session = Depends(get_db)):
    if not payload.prompt or not payload.prompt.strip():
        raise HTTPException(status_code=400, detail="Prompt cannot be empty.")

    prompt_entry = _get_or_create_system_prompt(db)
    prompt_value = payload.prompt.strip()
    setattr(prompt_entry, "prompt", prompt_value)
    db.add(prompt_entry)
    db.commit()
    db.refresh(prompt_entry)

    return {
        "prompt": prompt_entry.prompt,
        "updated_at": prompt_entry.updated_at.isoformat() if prompt_entry.updated_at else None
    }

