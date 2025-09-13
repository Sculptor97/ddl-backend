from django.contrib import admin
from .models import Driver, DailyRod


@admin.register(Driver)
class DriverAdmin(admin.ModelAdmin):
    list_display = ['name', 'home_tz', 'created_at']
    list_filter = ['home_tz', 'created_at']
    search_fields = ['name']
    ordering = ['name']


@admin.register(DailyRod)
class DailyRodAdmin(admin.ModelAdmin):
    list_display = ['driver', 'date', 'driving_hours', 'on_duty_hours', 'off_duty_hours']
    list_filter = ['date', 'driver']
    search_fields = ['driver__name']
    ordering = ['-date', 'driver']
    date_hierarchy = 'date'
