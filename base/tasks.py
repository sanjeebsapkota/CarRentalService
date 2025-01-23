from celery import shared_task
from .models import Rental
from datetime import datetime

@shared_task
def update_car_availability():
    """Task to update car availability when rentals expire."""
    expired_rentals = Rental.objects.filter(end_date__lt=datetime.now().date(), car__availability_status=False)
    for rental in expired_rentals:
        rental.car.availability_status = True
        rental.car.save()
