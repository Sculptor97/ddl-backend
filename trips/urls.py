from django.urls import path
from . import views

urlpatterns = [
    path('plan-trip/', views.plan_trip, name='plan_trip'),
    path('drivers/', views.get_drivers, name='get_drivers'),
    path('drivers/<int:driver_id>/logs/', views.get_driver_logs, name='get_driver_logs'),
]
