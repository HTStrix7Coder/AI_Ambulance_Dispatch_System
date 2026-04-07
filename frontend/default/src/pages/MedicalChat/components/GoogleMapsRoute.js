import React, { useEffect, useRef, useState, useMemo } from 'react';
import { GoogleMap, LoadScript, DirectionsRenderer, Marker, Polyline } from '@react-google-maps/api';

// Define libraries outside component to prevent reloading
const libraries = ['geometry'];

const GoogleMapsRoute = ({ 
  patientLat, 
  patientLon, 
  ambulanceLat, 
  ambulanceLon, 
  routeData, 
  ambulanceInfo,
  className = "w-full h-96 rounded-lg"
}) => {
  console.log('GoogleMapsRoute component rendering with props:', {
    patientLat,
    patientLon,
    ambulanceLat,
    ambulanceLon,
    routeData: routeData ? 'Present' : 'Missing',
    ambulanceInfo: ambulanceInfo ? 'Present' : 'Missing'
  });

  const mapRef = useRef(null);
  const [map, setMap] = useState(null);
  const [directions, setDirections] = useState(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState(null);
  const [userLocation, setUserLocation] = useState(null);
  const [isLocating, setIsLocating] = useState(false);

  // Get API key with fallback
  const apiKey = process.env.REACT_APP_GOOGLE_MAPS_API_KEY || 'AIzaSyBIcmRu-yA62s2Js4RtyJfsFKf9Rm-Xp6w';
  
  const mapContainerStyle = {
    width: '100%',
    height: '350px',
    borderRadius: '12px',
    border: '1px solid #e5e7eb',
    boxShadow: '0 4px 12px rgba(0, 0, 0, 0.08)'
  };

  const center = {
    lat: patientLat || 13.0827,
    lng: patientLon || 80.2707
  };

  const mapOptions = {
    disableDefaultUI: false,
    zoomControl: true,
    streetViewControl: true,
    mapTypeControl: true,
    fullscreenControl: true,
    rotateControl: true,
    scaleControl: true,
    clickableIcons: true,
    gestureHandling: 'greedy',
    styles: [
      // Hide POI labels to reduce clutter
      {
        featureType: 'poi',
        elementType: 'labels',
        stylers: [{ visibility: 'off' }]
      },
      // Style roads for better visibility
      {
        featureType: 'road',
        elementType: 'geometry',
        stylers: [
          { color: '#f5f5f5' },
          { weight: 1 }
        ]
      },
      {
        featureType: 'road',
        elementType: 'labels',
        stylers: [{ visibility: 'simplified' }]
      },
      // Style water
      {
        featureType: 'water',
        elementType: 'geometry',
        stylers: [{ color: '#c9c9c9' }]
      },
      // Style landscape (includes parks and green areas)
      {
        featureType: 'landscape',
        elementType: 'geometry',
        stylers: [{ color: '#e8f5e9' }]
      }
    ]
  };

  // Enhanced marker icons that look more like real Google Maps
  const patientMarkerIcon = {
    path: window.google?.maps?.SymbolPath?.CIRCLE || 'circle',
    fillColor: '#FF1744',
    fillOpacity: 1,
    strokeColor: '#FFFFFF',
    strokeWeight: 3,
    scale: 15
  };

  const ambulanceMarkerIcon = {
    path: window.google?.maps?.SymbolPath?.CIRCLE || 'circle',
    fillColor: '#00C853',
    fillOpacity: 1,
    strokeColor: '#FFFFFF',
    strokeWeight: 3,
    scale: 15
  };

  // Create custom marker HTML for better appearance
  const createCustomMarker = (color, text, isAmbulance = false) => {
    const size = isAmbulance ? 40 : 35;
    const iconHtml = `
      <div style="
        width: ${size}px;
        height: ${size}px;
        background-color: ${color};
        border: 3px solid white;
        border-radius: 50%;
        box-shadow: 0 2px 8px rgba(0,0,0,0.3);
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: ${isAmbulance ? '16px' : '14px'};
        font-weight: bold;
        color: white;
        text-shadow: 0 1px 2px rgba(0,0,0,0.5);
      ">
        ${text}
      </div>
    `;
    return iconHtml;
  };

  useEffect(() => {
    if (routeData && window.google && window.google.maps && window.google.maps.geometry) {
      try {
        // Only process if we have a valid polyline
        if (routeData.polyline && routeData.polyline.trim() && routeData.polyline.startsWith('_p~iF~ps|U')) {
          // This is a valid encoded polyline from Google Maps
          console.log('Processing valid Google Maps polyline');
          const directionsResult = {
            routes: [{
              legs: [{
                start_location: { lat: ambulanceLat, lng: ambulanceLon },
                end_location: { lat: patientLat, lng: patientLon },
                distance: { text: routeData.distance, value: routeData.distance_meters },
                duration: { text: routeData.duration, value: routeData.duration_seconds },
                steps: routeData.route_steps || []
              }],
              overview_polyline: { points: routeData.polyline }
            }]
          };
          setDirections(directionsResult);
        } else {
          console.log('No valid polyline data, will show straight line connection');
          // Don't set directions to null - let the fallback Polyline handle it
          setDirections(null);
        }
      } catch (err) {
        console.error('Error processing route data:', err);
        setError('Error displaying route: ' + err.message);
        setDirections(null);
      }
    } else if (routeData && !window.google) {
      console.warn('Google Maps not loaded yet');
    }
  }, [routeData, patientLat, patientLon, ambulanceLat, ambulanceLon]);

  const onLoad = (map) => {
    setMap(map);
    setIsLoading(false);
  };

  const onUnmount = () => {
    setMap(null);
  };

  // Function to get user's current location
  const getCurrentLocation = () => {
    if (!navigator.geolocation) {
      setError('Geolocation is not supported by this browser.');
      return;
    }

    setIsLocating(true);
    setError(null);

    navigator.geolocation.getCurrentPosition(
      (position) => {
        const userLat = position.coords.latitude;
        const userLng = position.coords.longitude;
        
        setUserLocation({ lat: userLat, lng: userLng });
        
        if (map) {
          // Smoothly pan to user location
          map.panTo({ lat: userLat, lng: userLng });
          map.setZoom(15); // Zoom in to show more detail
        }
        
        setIsLocating(false);
        console.log('User location found:', { lat: userLat, lng: userLng });
      },
      (error) => {
        setIsLocating(false);
        let errorMessage = 'Unable to retrieve your location. ';
        
        switch (error.code) {
          case error.PERMISSION_DENIED:
            errorMessage += 'Please allow location access to use this feature.';
            break;
          case error.POSITION_UNAVAILABLE:
            errorMessage += 'Location information is unavailable.';
            break;
          case error.TIMEOUT:
            errorMessage += 'Location request timed out.';
            break;
          default:
            errorMessage += 'An unknown error occurred.';
            break;
        }
        
        setError(errorMessage);
        console.error('Geolocation error:', error);
      },
      {
        enableHighAccuracy: true,
        timeout: 10000,
        maximumAge: 300000 // 5 minutes
      }
    );
  };

  if (error) {
    return (
      <div className={`${className} flex items-center justify-center bg-red-50 border border-red-200 rounded-lg`}>
        <div className="text-center text-red-600">
          <p className="font-semibold">Map Error</p>
          <p className="text-sm">{error}</p>
        </div>
      </div>
    );
  }

  // Add error handling for API key
  if (!apiKey || apiKey === 'YOUR_API_KEY_HERE') {
    return (
      <div className={`${className} flex items-center justify-center bg-yellow-50 border border-yellow-200 rounded-lg`}>
        <div className="text-center text-yellow-600">
          <p className="font-semibold">⚠️ Google Maps API Key Required</p>
          <p className="text-sm">Please set REACT_APP_GOOGLE_MAPS_API_KEY in your .env file</p>
        </div>
      </div>
    );
  }

  return (
    <div className="relative bg-white rounded-xl p-3 shadow-lg border border-gray-100">
      <div className="mb-3">
        <h2 className="text-lg font-semibold text-gray-800 flex items-center">
          <span className="mr-2">🗺️</span>
          Route Tracking
        </h2>
        <p className="text-gray-600 text-xs mt-1">Ambulance route with live traffic</p>
      </div>
      
      <LoadScript
        googleMapsApiKey={apiKey}
        libraries={libraries}
        onError={(error) => {
          console.error('Google Maps LoadScript error:', error);
          setError('Failed to load Google Maps: ' + error.message);
        }}
        onLoad={() => {
          console.log('Google Maps loaded successfully');
          setIsLoading(false);
        }}
      >
        {isLoading && (
          <div className="absolute inset-0 bg-gray-100 rounded-xl flex items-center justify-center z-10">
            <div className="text-center">
              <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-500 mx-auto mb-2"></div>
              <p className="text-gray-600 text-sm">Loading map...</p>
            </div>
          </div>
        )}
        
        <GoogleMap
          mapContainerStyle={mapContainerStyle}
          center={center}
          zoom={12}
          onLoad={onLoad}
          onUnmount={onUnmount}
          options={mapOptions}
          ref={mapRef}
          onError={(error) => {
            console.error('GoogleMap error:', error);
            setError('Map error: ' + error.message);
          }}
        >
          {/* Patient Marker */}
          {patientLat && patientLon && (
            <Marker
              position={{ lat: patientLat, lng: patientLon }}
              title="Patient Location"
              icon={patientMarkerIcon}
              label={{
                text: 'P',
                color: '#FFFFFF',
                fontSize: '12px',
                fontWeight: 'bold'
              }}
            />
          )}

          {/* Ambulance Marker */}
          {ambulanceLat && ambulanceLon && (
            <Marker
              position={{ lat: ambulanceLat, lng: ambulanceLon }}
              title={`Ambulance: ${ambulanceInfo?.vehicle_number || 'Unknown'}`}
              icon={ambulanceMarkerIcon}
              label={{
                text: 'A',
                color: '#FFFFFF',
                fontSize: '12px',
                fontWeight: 'bold'
              }}
            />
          )}

          {/* User Location Marker */}
          {userLocation && (
            <Marker
              position={userLocation}
              title="Your Location"
              icon={{
                path: window.google?.maps?.SymbolPath?.CIRCLE || 'circle',
                fillColor: '#2196F3',
                fillOpacity: 1,
                strokeColor: '#FFFFFF',
                strokeWeight: 3,
                scale: 12
              }}
              label={{
                text: 'U',
                color: '#FFFFFF',
                fontSize: '12px',
                fontWeight: 'bold'
              }}
            />
          )}

          {/* Directions Renderer with Enhanced Blue Route Line */}
          {directions && (
            <DirectionsRenderer
              directions={directions}
              options={{
                polylineOptions: {
                  strokeColor: '#4285F4',
                  strokeWeight: 6,
                  strokeOpacity: 1.0,
                  strokePattern: null,
                  geodesic: true
                },
                suppressMarkers: true,
                suppressInfoWindows: false,
                preserveViewport: false,
                hideRouteList: false,
                panel: null,
                draggable: false,
                markerOptions: {
                  clickable: true,
                  cursor: 'pointer'
                }
              }}
            />
          )}

          {/* Fallback: Draw straight line if no route data */}
          {!directions && patientLat && patientLon && ambulanceLat && ambulanceLon && window.google && (
            <Polyline
              path={[
                { lat: patientLat, lng: patientLon },
                { lat: ambulanceLat, lng: ambulanceLon }
              ]}
              options={{
                strokeColor: '#4285F4',
                strokeWeight: 4,
                strokeOpacity: 0.8,
                geodesic: true
              }}
            />
          )}
        </GoogleMap>
      </LoadScript>
      
      
      {/* Map Control Buttons */}
      <div className="absolute bottom-3 left-3 flex flex-col space-y-2">
        {/* Traffic Button */}
        <button
          onClick={() => {
            if (map) {
              // Toggle traffic layer
              const trafficLayer = new window.google.maps.TrafficLayer();
              trafficLayer.setMap(map);
            }
          }}
          className="bg-white hover:bg-gray-50 text-gray-700 hover:text-gray-900 px-4 py-2 rounded-lg shadow-lg border border-gray-200 flex items-center space-x-2 transition-all duration-200 font-medium text-sm"
        >
          <div className="flex items-center space-x-1">
            <div className="w-2 h-2 bg-red-500 rounded-full"></div>
            <div className="w-2 h-2 bg-yellow-500 rounded-full"></div>
            <div className="w-2 h-2 bg-green-500 rounded-full"></div>
          </div>
          <span>Traffic</span>
        </button>

        {/* Location Pin Button */}
        <button
          onClick={getCurrentLocation}
          disabled={isLocating}
          className="bg-white hover:bg-gray-50 text-gray-700 hover:text-gray-900 px-4 py-2 rounded-lg shadow-lg border border-gray-200 flex items-center space-x-2 transition-all duration-200 font-medium text-sm disabled:opacity-50 disabled:cursor-not-allowed"
          title="Find my location"
        >
          {isLocating ? (
            <>
              <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-blue-500"></div>
              <span>Finding...</span>
            </>
          ) : (
            <span>My Location</span>
          )}
        </button>
      </div>


    </div>
  );
};

export default GoogleMapsRoute;
