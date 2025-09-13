from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator


class Driver(models.Model):
    """Driver model for HOS tracking."""
    name = models.CharField(max_length=255)
    home_tz = models.CharField(max_length=50, default='UTC')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['name']


class DailyRod(models.Model):
    """Daily Record of Duty Status (RODS) for HOS compliance."""
    driver = models.ForeignKey(Driver, on_delete=models.CASCADE, related_name='daily_rods')
    date = models.DateField()
    driving_hours = models.DecimalField(max_digits=4, decimal_places=2, default=0.0,
                                       validators=[MinValueValidator(0), MaxValueValidator(24)])
    on_duty_hours = models.DecimalField(max_digits=4, decimal_places=2, default=0.0,
                                       validators=[MinValueValidator(0), MaxValueValidator(24)])
    off_duty_hours = models.DecimalField(max_digits=4, decimal_places=2, default=0.0,
                                        validators=[MinValueValidator(0), MaxValueValidator(24)])
    entries = models.JSONField(default=list, help_text="List of duty status entries for the day")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.driver.name} - {self.date}"

    class Meta:
        unique_together = ['driver', 'date']
        ordering = ['-date', 'driver']
