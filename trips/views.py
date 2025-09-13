from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from django.utils import timezone
from datetime import datetime, timedelta
from .models import Driver, DailyRod
from .serializers import TripPlanRequestSerializer, TripPlanResponseSerializer, DriverSerializer, DailyRodSerializer
from .ors_client import get_route
from .hos import hos_scheduler
import json


@api_view(['POST'])
def plan_trip(request):
    """
    Plan a trip with HOS compliance.
    
    Expected JSON payload:
    {
        "current_location": [longitude, latitude],
        "pickup": [longitude, latitude], 
        "dropoff": [longitude, latitude],
        "driver_id": optional_driver_id,
        "current_cycle_used_hours": optional_hours_already_used,
        "start_date": optional_start_date,
        "start_time": optional_start_time
    }
    
    Note: Coordinates are now geocoded from addresses on the frontend using Mapbox Geocoding API.
    """
    serializer = TripPlanRequestSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    data = serializer.validated_data
    current_location = tuple(data['current_location'])
    pickup = tuple(data['pickup'])
    dropoff = tuple(data['dropoff'])
    driver_id = data.get('driver_id')
    current_cycle_used_hours = data.get('current_cycle_used_hours', 0.0)
    start_date = data.get('start_date')
    start_time = data.get('start_time')
    
    # Validate coordinates are within reasonable bounds
    def validate_coordinates(coord, name):
        lng, lat = coord
        if not (-180 <= lng <= 180 and -90 <= lat <= 90):
            raise ValueError(f"Invalid {name} coordinates: longitude must be -180 to 180, latitude must be -90 to 90")
        return coord
    
    try:
        current_location = validate_coordinates(current_location, "current location")
        pickup = validate_coordinates(pickup, "pickup")
        dropoff = validate_coordinates(dropoff, "dropoff")
    except ValueError as e:
        return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
    
    # Get route information
    route_data = get_route(current_location, pickup, dropoff)
    
    # Debug logging
    print(f"🔍 Route Data Debug:")
    print(f"   Distance: {route_data['distance']} miles")
    print(f"   Duration: {route_data['duration']} hours")
    print(f"   Has Geometry: {'Yes' if route_data.get('geometry') else 'No'}")
    if route_data.get('geometry'):
        coords = route_data['geometry'].get('coordinates', [])
        print(f"   Geometry Points: {len(coords)}")
    
    # Calculate weekly used hours if driver_id provided
    weekly_used = current_cycle_used_hours
    if driver_id:
        try:
            driver = Driver.objects.get(id=driver_id)
            # Get last 8 days of records to calculate rolling hours
            eight_days_ago = timezone.now().date() - timedelta(days=8)
            recent_rods = DailyRod.objects.filter(
                driver=driver,
                date__gte=eight_days_ago
            ).order_by('-date')
            
            # Sum up on_duty_hours from recent records
            weekly_used = sum(float(rod.on_duty_hours) for rod in recent_rods)
            
        except Driver.DoesNotExist:
            return Response(
                {'error': 'Driver not found'}, 
                status=status.HTTP_404_NOT_FOUND
            )
    
    # Build trip segments with enhanced spatial analysis
    segments = [
        {
            'type': 'on_duty',
            'duration': 1.0,  # 1 hour for pickup
            'location': 'Pickup Location',
            'coordinates': pickup
        }
    ]
    
    # For single-day trips: Property-carrying driver, 70hrs/8days, no adverse driving conditions
    # 1 hour for pickup and drop-off, fueling every 1,000 miles
    max_driving_hours = 11.0  # FMCSA 11-hour driving limit
    total_drive_duration = route_data['duration']
    total_distance = route_data['distance']
    
    # For multi-day trips, we'll break down long driving segments into FMCSA-compliant chunks
    # No longer restricting to single-day trips
    
    # Break down long driving segments into FMCSA-compliant chunks
    if total_drive_duration <= max_driving_hours:
        # Single day trip - add driving segments with fueling stops every 1,000 miles
        current_distance = 0
        segment_number = 1
        
        while current_distance < total_distance:
            # Calculate distance for this driving segment
            remaining_distance = total_distance - current_distance
            segment_distance = min(remaining_distance, 1000.0)  # Max 1,000 miles per segment
            
            # Calculate driving time for this segment (proportional to distance)
            segment_drive_time = (segment_distance / total_distance) * total_drive_duration
            
            # Add driving segment
            segments.append({
                'type': 'drive',
                'duration': segment_drive_time,
                'location': f'Route Segment {segment_number} ({segment_distance:.1f} mi)',
                'coordinates': route_data['geometry']['coordinates']
            })
            
            current_distance += segment_distance
            segment_number += 1
            
            # Add fueling stop if not the last segment
            if current_distance < total_distance:
                segments.append({
                    'type': 'on_duty',
                    'duration': 0.5,
                    'location': 'Fueling Stop',
                    'coordinates': None
                })
    else:
        # Multi-day trip - break into 11-hour driving chunks with 10-hour rest breaks
        remaining_duration = total_drive_duration
        segment_number = 1
        
        while remaining_duration > 0:
            # Drive for up to 11 hours
            drive_duration = min(remaining_duration, max_driving_hours)
            segments.append({
                'type': 'drive',
                'duration': drive_duration,
                'location': f'Route Segment {segment_number} ({route_data["distance"] * (drive_duration / total_drive_duration):.1f} mi)',
                'coordinates': route_data['geometry']['coordinates']
            })
            
            remaining_duration -= drive_duration
            segment_number += 1
            
            # Add 10-hour rest break if more driving remains
            if remaining_duration > 0:
                segments.append({
                    'type': 'off_duty',
                    'duration': 10.0,  # 10-hour rest break
                    'location': 'Rest Break (10 hours)',
                    'coordinates': route_data['geometry']['coordinates']
                })
    
    segments.append({
        'type': 'on_duty',
        'duration': 1.0,  # 1 hour for dropoff
        'location': 'Dropoff Location',
        'coordinates': dropoff
    })
    
    # Determine start time
    if start_date and start_time:
        # Combine date and time
        start_datetime = datetime.combine(start_date.date(), start_time)
        if start_datetime.tzinfo is None:
            start_datetime = timezone.make_aware(start_datetime)
    else:
        start_datetime = timezone.now()
    
    # Schedule with HOS compliance
    print(f"🚛 HOS Scheduler Input:")
    print(f"   Start Time: {start_datetime}")
    print(f"   Total Route Duration: {route_data['duration']} hours")
    print(f"   Segments: {len(segments)} segments")
    for i, segment in enumerate(segments):
        print(f"     Segment {i+1}: {segment['type']} - {segment['duration']} hours - {segment['location']}")
    print(f"   Weekly Used: {weekly_used}")
    
    daily_logs = hos_scheduler(start_datetime, segments, weekly_used)
    
    print(f"📋 HOS Scheduler Output:")
    for i, log in enumerate(daily_logs):
        print(f"   Day {i+1}: {log['date']}")
        print(f"     Driving: {log['totals']['driving_hours']} hrs")
        print(f"     On Duty: {log['totals']['on_duty_hours']} hrs")
        print(f"     Off Duty: {log['totals']['off_duty_hours']} hrs")
    
    # If driver_id provided, persist the logs
    if driver_id:
        for log in daily_logs:
            DailyRod.objects.update_or_create(
                driver=driver,
                date=log['date'],
                defaults={
                    'driving_hours': log['totals']['driving_hours'],
                    'on_duty_hours': log['totals']['on_duty_hours'],
                    'off_duty_hours': log['totals']['off_duty_hours'],
                    'entries': log['entries']
                }
            )
    
    # Prepare enhanced response with spatial analysis data
    response_data = {
        'route': {
            'distance': route_data['distance'],
            'duration': route_data['duration'],
            'geometry': route_data['geometry'],
            'statistics': {
                'total_distance': route_data['distance'],
                'total_duration': route_data['duration'],
                'average_speed': route_data['distance'] / route_data['duration'] if route_data['duration'] > 0 else 0,
                'estimated_fuel_cost': route_data['distance'] * 0.15,
                'estimated_tolls': route_data['distance'] * 0.05
            }
        },
        'daily_logs': daily_logs,
        'total_distance': route_data['distance'],
        'total_duration': route_data['duration'],
        'hos_compliance': {
            'is_compliant': True,  # This would be calculated based on the logs
            'violations': [],
            'warnings': []
        },
        'rest_stops': calculate_rest_stops(route_data),
        'route_segments': split_route_segments(route_data)
    }
    
    return Response(response_data, status=status.HTTP_200_OK)


def calculate_rest_stops(route_data):
    """Calculate optimal rest stops along the route."""
    distance = route_data['distance']
    duration = route_data['duration']  # Already in hours
    
    rest_stops = []
    rest_interval_hours = 8  # Rest every 8 hours
    
    # Calculate rest stops at regular intervals
    rest_intervals = int(duration / rest_interval_hours)
    
    for i in range(1, rest_intervals + 1):
        time_from_start = i * rest_interval_hours
        distance_ratio = time_from_start / duration
        distance_from_start = distance_ratio * distance
        
        # Find coordinates at this distance (simplified)
        coordinates = route_data['geometry']['coordinates']
        if coordinates:
            coord_index = min(int(distance_ratio * len(coordinates)), len(coordinates) - 1)
            location = coordinates[coord_index]
            
            rest_stops.append({
                'location': location,
                'distance': distance_from_start,
                'time_from_start': time_from_start,
                'amenities': ['Fuel', 'Food', 'Restrooms', 'Parking']
            })
    
    return rest_stops


def split_route_segments(route_data):
    """Split route into manageable segments for multi-day trips."""
    distance = route_data['distance']
    duration = route_data['duration']  # Already in hours
    max_driving_hours = 11  # FMCSA limit
    
    segments = []
    segments_needed = max(1, int(duration / max_driving_hours))
    segment_distance = distance / segments_needed
    
    coordinates = route_data['geometry']['coordinates']
    
    for i in range(segments_needed):
        start_distance = i * segment_distance
        end_distance = min((i + 1) * segment_distance, distance)
        
        # Find coordinates for segment start and end
        start_coord_index = int((start_distance / distance) * len(coordinates))
        end_coord_index = int((end_distance / distance) * len(coordinates))
        
        segment_coords = coordinates[start_coord_index:end_coord_index + 1]
        
        segments.append({
            'segment_number': i + 1,
            'start_distance': start_distance,
            'end_distance': end_distance,
            'distance': end_distance - start_distance,
            'duration': (end_distance - start_distance) / distance * duration,
            'coordinates': segment_coords
        })
    
    return segments


@api_view(['GET'])
def get_drivers(request):
    """Get all drivers."""
    drivers = Driver.objects.all()
    serializer = DriverSerializer(drivers, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(['GET'])
def get_driver_logs(request, driver_id):
    """Get HOS logs for a specific driver."""
    try:
        driver = Driver.objects.get(id=driver_id)
        logs = DailyRod.objects.filter(driver=driver).order_by('-date')
        serializer = DailyRodSerializer(logs, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    except Driver.DoesNotExist:
        return Response(
            {'error': 'Driver not found'}, 
            status=status.HTTP_404_NOT_FOUND
        )
