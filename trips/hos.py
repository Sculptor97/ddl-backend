"""
Hours of Service (HOS) scheduler implementing FMCSA regulations.
"""
from datetime import datetime, timedelta
from typing import List, Dict, Any
from dateutil import tz


def hos_scheduler(start_time: datetime, segments: List[Dict], weekly_used: float = 0.0) -> List[Dict]:
    """
    Schedule trip segments according to FMCSA HOS regulations for multi-day trips.
    Creates continuous 24-hour timelines starting from midnight for each day.
    
    Args:
        start_time: When the trip starts
        segments: List of segments with 'type', 'duration', 'location'
        weekly_used: Hours already used in current 8-day cycle
    
    Returns:
        List of daily logs with entries and totals for each day
    """
    # Start the day at midnight of the start date
    day_start = start_time.replace(hour=0, minute=0, second=0, microsecond=0)
    current_time = start_time
    daily_logs = []
    daily_entries = []
    
    # HOS tracking variables
    daily_driving = 0.0
    daily_on_duty = 0.0
    daily_off_duty = 0.0
    weekly_hours = weekly_used
    consecutive_driving = 0.0
    
    # Add initial off-duty period from midnight to start time
    if start_time > day_start:
        off_duty_duration = (start_time - day_start).total_seconds() / 3600
        daily_entries.append({
            'start_time': '00:00',
            'end_time': start_time.strftime('%H:%M'),
            'status': 'off_duty',
            'location': 'Off Duty',
            'duration': off_duty_duration
        })
        daily_off_duty += off_duty_duration
    
    # Check 70-hour rule before starting trip
    if weekly_hours > 70.0:
        # Need 34-hour restart before starting
        restart_duration = 34.0
        daily_entries.append({
            'start_time': current_time.strftime('%H:%M'),
            'end_time': (current_time + timedelta(hours=restart_duration)).strftime('%H:%M'),
            'status': 'off_duty',
            'location': '34-hour Restart',
            'duration': restart_duration
        })
        daily_off_duty += restart_duration
        current_time += timedelta(hours=restart_duration)
        weekly_hours = 0.0  # Reset weekly hours

    # Process each segment
    for segment in segments:
        segment_type = segment['type']
        duration = segment['duration']
        location = segment.get('location', '')
        
        # Check if we need to start a new day (cross midnight)
        if current_time.date() != day_start.date():
            print(f"🌅 Crossing midnight: {day_start.date()} -> {current_time.date()}")
            print(f"   Day totals before save: Driving={daily_driving:.1f}, On Duty={daily_on_duty:.1f}, Off Duty={daily_off_duty:.1f}")
            
            # Save current day
            daily_logs.append({
                'date': day_start.date().isoformat(),
                'entries': daily_entries.copy(),
                'totals': {
                    'driving_hours': daily_driving,
                    'on_duty_hours': daily_on_duty,
                    'off_duty_hours': daily_off_duty
                }
            })
            
            # Start new day
            day_start = current_time.replace(hour=0, minute=0, second=0, microsecond=0)
            daily_entries = []
            daily_driving = 0.0
            daily_on_duty = 0.0
            daily_off_duty = 0.0
            
            # Add off-duty period from midnight to current time
            if current_time > day_start:
                off_duty_duration = (current_time - day_start).total_seconds() / 3600
                daily_entries.append({
                    'start_time': '00:00',
                    'end_time': current_time.strftime('%H:%M'),
                    'status': 'off_duty',
                    'location': 'Off Duty',
                    'duration': off_duty_duration
                })
                daily_off_duty += off_duty_duration
                print(f"   Added off-duty period: {off_duty_duration:.1f} hours")
        
        # Process segment based on type
        if segment_type == 'drive':
            print(f"🚛 Processing drive segment: {duration} hours, current daily driving: {daily_driving}")
            
            # Check 11-hour driving limit
            if daily_driving + duration > 11.0:
                # Need to insert 10-hour break
                break_duration = 10.0
                daily_entries.append({
                    'start_time': current_time.strftime('%H:%M'),
                    'end_time': (current_time + timedelta(hours=break_duration)).strftime('%H:%M'),
                    'status': 'off_duty',
                    'location': 'Rest Break (10 hours)',
                    'duration': break_duration
                })
                daily_off_duty += break_duration
                current_time += timedelta(hours=break_duration)
                daily_driving = 0.0  # Reset after 10-hour break
                consecutive_driving = 0.0
            
            # Check 8-hour consecutive driving limit (need 30-min break)
            if consecutive_driving + duration > 8.0:
                # Insert 30-minute break
                break_duration = 0.5
                daily_entries.append({
                    'start_time': current_time.strftime('%H:%M'),
                    'end_time': (current_time + timedelta(hours=break_duration)).strftime('%H:%M'),
                    'status': 'off_duty',
                    'location': '30-min Break',
                    'duration': break_duration
                })
                daily_off_duty += break_duration
                current_time += timedelta(hours=break_duration)
                consecutive_driving = 0.0
            
            # Handle segment that might span across midnight
            remaining_duration = duration
            while remaining_duration > 0:
                # Check if we need to start a new day (cross midnight) - handle within segment processing
                if current_time.date() != day_start.date():
                    print(f"🌅 Crossing midnight during segment: {day_start.date()} -> {current_time.date()}")
                    print(f"   Day totals before save: Driving={daily_driving:.1f}, On Duty={daily_on_duty:.1f}, Off Duty={daily_off_duty:.1f}")
                    
                    # Save current day
                    daily_logs.append({
                        'date': day_start.date().isoformat(),
                        'entries': daily_entries.copy(),
                        'totals': {
                            'driving_hours': daily_driving,
                            'on_duty_hours': daily_on_duty,
                            'off_duty_hours': daily_off_duty
                        }
                    })
                    
                    # Start new day
                    day_start = current_time.replace(hour=0, minute=0, second=0, microsecond=0)
                    daily_entries = []
                    daily_driving = 0.0
                    daily_on_duty = 0.0
                    daily_off_duty = 0.0
                    
                    # Add off-duty period from midnight to current time
                    if current_time > day_start:
                        off_duty_duration = (current_time - day_start).total_seconds() / 3600
                        daily_entries.append({
                            'start_time': '00:00',
                            'end_time': current_time.strftime('%H:%M'),
                            'status': 'off_duty',
                            'location': 'Off Duty',
                            'duration': off_duty_duration
                        })
                        daily_off_duty += off_duty_duration
                        print(f"   Added off-duty period: {off_duty_duration:.1f} hours")
                
                # Calculate how much time is left in current day
                day_end = day_start + timedelta(days=1)
                time_left_in_day = (day_end - current_time).total_seconds() / 3600
                
                # Use the smaller of remaining duration or time left in day
                segment_duration = min(remaining_duration, time_left_in_day)
                
                # Add driving segment
                daily_entries.append({
                    'start_time': current_time.strftime('%H:%M'),
                    'end_time': (current_time + timedelta(hours=segment_duration)).strftime('%H:%M'),
                    'status': 'driving',
                    'location': location,
                    'duration': segment_duration
                })
                daily_driving += segment_duration
                daily_on_duty += segment_duration  # Driving time counts as on-duty time
                consecutive_driving += segment_duration
                current_time += timedelta(hours=segment_duration)
                remaining_duration -= segment_duration
                
                # If we've used all time in the day, the midnight crossing logic will handle the next day
                if remaining_duration > 0:
                    print(f"   Segment spans midnight, {remaining_duration:.1f} hours remaining")
            
        elif segment_type == 'on_duty':
            # Check 14-hour on-duty window
            if daily_on_duty + duration > 14.0:
                # Need to insert 10-hour break
                break_duration = 10.0
                daily_entries.append({
                    'start_time': current_time.strftime('%H:%M'),
                    'end_time': (current_time + timedelta(hours=break_duration)).strftime('%H:%M'),
                    'status': 'off_duty',
                    'location': '14-hour Reset',
                    'duration': break_duration
                })
                daily_off_duty += break_duration
                current_time += timedelta(hours=break_duration)
                daily_on_duty = 0.0  # Reset after 10-hour break
            
            # Handle segment that might span across midnight
            remaining_duration = duration
            while remaining_duration > 0:
                # Check if we need to start a new day (cross midnight) - handle within segment processing
                if current_time.date() != day_start.date():
                    print(f"🌅 Crossing midnight during on-duty segment: {day_start.date()} -> {current_time.date()}")
                    print(f"   Day totals before save: Driving={daily_driving:.1f}, On Duty={daily_on_duty:.1f}, Off Duty={daily_off_duty:.1f}")
                    
                    # Save current day
                    daily_logs.append({
                        'date': day_start.date().isoformat(),
                        'entries': daily_entries.copy(),
                        'totals': {
                            'driving_hours': daily_driving,
                            'on_duty_hours': daily_on_duty,
                            'off_duty_hours': daily_off_duty
                        }
                    })
                    
                    # Start new day
                    day_start = current_time.replace(hour=0, minute=0, second=0, microsecond=0)
                    daily_entries = []
                    daily_driving = 0.0
                    daily_on_duty = 0.0
                    daily_off_duty = 0.0
                    
                    # Add off-duty period from midnight to current time
                    if current_time > day_start:
                        off_duty_duration = (current_time - day_start).total_seconds() / 3600
                        daily_entries.append({
                            'start_time': '00:00',
                            'end_time': current_time.strftime('%H:%M'),
                            'status': 'off_duty',
                            'location': 'Off Duty',
                            'duration': off_duty_duration
                        })
                        daily_off_duty += off_duty_duration
                        print(f"   Added off-duty period: {off_duty_duration:.1f} hours")
                
                # Calculate how much time is left in current day
                day_end = day_start + timedelta(days=1)
                time_left_in_day = (day_end - current_time).total_seconds() / 3600
                
                # Use the smaller of remaining duration or time left in day
                segment_duration = min(remaining_duration, time_left_in_day)
                
                # Add on-duty segment
                daily_entries.append({
                    'start_time': current_time.strftime('%H:%M'),
                    'end_time': (current_time + timedelta(hours=segment_duration)).strftime('%H:%M'),
                    'status': 'on_duty',
                    'location': location,
                    'duration': segment_duration
                })
                daily_on_duty += segment_duration
                current_time += timedelta(hours=segment_duration)
                remaining_duration -= segment_duration
                
                # If we've used all time in the day, the midnight crossing logic will handle the next day
                if remaining_duration > 0:
                    print(f"   On-duty segment spans midnight, {remaining_duration:.1f} hours remaining")
            
        elif segment_type == 'off_duty':
            # Handle segment that might span across midnight
            remaining_duration = duration
            while remaining_duration > 0:
                # Check if we need to start a new day (cross midnight) - handle within segment processing
                if current_time.date() != day_start.date():
                    print(f"🌅 Crossing midnight during off-duty segment: {day_start.date()} -> {current_time.date()}")
                    print(f"   Day totals before save: Driving={daily_driving:.1f}, On Duty={daily_on_duty:.1f}, Off Duty={daily_off_duty:.1f}")
                    
                    # Save current day
                    daily_logs.append({
                        'date': day_start.date().isoformat(),
                        'entries': daily_entries.copy(),
                        'totals': {
                            'driving_hours': daily_driving,
                            'on_duty_hours': daily_on_duty,
                            'off_duty_hours': daily_off_duty
                        }
                    })
                    
                    # Start new day
                    day_start = current_time.replace(hour=0, minute=0, second=0, microsecond=0)
                    daily_entries = []
                    daily_driving = 0.0
                    daily_on_duty = 0.0
                    daily_off_duty = 0.0
                    
                    # Add off-duty period from midnight to current time
                    if current_time > day_start:
                        off_duty_duration = (current_time - day_start).total_seconds() / 3600
                        daily_entries.append({
                            'start_time': '00:00',
                            'end_time': current_time.strftime('%H:%M'),
                            'status': 'off_duty',
                            'location': 'Off Duty',
                            'duration': off_duty_duration
                        })
                        daily_off_duty += off_duty_duration
                        print(f"   Added off-duty period: {off_duty_duration:.1f} hours")
                
                # Calculate how much time is left in current day
                day_end = day_start + timedelta(days=1)
                time_left_in_day = (day_end - current_time).total_seconds() / 3600
                
                # Use the smaller of remaining duration or time left in day
                segment_duration = min(remaining_duration, time_left_in_day)
                
                # Add off-duty segment
                daily_entries.append({
                    'start_time': current_time.strftime('%H:%M'),
                    'end_time': (current_time + timedelta(hours=segment_duration)).strftime('%H:%M'),
                    'status': 'off_duty',
                    'location': location,
                    'duration': segment_duration
                })
                daily_off_duty += segment_duration
                current_time += timedelta(hours=segment_duration)
                remaining_duration -= segment_duration
                consecutive_driving = 0.0  # Reset consecutive driving
                
                # If we've used all time in the day, the midnight crossing logic will handle the next day
                if remaining_duration > 0:
                    print(f"   Off-duty segment spans midnight, {remaining_duration:.1f} hours remaining")
    
    # Add final off-duty period to complete the 24-hour day
    day_end = day_start + timedelta(days=1)
    if current_time < day_end:
        final_off_duty_duration = (day_end - current_time).total_seconds() / 3600
        daily_entries.append({
            'start_time': current_time.strftime('%H:%M'),
            'end_time': '24:00',  # Use 24:00 to represent end of day
            'status': 'off_duty',
            'location': 'Off Duty',
            'duration': final_off_duty_duration
        })
        daily_off_duty += final_off_duty_duration
    
    # Update weekly hours for next day
    weekly_hours += daily_on_duty
    
    # Save final day
    daily_logs.append({
        'date': day_start.date().isoformat(),
        'entries': daily_entries,
        'totals': {
            'driving_hours': daily_driving,
            'on_duty_hours': daily_on_duty,
            'off_duty_hours': daily_off_duty
        }
    })
    
    # Debug: Print calculation summary
    print(f"📊 Multi-Day HOS Calculation Summary:")
    print(f"   Total Days: {len(daily_logs)}")
    print(f"   Final Day Driving: {daily_driving:.1f} hours")
    print(f"   Final Day On Duty: {daily_on_duty:.1f} hours")
    print(f"   Final Day Off Duty: {daily_off_duty:.1f} hours")
    print(f"   Weekly Hours Used: {weekly_hours:.1f} hours")
    print(f"   Final Day Entries: {len(daily_entries)}")
    
    # Calculate totals across all days
    total_driving = sum(log['totals']['driving_hours'] for log in daily_logs)
    total_on_duty = sum(log['totals']['on_duty_hours'] for log in daily_logs)
    total_off_duty = sum(log['totals']['off_duty_hours'] for log in daily_logs)
    
    print(f"📊 Trip Totals (All Days):")
    print(f"   Total Driving: {total_driving:.1f} hours")
    print(f"   Total On Duty: {total_on_duty:.1f} hours")
    print(f"   Total Off Duty: {total_off_duty:.1f} hours")
    
    return daily_logs
