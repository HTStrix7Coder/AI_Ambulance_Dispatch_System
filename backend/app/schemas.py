from pydantic import BaseModel
from typing import Optional, List

# Schema for the data received from the conversational frontend
class CaseInput(BaseModel):
    name: str
    age: int
    gender: str
    contact: str
    symptoms: str
    location: str
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    # This field will be added by medicalchat.py before calling the triage endpoint
    chat_history: Optional[List[dict]] = None

# Schema for the data returned to the frontend after creating a case
class CaseResponse(BaseModel):
    id: int
    triage_level: str
    symptoms: str
    status: str
    patient_name: str

    class Config:
        from_attributes = True

# Schema for an individual chat message
class ChatRequest(BaseModel):
    message: str
    session_id: str
    latitude: Optional[float] = None
    longitude: Optional[float] = None

# Schema for the /triage/recent endpoint
class RecentCaseResponse(BaseModel):
    id: int
    patient_name: str
    age: int
    gender: str
    contact: Optional[str] = None
    symptoms: str
    status: str
    triage_level: Optional[str] = None
    ambulance_type: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    location: Optional[str] = None

    class Config:
        from_attributes = True

# --- NEW SCHEMA FOR THE AMBULANCE STATUS ENDPOINT ---
class AmbulanceStatusResponse(BaseModel):
    ambulance_id: int
    vehicle_number: str
    type_of_ambulance: str
    status: str
    current_location: str
    no_of_staffs: int
    fuel_level: int

    class Config:
        from_attributes = True

# --- NEW SCHEMA FOR THE CHAT HISTORY ENDPOINT ---
class ChatMessage(BaseModel):
    sender: str
    message: str

    class Config:
        from_attributes = True
