from sqlalchemy.orm import Session, joinedload
from . import models

# This new function saves the patient, the case, AND the ambulance
def create_case_and_ambulance(db: Session, case_data: dict):
    """
    Creates a Patient, a Case, and a corresponding Ambulance record
    in a single database transaction.
    """
    # 1. Create Patient and Case objects
    db_patient = models.Patient(
        name=case_data.get('name'),
        age=case_data.get('age'),
        gender=case_data.get('gender'),
        contact=case_data.get('contact'),
        patient_triage=case_data.get('patient_triage'),
        ambulance_type=case_data.get('ambulance_type'),
        patient_status=case_data.get('patient_status')
    )

    # Convert float to Decimal for database storage
    from decimal import Decimal
    latitude = case_data.get('latitude')
    longitude = case_data.get('longitude')
    
    if latitude is not None:
        latitude = Decimal(str(latitude))
    if longitude is not None:
        longitude = Decimal(str(longitude))
    
    db_case = models.Case(
        patient=db_patient,  # Link to the patient object directly
        triage_level=case_data.get('triage_level'),
        symptoms=case_data.get('symptoms'),
        location=case_data.get('location'),
        latitude=latitude,
        longitude=longitude,
    )

    # 2. Create the new Ambulance record if details are present
    ambulance_data = case_data.get("ambulance_details", {})
    db_ambulance = None # Initialize to None
    if ambulance_data:
        # Convert ambulance coordinates to Decimal if provided
        ambulance_lat = ambulance_data.get('latitude')
        ambulance_lon = ambulance_data.get('longitude')
        
        if ambulance_lat is not None:
            ambulance_lat = Decimal(str(ambulance_lat))
        if ambulance_lon is not None:
            ambulance_lon = Decimal(str(ambulance_lon))
        
        db_ambulance = models.Ambulance(
            type_of_ambulance=case_data.get("ambulance_type"),
            vehicle_number=ambulance_data.get("vehicle_number"),
            no_of_staffs=ambulance_data.get("no_of_staffs"),
            current_location=ambulance_data.get("current_location"),
            latitude=ambulance_lat,
            longitude=ambulance_lon,
            fuel_level=ambulance_data.get("fuel_level"),
            status='dispatch'  # Mark as dispatched for this case
        )
        db.add(db_ambulance)

    # 3. Add all objects to the session
    db.add(db_patient)
    db.add(db_case)
    
    # 4. Commit all changes at once
    db.commit()

    # 5. Refresh all objects to get their new state from the DB (like IDs)
    db.refresh(db_patient)
    db.refresh(db_case)
    if db_ambulance:
        db.refresh(db_ambulance)

    return db_case


def get_recent_cases(db: Session):
    """
    Gets the most recent cases and uses a JOIN to efficiently fetch
    the related patient data in a single query.
    """
    return (
        db.query(models.Case)
        .options(joinedload(models.Case.patient)) # This performs an efficient JOIN
        .order_by(models.Case.id.desc())
        .all()
    )


def get_cases(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Case).offset(skip).limit(limit).all()

