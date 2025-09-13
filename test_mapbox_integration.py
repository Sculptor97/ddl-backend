#!/usr/bin/env python3
"""
Test script to verify Mapbox integration in the ORS client.
Run this from the project root directory.
"""

import os
import sys
import django
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from trips.ors_client import get_route

def test_mapbox_integration():
    """Test the Mapbox integration with sample coordinates."""
    
    print("🧪 Testing Mapbox Integration")
    print("=" * 50)
    
    # Test coordinates (New York area)
    current = (-74.0059, 40.7128)  # NYC
    pickup = (-73.9851, 40.7589)   # Central Park
    dropoff = (-74.0445, 40.6892)  # Statue of Liberty
    
    print(f"📍 Test Coordinates:")
    print(f"   Current: {current}")
    print(f"   Pickup: {pickup}")
    print(f"   Dropoff: {dropoff}")
    print()
    
    try:
        # Call the route function
        result = get_route(current, pickup, dropoff)
        
        print("📊 Route Result:")
        print(f"   Distance: {result['distance']} miles")
        print(f"   Duration: {result['duration']} hours")
        print(f"   Has Geometry: {'Yes' if result.get('geometry') else 'No'}")
        
        if result.get('geometry'):
            coords = result['geometry'].get('coordinates', [])
            print(f"   Geometry Points: {len(coords)}")
        
        # Determine which API was used
        if result['distance'] == 300.0 and result['duration'] == 6.0:
            print("\n⚠️  WARNING: Mock data detected - API not working")
        else:
            print("\n✅ SUCCESS: Real route data received!")
            
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    test_mapbox_integration()


