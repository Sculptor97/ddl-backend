from rest_framework import serializers
from .models import Driver, DailyRod


class DriverSerializer(serializers.ModelSerializer):
    class Meta:
        model = Driver
        fields = ['id', 'name', 'home_tz', 'created_at', 'updated_at']


class DailyRodSerializer(serializers.ModelSerializer):
    driver_name = serializers.CharField(source='driver.name', read_only=True)
    
    class Meta:
        model = DailyRod
        fields = ['id', 'driver', 'driver_name', 'date', 'driving_hours', 
                 'on_duty_hours', 'off_duty_hours', 'entries', 'created_at', 'updated_at']


class TripPlanRequestSerializer(serializers.Serializer):
    current_location = serializers.ListField(
        child=serializers.FloatField(),
        min_length=2,
        max_length=2,
        help_text="[longitude, latitude] of current location"
    )
    pickup = serializers.ListField(
        child=serializers.FloatField(),
        min_length=2,
        max_length=2,
        help_text="[longitude, latitude] of pickup location"
    )
    dropoff = serializers.ListField(
        child=serializers.FloatField(),
        min_length=2,
        max_length=2,
        help_text="[longitude, latitude] of dropoff location"
    )
    driver_id = serializers.IntegerField(required=False, allow_null=True)
    current_cycle_used_hours = serializers.FloatField(required=False, default=0.0)
    start_date = serializers.DateTimeField(required=False, allow_null=True)
    start_time = serializers.TimeField(required=False, allow_null=True)


class TripPlanResponseSerializer(serializers.Serializer):
    route = serializers.DictField()
    daily_logs = serializers.ListField()
    total_distance = serializers.FloatField()
    total_duration = serializers.FloatField()
