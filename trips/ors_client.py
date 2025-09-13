"""
Route planning client supporting both OpenRouteService and Mapbox.
"""
import requests
import json
from typing import Dict, List, Tuple, Optional
from django.conf import settings


def get_route(current: Tuple[float, float], pickup: Tuple[float, float], 
              dropoff: Tuple[float, float]) -> Dict:
    """
    Get route from OpenRouteService, Mapbox, or return mock data.
    
    Args:
        current: (longitude, latitude) of current location
        pickup: (longitude, latitude) of pickup location
        dropoff: (longitude, latitude) of dropoff location
    
    Returns:
        Dict with distance (miles), duration (hours), and geometry
    """
    print(f"🗺️  Route calculation requested for:")
    print(f"   Current: {current}")
    print(f"   Pickup: {pickup}")
    print(f"   Dropoff: {dropoff}")
    
    # Check API availability
    mapbox_available = hasattr(settings, 'MAPBOX_ACCESS_TOKEN') and settings.MAPBOX_ACCESS_TOKEN
    ors_available = hasattr(settings, 'ORS_API_KEY') and settings.ORS_API_KEY
    
    print(f"🔑 API Status:")
    print(f"   Mapbox: {'✅ Available' if mapbox_available else '❌ Not configured'}")
    print(f"   ORS: {'✅ Available' if ors_available else '❌ Not configured'}")
    
    # Try Mapbox first if API key is available
    if mapbox_available:
        print("🚀 Using Mapbox Directions API...")
        return _get_mapbox_route(current, pickup, dropoff)
    
    # Fallback to OpenRouteService
    if ors_available:
        print("🚀 Using OpenRouteService API...")
        return _get_ors_route(current, pickup, dropoff)
    
    # Final fallback to mock data
    print("⚠️  Using mock data (no API keys configured)")
    return _get_mock_route(current, pickup, dropoff)


def _get_mapbox_route(current: Tuple[float, float], pickup: Tuple[float, float], 
                     dropoff: Tuple[float, float]) -> Dict:
    """Get route from Mapbox Directions API."""
    try:
        # Mapbox Directions API endpoint
        coordinates = f"{current[0]},{current[1]};{pickup[0]},{pickup[1]};{dropoff[0]},{dropoff[1]}"
        url = f"https://api.mapbox.com/directions/v5/mapbox/driving/{coordinates}"
        
        params = {
            'access_token': settings.MAPBOX_ACCESS_TOKEN,
            'geometries': 'geojson',
            'overview': 'full',
            'steps': 'false'
        }
        
        print(f"📡 Mapbox API Request:")
        print(f"   URL: {url}")
        print(f"   Token: {settings.MAPBOX_ACCESS_TOKEN[:10]}...")
        
        response = requests.get(url, params=params, timeout=30)
        print(f"📊 Response Status: {response.status_code}")
        
        response.raise_for_status()
        
        data = response.json()
        print(f"📋 Response Data Keys: {list(data.keys())}")
        
        if 'routes' in data and len(data['routes']) > 0:
            route = data['routes'][0]
            
            # Convert meters to miles and seconds to hours
            distance_miles = route['distance'] * 0.000621371
            duration_hours = route['duration'] / 3600
            
            print(f"✅ Mapbox Route Success:")
            print(f"   Distance: {distance_miles:.2f} miles")
            print(f"   Duration: {duration_hours:.2f} hours")
            print(f"   Geometry points: {len(route['geometry']['coordinates'])}")
            
            return {
                'distance': round(distance_miles, 2),
                'duration': round(duration_hours, 2),
                'geometry': route['geometry']
            }
        else:
            print("❌ No routes found in Mapbox response")
            return _get_mock_route(current, pickup, dropoff)
            
    except Exception as e:
        print(f"❌ Mapbox API error: {e}")
        print(f"   Error type: {type(e).__name__}")
        return _get_mock_route(current, pickup, dropoff)


def _get_ors_route(current: Tuple[float, float], pickup: Tuple[float, float], 
                  dropoff: Tuple[float, float]) -> Dict:
    """Get route from OpenRouteService API."""
    try:
        # OpenRouteService API endpoint
        url = "https://api.openrouteservice.org/v2/directions/driving-car"
        
        headers = {
            'Authorization': settings.ORS_API_KEY,
            'Content-Type': 'application/json'
        }
        
        # Build coordinates: current -> pickup -> dropoff
        coordinates = [list(current), list(pickup), list(dropoff)]
        
        body = {
            "coordinates": coordinates,
            "format": "geojson",
            "units": "mi"
        }
        
        response = requests.post(url, json=body, headers=headers, timeout=30)
        response.raise_for_status()
        
        data = response.json()
        
        if 'features' in data and len(data['features']) > 0:
            feature = data['features'][0]
            properties = feature['properties']
            geometry = feature['geometry']
            
            # Convert meters to miles and seconds to hours
            distance_miles = properties['summary']['distance'] * 0.000621371
            duration_hours = properties['summary']['duration'] / 3600
            
            return {
                'distance': round(distance_miles, 2),
                'duration': round(duration_hours, 2),
                'geometry': geometry
            }
        else:
            return _get_mock_route(current, pickup, dropoff)
            
    except Exception as e:
        print(f"ORS API error: {e}")
        return _get_mock_route(current, pickup, dropoff)


def _get_mock_route(current: Tuple[float, float], pickup: Tuple[float, float], 
                   dropoff: Tuple[float, float]) -> Dict:
    """Return mock route data when ORS API is not available."""
    
    # Create a simple line geometry connecting the three points
    coordinates = [list(current), list(pickup), list(dropoff)]
    
    geometry = {
        "type": "LineString",
        "coordinates": coordinates
    }
    
    # Calculate realistic distance based on coordinates
    import math
    
    def haversine_distance(coord1, coord2):
        """Calculate distance between two coordinates in miles."""
        lat1, lon1 = coord1[1], coord1[0]  # Note: coordinates are [lon, lat]
        lat2, lon2 = coord2[1], coord2[0]
        
        R = 3959  # Earth's radius in miles
        
        dlat = math.radians(lat2 - lat1)
        dlon = math.radians(lon2 - lon1)
        
        a = (math.sin(dlat/2) * math.sin(dlat/2) + 
             math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * 
             math.sin(dlon/2) * math.sin(dlon/2))
        
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
        return R * c
    
    # Calculate total distance
    total_distance = 0
    total_distance += haversine_distance(current, pickup)
    total_distance += haversine_distance(pickup, dropoff)
    
    # Estimate duration (assume 50 mph average speed)
    estimated_duration = total_distance / 50.0
    
    print(f"📊 Mock Route Calculation:")
    print(f"   Calculated Distance: {total_distance:.2f} miles")
    print(f"   Estimated Duration: {estimated_duration:.2f} hours")
    print(f"   ⚠️  Using mock data - configure MAPBOX_ACCESS_TOKEN for real routes")
    
    return {
        'distance': round(total_distance, 2),
        'duration': round(estimated_duration, 2),
        'geometry': geometry
    }
