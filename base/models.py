from django.db import models
from django.contrib.auth.models import User


# Create your models here.
class Car(models.Model):
    make = models.CharField(max_length=50)
    model = models.CharField(max_length=50)
    year = models.PositiveIntegerField()
    rental_price_per_day = models.DecimalField(max_digits=10, decimal_places=2)
    availability_status = models.BooleanField(default=True)
    image = models.ImageField(upload_to='car_images/', blank=True, null=True)  # New image field

    def __str__(self):
        return f"{self.make} {self.model} ({self.year})"
    

class Rental(models.Model):
    car = models.ForeignKey(Car, on_delete=models.CASCADE)
    customer = models.ForeignKey(User, on_delete=models.CASCADE)
    start_date = models.DateField()
    end_date = models.DateField()
    total_price = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"Rental: {self.car} by {self.customer}"
    

class Invoice(models.Model):
    booking = models.OneToOneField(Rental, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    total_price = models.DecimalField(max_digits=10, decimal_places=2, default=0.0)  
    

    def __str__(self):
        return f"Invoice {self.id} for Booking {self.booking.id}"
    
class Testimonial(models.Model):
    name = models.CharField(max_length=100)
    designation = models.CharField(max_length=100)
    message = models.TextField()
    image = models.ImageField(upload_to='images/')

    def __str__(self):
        return self.name
    



####### FOR ESEWA #######
class Payment(models.Model):
    rental = models.OneToOneField(Rental, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    transaction_id = models.CharField(max_length=100, blank=True, null=True)
    status = models.CharField(max_length=20, choices=[('Pending', 'Pending'), ('Completed', 'Completed'), ('Failed', 'Failed')], default='Pending')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Payment {self.transaction_id} - {self.status}"
    