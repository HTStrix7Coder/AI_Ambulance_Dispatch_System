# Smart Ambulance Selection System Implementation

## Overview

This document explains the implementation of the new smart ambulance selection system that replaces the previous AI-generated ambulance approach with a real ambulance selection based on multiple criteria.

## What Changed

### Before (Old System):
- AI generated new ambulance details for each case
- No real ambulance selection from existing database
- Random coordinates and fuel levels
- No route optimization

### After (New System):
- Selects from existing ambulances in the database
- Filters by fuel level > 50%
- Calculates routes for all eligible ambulances using Google Maps API
- Selects based on shortest time, shortest distance, and highest fuel level

## Implementation Details

### 1. Smart Ambulance Selection Algorithm

**File:** `backend/app/routers/maps.py`

**New Function:** `find_best_ambulance_with_routes()`

**Selection Criteria:**
1. **Fuel Level Filter:** Only ambulances with fuel > 50%
2. **Primary Criteria:** Shortest travel time (from Google Maps API)
3. **Secondary Criteria:** Shortest route distance
4. **Tertiary Criteria:** Highest fuel level

**Process:**
```python
# Step 1: Filter eligible ambulances
eligible_ambulances = db.query(models.Ambulance).filter(
    models.Ambulance.status == "available",
    models.Ambulance.fuel_level > 50,
    models.Ambulance.latitude.isnot(None),
    models.Ambulance.longitude.isnot(None)
).all()

# Step 2: Calculate routes for all eligible ambulances
for ambulance in eligible_ambulances:
    route_info = get_route_info(patient_lat, patient_lon, amb_lat, amb_lon)
    # Store route data with ambulance details

# Step 3: Select best ambulance based on criteria
best_ambulance = select_best_ambulance(ambulance_route_data)
```

### 2. Updated Triage System

**File:** `backend/app/routers/triage.py`

**Changes:**
- Removed AI ambulance generation
- Added smart ambulance selection after case creation
- Updates selected ambulance status to 'dispatch'
- Provides detailed logging of selection process

**New Flow:**
1. AI analyzes symptoms and determines ambulance type needed
2. Patient and case are created in database
3. Smart selection finds best available ambulance
4. Selected ambulance status updated to 'dispatch'
5. Route information calculated and stored

### 3. Enhanced Google Maps Integration

**Features:**
- Calculates routes from all eligible ambulances to patient location
- Provides real-time travel time and distance
- Falls back to straight-line distance if API fails
- Includes route steps and polyline data

### 4. New API Endpoints

**New Endpoint:** `/triage/case/{case_id}/ambulance`
- Returns dispatched ambulance details for a specific case
- Includes route information and selection reasoning

**Enhanced Endpoint:** `/maps/nearest-ambulance`
- Now uses smart selection algorithm
- Returns selection criteria and reasoning
- Includes detailed route information

## Database Requirements

### Ambulance Table Structure
```sql
CREATE TABLE ambulances (
    ambulance_id INTEGER PRIMARY KEY,
    type_of_ambulance ENUM('Basic', 'Advanced', 'ICU'),
    vehicle_number VARCHAR(255) UNIQUE,
    no_of_staffs INTEGER,
    current_location VARCHAR(255),
    latitude DECIMAL(9, 6),
    longitude DECIMAL(9, 6),
    status ENUM('available', 'dispatch', 'out_of_services', 'maintenance'),
    fuel_level INTEGER,
    last_updated TIMESTAMP
);
```

### Demo Data Setup

Run the demo ambulance script to add test data:
```bash
cd backend
python add_demo_ambulances.py
```

This adds 6 demo ambulances with:
- Different fuel levels (30%, 60%, 75%, 85%, 90%, 95%)
- Various locations across Chennai
- Different ambulance types (Basic, Advanced, ICU)
- Realistic coordinates

## Testing the System

### 1. Add Demo Ambulances
```bash
cd backend
python add_demo_ambulances.py
```

### 2. Test Smart Selection
```bash
# Test with different patient locations
curl "http://localhost:8000/maps/nearest-ambulance?patient_lat=13.0827&patient_lon=80.2707&ambulance_type=Advanced"
```

### 3. Create Test Case
```bash
curl -X POST "http://localhost:8000/triage/" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Test Patient",
    "age": 35,
    "gender": "Male",
    "contact": "9876543210",
    "symptoms": "Chest pain and difficulty breathing",
    "location": "Chennai Central",
    "latitude": 13.0827,
    "longitude": 80.2707
  }'
```

### 4. Check Dispatched Ambulance
```bash
curl "http://localhost:8000/triage/case/1/ambulance"
```

## Selection Logic Examples

### Example 1: Emergency Case (ICU Required)
- Patient location: Chennai Central (13.0827, 80.2707)
- Available ICU ambulances:
  - TN-07-ICU-003: T. Nagar, 85% fuel, 15 min travel time
  - TN-07-ICU-006: Tambaram, 90% fuel, 25 min travel time
- **Selected:** TN-07-ICU-003 (shorter travel time)

### Example 2: Basic Case (Basic Ambulance)
- Patient location: Anna Nagar (13.0850, 80.2200)
- Available Basic ambulances:
  - TN-07-BAS-001: Chennai Central, 95% fuel, 20 min travel time
  - TN-07-BAS-004: Adyar, 30% fuel (FILTERED OUT - fuel < 50%)
- **Selected:** TN-07-BAS-001 (only eligible option)

## Frontend Integration

The frontend will automatically receive:
- Selected ambulance details
- Route information with travel time
- Selection reasoning
- Real-time coordinates for mapping

## Benefits

1. **Realistic Operations:** Uses actual ambulances instead of generated ones
2. **Optimized Routes:** Google Maps API provides accurate travel times
3. **Fuel Efficiency:** Ensures ambulances have sufficient fuel
4. **Scalable:** Can handle multiple ambulances and complex routing
5. **Transparent:** Provides clear selection reasoning
6. **Reliable:** Fallback mechanisms for API failures

## Monitoring and Debugging

### Debug Endpoints
- `/maps/debug/api-status` - Check Google Maps API status
- `/maps/debug/test-route` - Test route calculation
- `/maps/debug/ambulance-search` - Debug ambulance selection

### Logging
The system provides detailed console logging:
```
🔍 Evaluating 3 eligible ambulances...
📊 Ambulance TN-07-ADV-002: 15 min, 8.2 km, Fuel: 75%
📊 Ambulance TN-07-BAS-001: 12 min, 6.5 km, Fuel: 95%
✅ Best ambulance selected: TN-07-BAS-001
   Reason: Selected based on shortest time (12 min) and distance (6.5 km) with 95% fuel
```

## Future Enhancements

1. **Traffic-Aware Routing:** Real-time traffic conditions
2. **Dynamic Fuel Updates:** Real-time fuel level monitoring
3. **Load Balancing:** Distribute cases across available ambulances
4. **Priority Queuing:** Handle multiple simultaneous cases
5. **Geofencing:** Define service areas for ambulances
6. **Performance Analytics:** Track response times and efficiency

Google Maps API working
Here’s the short version:
Query DB → Find eligible ambulances (fuel > 50%, available, with coords).
For each ambulance → Make 1 Google Maps API call (so 6 ambulances = 6 calls).
# Example results:
Ambulance A: 12 minutes, 5.2 km
Ambulance B: 18 minutes, 7.8 km  
Ambulance C: 15 minutes, 6.1 km
Ambulance D: 25 minutes, 9.3 km
Ambulance E: 14 minutes, 5.9 km
Ambulance F: 22 minutes, 8.7 km
Each call returns travel time & distance.
Compare results → Pick the fastest ambulance.
👉 No batch routing — Google Maps requires separate calls for each ambulance. 🚑

Google Maps API doesn't have a "batch route calculation" endpoint that takes multiple origins to one destination. Each route calculation is a separate API call.