from django.contrib import admin

# Register your models here.
from .models import Car,Rental,Invoice,Testimonial

admin.site.register(Car)
admin.site.register(Rental)
admin.site.register(Invoice)
admin.site.register(Testimonial)
