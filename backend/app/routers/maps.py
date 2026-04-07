from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Optional, List
import googlemaps
import os
from dotenv import load_dotenv
import math
from decimal import Decimal
from ..database import get_db
from .. import models
from ..schemas import AmbulanceStatusResponse

load_dotenv()

router = APIRouter()

# Initialize Google Maps client
GOOGLE_MAPS_API_KEY = os.getenv("GOOGLE_MAPS_API_KEY") or "AIzaSyBIcmRu-yA62s2Js4RtyJfsFKf9Rm-Xp6w"
if not GOOGLE_MAPS_API_KEY:
    print("⚠️ WARNING: GOOGLE_MAPS_API_KEY environment variable is not set!")
    print("   The system will use fallback route calculations without Google Maps API.")
    gmaps = None
else:
    print(f"✅ Google Maps API key loaded: {GOOGLE_MAPS_API_KEY[:10]}...")
    try:
        gmaps = googlemaps.Client(key=GOOGLE_MAPS_API_KEY)
        print("✅ Google Maps client initialized successfully")
    except Exception as e:
        print(f"❌ Error initializing Google Maps client: {e}")
        gmaps = None

def calculate_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Calculate the distance between two points using the Haversine formula."""
    # Convert decimal degrees to radians
    lat1, lon1, lat2, lon2 = map(math.radians, [lat1, lon1, lat2, lon2])
    
    # Haversine formula
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = math.sin(dlat/2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon/2)**2
    c = 2 * math.asin(math.sqrt(a))
    
    # Radius of earth in kilometers
    r = 6371
    return c * r

def find_best_ambulance_with_routes(patient_lat: float, patient_lon: float, ambulance_type: str, db: Session) -> dict:
    """
    Find the best ambulance based on fuel level >50%, shortest route, and shortest time.
    Returns ambulance details with route information.
    """
    # Step 1: Filter ambulances with fuel level > 50% and available status
    eligible_ambulances = db.query(models.Ambulance).filter(
        models.Ambulance.status == "available",
        models.Ambulance.fuel_level > 50,  # type: ignore
        models.Ambulance.latitude.isnot(None),
        models.Ambulance.longitude.isnot(None)
    ).all()
    
    # Step 2: Further filter by ambulance type if specified
    if ambulance_type and ambulance_type != "Any":
        type_filtered = [amb for amb in eligible_ambulances if amb.type_of_ambulance == ambulance_type]  # pyright: ignore[reportGeneralTypeIssues]
        if type_filtered:  # If we have ambulances of the specified type, use them
            eligible_ambulances = type_filtered
        # If no ambulances of specified type, fall back to all eligible ambulances
    
    if not eligible_ambulances:
        print(f"⚠️ No eligible ambulances found with fuel >50%. Creating fallback ambulance.")
        fallback_ambulance = create_fallback_ambulance(ambulance_type)
        return {
            "ambulance": fallback_ambulance,
            "route": get_route_info(patient_lat, patient_lon, 
                                  float(fallback_ambulance.latitude) if fallback_ambulance.latitude is not None else 0.0,  # type: ignore
                                  float(fallback_ambulance.longitude) if fallback_ambulance.longitude is not None else 0.0),  # type: ignore
            "selection_reason": "fallback - no eligible ambulances"
        }
    
    print(f"🔍 Evaluating {len(eligible_ambulances)} eligible ambulances...")
    
    # Step 3: Calculate routes for all eligible ambulances
    ambulance_route_data = []
    
    for ambulance in eligible_ambulances:
        amb_lat = float(ambulance.latitude) if ambulance.latitude is not None else 0.0  # type: ignore
        amb_lon = float(ambulance.longitude) if ambulance.longitude is not None else 0.0  # type: ignore
        
        try:
            # Get route information from Google Maps API
            route_info = get_route_info(patient_lat, patient_lon, amb_lat, amb_lon)
            
            # Calculate straight-line distance as backup
            straight_distance = calculate_distance(patient_lat, patient_lon, amb_lat, amb_lon)
            
            ambulance_route_data.append({
                "ambulance": ambulance,
                "route": route_info,
                "straight_distance_km": straight_distance,
                "fuel_level": ambulance.fuel_level,
                "ambulance_type": ambulance.type_of_ambulance
            })
            
            print(f"📊 Ambulance {ambulance.vehicle_number}: {route_info.get('duration', 'N/A')}, "
                  f"{route_info.get('distance', 'N/A')}, Fuel: {ambulance.fuel_level}%")
                  
        except Exception as e:
            print(f"❌ Error calculating route for ambulance {ambulance.vehicle_number}: {e}")
            # Add with fallback route info
            straight_distance = calculate_distance(patient_lat, patient_lon, amb_lat, amb_lon)
            ambulance_route_data.append({
                "ambulance": ambulance,
                "route": {
                    "duration": f"{int(straight_distance * 2)} min (estimated)",
                    "duration_seconds": int(straight_distance * 2 * 60),
                    "distance": f"{straight_distance:.1f} km (straight line)",
                    "distance_meters": int(straight_distance * 1000),
                    "api_status": "error"
                },
                "straight_distance_km": straight_distance,
                "fuel_level": ambulance.fuel_level,
                "ambulance_type": ambulance.type_of_ambulance
            })
    
    # Step 4: Select the best ambulance based on criteria
    best_ambulance_data = select_best_ambulance(ambulance_route_data, patient_lat, patient_lon)
    
    return best_ambulance_data

def select_best_ambulance(ambulance_route_data: list, patient_lat: float, patient_lon: float) -> dict:
    """
    Select the best ambulance based on:
    1. Fuel level > 50% (already filtered)
    2. Shortest route distance
    3. Shortest travel time
    """
    if not ambulance_route_data:
        return {}
    
    # Sort by multiple criteria
    # Primary: Shortest travel time (duration_seconds)
    # Secondary: Shortest distance
    # Tertiary: Highest fuel level
    
    def sort_key(data):
        route = data["route"]
        duration_seconds = route.get("duration_seconds", float('inf'))
        distance_meters = route.get("distance_meters", float('inf'))
        fuel_level = data["fuel_level"]
        
        # Return tuple for multi-criteria sorting
        # Lower duration and distance are better, higher fuel is better
        return (duration_seconds, distance_meters, -fuel_level)
    
    # Sort by the criteria
    sorted_ambulances = sorted(ambulance_route_data, key=sort_key)
    best_ambulance_data = sorted_ambulances[0]
    
    # Add selection reasoning
    best_ambulance_data["selection_reason"] = (
        f"Selected based on shortest time ({best_ambulance_data['route'].get('duration', 'N/A')}) "
        f"and distance ({best_ambulance_data['route'].get('distance', 'N/A')}) "
        f"with {best_ambulance_data['fuel_level']}% fuel"
    )
    
    print(f"✅ Best ambulance selected: {best_ambulance_data['ambulance'].vehicle_number}")
    print(f"   Reason: {best_ambulance_data['selection_reason']}")
    
    return best_ambulance_data

def find_nearest_ambulance(patient_lat: float, patient_lon: float, ambulance_type: str, db: Session) -> Optional[models.Ambulance]:
    """
    Legacy function - now uses the new smart selection algorithm.
    Kept for backward compatibility.
    """
    best_ambulance_data = find_best_ambulance_with_routes(patient_lat, patient_lon, ambulance_type, db)
    return best_ambulance_data["ambulance"] if best_ambulance_data else None

def create_fallback_ambulance(ambulance_type: str) -> models.Ambulance:
    """Create a fallback ambulance for demo purposes when no ambulances are in database."""
    from decimal import Decimal
    
    # Chennai coordinates for fallback ambulance
    fallback_lat = Decimal('13.0827')
    fallback_lon = Decimal('80.2707')
    
    fallback_ambulance = models.Ambulance()
    fallback_ambulance.ambulance_id = 999  # Demo ID  # pyright: ignore[reportAttributeAccessIssue]
    fallback_ambulance.type_of_ambulance = ambulance_type  # pyright: ignore[reportAttributeAccessIssue]
    fallback_ambulance.vehicle_number = f"TN-07-DEMO-{ambulance_type.upper()}"  # pyright: ignore[reportAttributeAccessIssue]
    fallback_ambulance.no_of_staffs = 3 if ambulance_type == "Advanced" else 2  # pyright: ignore[reportAttributeAccessIssue]
    fallback_ambulance.current_location = "Chennai Central, Tamil Nadu"  # pyright: ignore[reportAttributeAccessIssue]
    fallback_ambulance.latitude = fallback_lat  # pyright: ignore[reportAttributeAccessIssue]
    fallback_ambulance.longitude = fallback_lon  # pyright: ignore[reportAttributeAccessIssue]
    fallback_ambulance.status = "available"  # pyright: ignore[reportAttributeAccessIssue]
    fallback_ambulance.fuel_level = 85  # pyright: ignore[reportAttributeAccessIssue]
    
    return fallback_ambulance

def get_route_info(origin_lat: float, origin_lon: float, dest_lat: float, dest_lon: float) -> dict:
    """Get route information from Google Maps API."""
    if gmaps is None:
        print("⚠️ Google Maps API not available, using fallback route calculation")
        # Calculate straight-line distance as fallback
        straight_distance = calculate_distance(origin_lat, origin_lon, dest_lat, dest_lon)
        return {
            "duration": f"{int(straight_distance * 2)} min (estimated)",
            "duration_seconds": int(straight_distance * 2 * 60),
            "distance": f"{straight_distance:.1f} km (straight line)",
            "distance_meters": int(straight_distance * 1000),
            "polyline": "",
            "route_steps": [],
            "api_status": "fallback"
        }
    
    try:
        print(f"🗺️ Requesting route from Google Maps API: ({origin_lat}, {origin_lon}) → ({dest_lat}, {dest_lon})")
        
        # Get directions
        directions_result = gmaps.directions(  # pyright: ignore[reportAttributeAccessIssue]
            origin=(origin_lat, origin_lon),
            destination=(dest_lat, dest_lon),
            mode="driving",
            units="metric"
        )
        if not directions_result:
            print("❌ No route found from Google Maps API")
            raise HTTPException(status_code=404, detail="No route found")
        
        print(f"✅ Google Maps API returned route successfully")
        route = directions_result[0]
        leg = route['legs'][0]
        
        # Extract route information
        duration = leg['duration']['text']
        duration_seconds = leg['duration']['value']
        distance = leg['distance']['text']
        distance_meters = leg['distance']['value']
        
        # Get polyline for the route
        overview_polyline = route['overview_polyline']['points']
        
        print(f"📊 Route details: {distance}, {duration}")
        
        return {
            "duration": duration,
            "duration_seconds": duration_seconds,
            "distance": distance,
            "distance_meters": distance_meters,
            "polyline": overview_polyline,
            "route_steps": [
                {
                    "instruction": step['html_instructions'].replace('<b>', '').replace('</b>', ''),
                    "distance": step['distance']['text'],
                    "duration": step['duration']['text']
                }
                for step in leg['steps']
            ],
            "api_status": "success"
        }
    except Exception as e:
        print(f"❌ Google Maps API error: {str(e)}")
        # Fallback to straight-line distance
        straight_distance = calculate_distance(origin_lat, origin_lon, dest_lat, dest_lon)
        return {
            "duration": f"{int(straight_distance * 2)} min (estimated)",
            "duration_seconds": int(straight_distance * 2 * 60),
            "distance": f"{straight_distance:.1f} km (straight line)",
            "distance_meters": int(straight_distance * 1000),
            "polyline": "",
            "route_steps": [],
            "api_status": f"error: {str(e)}"
        }

@router.get("/nearest-ambulance")
async def get_nearest_ambulance_route(
    patient_lat: float,
    patient_lon: float,
    ambulance_type: str,
    db: Session = Depends(get_db)
):
    """Find the best ambulance based on fuel level >50%, shortest route, and shortest time."""
    
    # Use the new smart selection algorithm
    best_ambulance_data = find_best_ambulance_with_routes(patient_lat, patient_lon, ambulance_type, db)
    
    if not best_ambulance_data:
        raise HTTPException(status_code=404, detail=f"No available {ambulance_type} ambulance found")
    
    ambulance = best_ambulance_data["ambulance"]
    route_info = best_ambulance_data["route"]
    selection_reason = best_ambulance_data.get("selection_reason", "Selected based on criteria")
    
    # Safely convert coordinates
    amb_lat = float(ambulance.latitude) if ambulance.latitude is not None else 0.0  # pyright: ignore[reportArgumentType]
    amb_lon = float(ambulance.longitude) if ambulance.longitude is not None else 0.0  # pyright: ignore[reportArgumentType]
    
    # Calculate straight-line distance
    straight_distance = calculate_distance(patient_lat, patient_lon, amb_lat, amb_lon)
    
    return {
        "ambulance": {
            "ambulance_id": ambulance.ambulance_id,
            "vehicle_number": ambulance.vehicle_number,
            "type_of_ambulance": ambulance.type_of_ambulance,
            "current_location": ambulance.current_location,
            "latitude": amb_lat,
            "longitude": amb_lon,
            "no_of_staffs": ambulance.no_of_staffs,
            "fuel_level": ambulance.fuel_level,
            "status": ambulance.status
        },
        "route": route_info,
        "straight_line_distance_km": round(straight_distance, 2),
        "patient_location": {
            "latitude": patient_lat,
            "longitude": patient_lon
        },
        "selection_reason": selection_reason,
        "selection_criteria": {
            "fuel_level_minimum": 50,
            "primary_criteria": "shortest_travel_time",
            "secondary_criteria": "shortest_distance",
            "tertiary_criteria": "highest_fuel_level"
        }
    }

@router.post("/update-ambulance-location/{ambulance_id}")
async def update_ambulance_location(
    ambulance_id: int,
    latitude: float,
    longitude: float,
    current_location: str,
    db: Session = Depends(get_db)
):
    """Update ambulance location with coordinates."""
    
    ambulance = db.query(models.Ambulance).filter(models.Ambulance.ambulance_id == ambulance_id).first()
    
    if not ambulance:
        raise HTTPException(status_code=404, detail="Ambulance not found")
    
    # Update ambulance location - SQLAlchemy will handle the conversion
    if latitude is not None:
        ambulance.latitude = Decimal(str(latitude))  # pyright: ignore[reportAttributeAccessIssue]
    if longitude is not None:
        ambulance.longitude = Decimal(str(longitude))  # pyright: ignore[reportAttributeAccessIssue]
    ambulance.current_location = current_location  # pyright: ignore[reportAttributeAccessIssue]
    
    db.commit()
    db.refresh(ambulance)
    
    return {
        "message": "Ambulance location updated successfully",
        "ambulance_id": ambulance.ambulance_id,
        "vehicle_number": ambulance.vehicle_number,
        "latitude": float(ambulance.latitude) if ambulance.latitude else 0.0,  # pyright: ignore[reportArgumentType, reportGeneralTypeIssues]
        "longitude": float(ambulance.longitude) if ambulance.longitude else 0.0,  # pyright: ignore[reportArgumentType, reportGeneralTypeIssues]
        "current_location": ambulance.current_location
    }

@router.get("/ambulances-with-coordinates")
async def get_ambulances_with_coordinates(db: Session = Depends(get_db)):
    """Get all ambulances that have coordinate information."""
    
    ambulances = db.query(models.Ambulance).filter(
        models.Ambulance.latitude.isnot(None),
        models.Ambulance.longitude.isnot(None)
    ).all()
    
    return [
        {
            "ambulance_id": ambulance.ambulance_id,
            "vehicle_number": ambulance.vehicle_number,
            "type_of_ambulance": ambulance.type_of_ambulance,
            "current_location": ambulance.current_location,
            "latitude": float(ambulance.latitude) if ambulance.latitude else 0.0,  # pyright: ignore[reportArgumentType, reportGeneralTypeIssues]
            "longitude": float(ambulance.longitude) if ambulance.longitude else 0.0,  # pyright: ignore[reportArgumentType, reportGeneralTypeIssues]
            "status": ambulance.status,
            "no_of_staffs": ambulance.no_of_staffs,
            "fuel_level": ambulance.fuel_level
        }
        for ambulance in ambulances
    ]

@router.post("/add-demo-ambulances")
async def add_demo_ambulances(db: Session = Depends(get_db)):
    """Add demo ambulances to the database for testing purposes."""
    from decimal import Decimal
    
    demo_ambulances = [
        {
            "type_of_ambulance": "Basic",
            "vehicle_number": "TN-07-BAS-001",
            "no_of_staffs": 2,
            "current_location": "Chennai Central Station",
            "latitude": Decimal('13.0827'),
            "longitude": Decimal('80.2707'),
            "status": "available",
            "fuel_level": 90
        },
        {
            "type_of_ambulance": "Advanced",
            "vehicle_number": "TN-07-ADV-002",
            "no_of_staffs": 3,
            "current_location": "Anna Nagar, Chennai",
            "latitude": Decimal('13.0850'),
            "longitude": Decimal('80.2200'),
            "status": "available",
            "fuel_level": 85
        },
        {
            "type_of_ambulance": "ICU",
            "vehicle_number": "TN-07-ICU-003",
            "no_of_staffs": 4,
            "current_location": "T. Nagar, Chennai",
            "latitude": Decimal('13.0400'),
            "longitude": Decimal('80.2400'),
            "status": "available",
            "fuel_level": 95
        }
    ]
    
    added_ambulances = []
    for ambulance_data in demo_ambulances:
        # Check if ambulance already exists
        existing = db.query(models.Ambulance).filter(
            models.Ambulance.vehicle_number == ambulance_data["vehicle_number"]
        ).first()
        
        if not existing:
            ambulance = models.Ambulance(**ambulance_data)
            db.add(ambulance)
            added_ambulances.append(ambulance_data)
    
    db.commit()
    
    return {
        "message": f"Added {len(added_ambulances)} demo ambulances",
        "ambulances": added_ambulances
    }

# ==================== DEBUGGING ENDPOINTS ====================

@router.get("/debug/api-status")
async def debug_api_status():
    """Debug endpoint to check Google Maps API status."""
    status = {
        "api_key_present": bool(GOOGLE_MAPS_API_KEY),
        "api_key_preview": GOOGLE_MAPS_API_KEY[:10] + "..." if GOOGLE_MAPS_API_KEY else "None",
        "gmaps_client_initialized": gmaps is not None,
        "environment_variable": os.getenv("GOOGLE_MAPS_API_KEY") is not None,
        "timestamp": __import__('datetime').datetime.now().isoformat()
    }
    
    print(f"🔍 API Status Debug: {status}")
    return status

@router.get("/debug/test-route")
async def debug_test_route():
    """Test Google Maps API with a simple route in Chennai."""
    test_coords = {
        "origin": (13.0827, 80.2707),  # Chennai Central
        "destination": (13.0400, 80.2400)  # T. Nagar
    }
    
    print(f"🧪 Testing Google Maps API with Chennai route...")
    
    try:
        route_info = get_route_info(
            test_coords["origin"][0], test_coords["origin"][1],
            test_coords["destination"][0], test_coords["destination"][1]
        )
        
        result = {
            "test_coordinates": test_coords,
            "route_info": route_info,
            "api_status": route_info.get("api_status", "unknown"),
            "success": route_info.get("api_status") == "success",
            "timestamp": __import__('datetime').datetime.now().isoformat()
        }
        
        print(f"🧪 Test Route Result: {result['success']}")
        return result
        
    except Exception as e:
        error_result = {
            "test_coordinates": test_coords,
            "error": str(e),
            "api_status": "failed",
            "success": False,
            "timestamp": __import__('datetime').datetime.now().isoformat()
        }
        
        print(f"🧪 Test Route Failed: {e}")
        return error_result

@router.get("/debug/system-info")
async def debug_system_info():
    """Get comprehensive system debugging information."""
    import sys
    import platform
    
    # Check if googlemaps module is properly installed
    try:
        import googlemaps
        googlemaps_version = getattr(googlemaps, '__version__', 'unknown')
        googlemaps_available = True
    except ImportError:
        googlemaps_version = "not installed"
        googlemaps_available = False
    
    # Check environment variables
    env_vars = {
        "GOOGLE_MAPS_API_KEY": bool(os.getenv("GOOGLE_MAPS_API_KEY")),
        "DATABASE_URL": bool(os.getenv("DATABASE_URL")),
    }
    
    system_info = {
        "python_version": sys.version,
        "platform": platform.platform(),
        "googlemaps_module": {
            "available": googlemaps_available,
            "version": googlemaps_version,
        },
        "environment_variables": env_vars,
        "api_client_status": {
            "initialized": gmaps is not None,
            "api_key_present": bool(GOOGLE_MAPS_API_KEY)
        },
        "timestamp": __import__('datetime').datetime.now().isoformat()
    }
    
    print(f"🔍 System Info Debug: {system_info}")
    return system_info

@router.get("/debug/ambulance-search")
async def debug_ambulance_search(
    patient_lat: float = 13.0827,
    patient_lon: float = 80.2707,
    ambulance_type: str = "Advanced",
    db: Session = Depends(get_db)
):
    """Debug endpoint to test ambulance search functionality."""
    print(f"🔍 Debugging ambulance search for {ambulance_type} at ({patient_lat}, {patient_lon})")
    
    # Test database query
    try:
        all_ambulances = db.query(models.Ambulance).all()
        available_ambulances = db.query(models.Ambulance).filter(
            models.Ambulance.status == "available"
        ).all()
        ambulances_with_coords = db.query(models.Ambulance).filter(
            models.Ambulance.latitude.isnot(None),
            models.Ambulance.longitude.isnot(None)
        ).all()
        
        print(f"📊 Database Query Results:")
        print(f"   Total ambulances: {len(all_ambulances)}")
        print(f"   Available ambulances: {len(available_ambulances)}")
        print(f"   Ambulances with coordinates: {len(ambulances_with_coords)}")
        
        # Test the actual search function
        nearest_ambulance = find_nearest_ambulance(patient_lat, patient_lon, ambulance_type, db)
        
        result = {
            "search_parameters": {
                "patient_lat": patient_lat,
                "patient_lon": patient_lon,
                "ambulance_type": ambulance_type
            },
            "database_stats": {
                "total_ambulances": len(all_ambulances),
                "available_ambulances": len(available_ambulances),
                "ambulances_with_coordinates": len(ambulances_with_coords)
            },
            "search_result": {
                "found_ambulance": nearest_ambulance is not None,
                "ambulance_id": nearest_ambulance.ambulance_id if nearest_ambulance else None,
                "vehicle_number": nearest_ambulance.vehicle_number if nearest_ambulance else None,
                "type": nearest_ambulance.type_of_ambulance if nearest_ambulance else None,
                "status": nearest_ambulance.status if nearest_ambulance else None
            },
            "timestamp": __import__('datetime').datetime.now().isoformat()
        }
        
        print(f"🔍 Ambulance Search Debug: Found = {result['search_result']['found_ambulance']}")
        return result
        
    except Exception as e:
        error_result = {
            "search_parameters": {
                "patient_lat": patient_lat,
                "patient_lon": patient_lon,
                "ambulance_type": ambulance_type
            },
            "error": str(e),
            "timestamp": __import__('datetime').datetime.now().isoformat()
        }
        
        print(f"🔍 Ambulance Search Debug Failed: {e}")
        return error_result
