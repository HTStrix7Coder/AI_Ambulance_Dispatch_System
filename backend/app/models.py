from sqlalchemy import TIMESTAMP, Column, Integer, String, Enum, ForeignKey, Text, func, DECIMAL
from sqlalchemy.orm import relationship
from .database import Base

class Patient(Base):
    __tablename__ = "patients"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100))
    age = Column(Integer)
    gender = Column(Enum("M","F"))
    contact = Column(String(20))
    patient_triage = Column(Enum("Red","Orange","Yellow"))
    ambulance_type = Column(Enum("Basic","Advanced","ICU"))
    patient_status = Column(Enum("Pending","Admitted","Travelling"), default="Pending")
    # Relationship to the cases table
    cases = relationship("Case", back_populates="patient")

class Case(Base):
    __tablename__ = "cases"
    id = Column(Integer, primary_key=True, index=True)
    patient_id = Column(Integer, ForeignKey("patients.id"))
    triage_level = Column(Enum("Emergency","Transport","Clinical"))
    symptoms = Column(Text)
    location = Column(String(255))
    latitude = Column(DECIMAL(9, 6), nullable=True)
    longitude = Column(DECIMAL(9, 6), nullable=True)
    status = Column(Enum("Pending","Assigned","Completed"), default="Pending")
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())
    # Relationship back to the patient table
    patient = relationship("Patient", back_populates="cases")

class Ambulance(Base):
    __tablename__ = "ambulances"
    ambulance_id = Column(Integer, primary_key=True, index=True)
    type_of_ambulance = Column(Enum("Basic", "Advanced", "ICU"))
    vehicle_number = Column(String(255), unique=True)
    no_of_staffs = Column(Integer)
    current_location = Column(String(255))  # Address description
    latitude = Column(DECIMAL(9, 6), nullable=True)  # For Google Maps coordinates
    longitude = Column(DECIMAL(9, 6), nullable=True)  # For Google Maps coordinates
    status = Column(Enum("available", "dispatch", "out_of_services", "maintenance"), default="available")
    fuel_level = Column(Integer)
    last_updated = Column(TIMESTAMP(timezone=True), default=func.now())
    # Relationship to the staff and dispatch tables
    staffs = relationship("Staff", back_populates="ambulance")

class Staff(Base):
    __tablename__ = "staffs"
    staff_id = Column(Integer, primary_key=True, index=True)
    ambulance_id = Column(Integer, ForeignKey("ambulances.ambulance_id"))
    role = Column(String(255))
    staff_status = Column(Enum("available", "on_call", "busy", "on_leave"), default="available")
    # Relationship back to the ambulance table
    ambulance = relationship("Ambulance", back_populates="staffs")


class SystemPrompt(Base):
    __tablename__ = "system_prompts"
    id = Column(Integer, primary_key=True, index=True)
    prompt = Column(Text, nullable=False)
    updated_at = Column(TIMESTAMP(timezone=True), server_default=func.now(), onupdate=func.now())

