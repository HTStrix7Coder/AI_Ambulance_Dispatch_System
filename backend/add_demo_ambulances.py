#!/usr/bin/env python3
"""
Script to add demo ambulances to the database for testing the new ambulance selection system.
"""

import sys
import os
from decimal import Decimal

# Add the backend directory to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.database import SessionLocal
from app import models

def add_demo_ambulances():
    """Add demo ambulances with different fuel levels and locations for testing."""
    
    db = SessionLocal()
    
    try:
        # Demo ambulances with different fuel levels and locations in Chennai
        demo_ambulances = [
            {
                "type_of_ambulance": "Basic",
                "vehicle_number": "TN-07-BAS-001",
                "no_of_staffs": 2,
                "current_location": "Chennai Central Station",
                "latitude": Decimal('13.0827'),
                "longitude": Decimal('80.2707'),
                "status": "available",
                "fuel_level": 95  # High fuel - should be selected for close calls
            },
            {
                "type_of_ambulance": "Advanced",
                "vehicle_number": "TN-07-ADV-002",
                "no_of_staffs": 3,
                "current_location": "Anna Nagar, Chennai",
                "latitude": Decimal('13.0850'),
                "longitude": Decimal('80.2200'),
                "status": "available",
                "fuel_level": 75  # Good fuel level
            },
            {
                "type_of_ambulance": "ICU",
                "vehicle_number": "TN-07-ICU-003",
                "no_of_staffs": 4,
                "current_location": "T. Nagar, Chennai",
                "latitude": Decimal('13.0400'),
                "longitude": Decimal('80.2400'),
                "status": "available",
                "fuel_level": 85  # Good fuel level
            },
            {
                "type_of_ambulance": "Basic",
                "vehicle_number": "TN-07-BAS-004",
                "no_of_staffs": 2,
                "current_location": "Adyar, Chennai",
                "latitude": Decimal('12.9893'),
                "longitude": Decimal('80.2269'),
                "status": "available",
                "fuel_level": 30  # Low fuel - should be filtered out
            },
            {
                "type_of_ambulance": "Advanced",
                "vehicle_number": "TN-07-ADV-005",
                "no_of_staffs": 3,
                "current_location": "Velachery, Chennai",
                "latitude": Decimal('12.9808'),
                "longitude": Decimal('80.2167'),
                "status": "available",
                "fuel_level": 60  # Just above threshold
            },
            {
                "type_of_ambulance": "ICU",
                "vehicle_number": "TN-07-ICU-006",
                "no_of_staffs": 4,
                "current_location": "Tambaram, Chennai",
                "latitude": Decimal('12.9269'),
                "longitude": Decimal('80.1159'),
                "status": "available",
                "fuel_level": 90  # Excellent fuel level
            }
        ]
        
        added_count = 0
        
        for ambulance_data in demo_ambulances:
            # Check if ambulance already exists
            existing = db.query(models.Ambulance).filter(
                models.Ambulance.vehicle_number == ambulance_data["vehicle_number"]
            ).first()
            
            if not existing:
                ambulance = models.Ambulance(**ambulance_data)
                db.add(ambulance)
                added_count += 1
                print(f"✅ Added {ambulance_data['vehicle_number']} - {ambulance_data['type_of_ambulance']} with {ambulance_data['fuel_level']}% fuel")
            else:
                print(f"⚠️ Ambulance {ambulance_data['vehicle_number']} already exists")
        
        db.commit()
        print(f"\n🎉 Successfully added {added_count} new demo ambulances!")
        print("\nDemo ambulances added:")
        print("- 3 with fuel > 50% (eligible for dispatch)")
        print("- 1 with fuel < 50% (will be filtered out)")
        print("- Different types: Basic, Advanced, ICU")
        print("- Various locations across Chennai")
        
    except Exception as e:
        print(f"❌ Error adding demo ambulances: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    print("🚑 Adding demo ambulances to the database...")
    add_demo_ambulances()
