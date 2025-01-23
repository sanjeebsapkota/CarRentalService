"""
URL configuration for CarRentalProject project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from base.views import * 
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('',home, name='home'),
    path('about/', about, name='about'),
    path('enquiry/', enquiry_form_submission, name='submit-enquiry'),
    path('contact/', contact, name='contact'),
    path('car_list/', car_list, name='car_list'),
    path('book/<int:car_id>/', book_car, name='book_car'),
    path('invoice/<int:rental_id>/', invoice, name='invoice'),
    path('login/', login, name='login'),
    path('register/', register, name='register'),
    path('logout/', logout_task, name='logout'),
    path('submit-enquiry/', enquiry_form_submission, name='submit-enquiry'),
    
    path('invoices/', invoice_list, name='invoice_list'),
    path('invoices/<int:invoice_id>/', invoice_detail, name='invoice_detail'),

    # path('khalti/initiate/<int:invoice_id>/', initiate_khalti_payment, name='initiate_khalti_payment'),
    # path('khalti/verify/<int:invoice_id>/', verify_khalti_payment, name='verify_khalti_payment'),

    
    
    #######KHALTI VERSION 2###########

    path('khalti/payment/<int:rental_id>/', khalti_payment, name='khalti_payment'),
    path('khalti/verify/', khalti_verify, name='khalti_verify'),
   


    
]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)