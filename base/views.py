from django.shortcuts import render,HttpResponse
from .models import Car,Rental,Invoice,Testimonial
from django.utils import timezone
from django.shortcuts import render, get_object_or_404, redirect
# from django.contrib.auth.decorators import login_required
from django.core.mail import send_mail

# Create your views here.
def home(request):
    return render(request,'home.html')


#displays a single invoice in detail.
def invoice_detail(request, invoice_id):
    
    # Get the invoice object based on the invoice_id from the URL
    invoice = get_object_or_404(Invoice, id=invoice_id)

    # Pass the invoice object to the template
    return render(request, 'invoice_detail.html', {'invoice': invoice},)

def cars(request):
    return render(request, 'cars.html')



def about(request):
    testimonials = Testimonial.objects.all()
    return render(request, 'about.html', {'testimonials': testimonials})

def contact(request):
    return render(request, 'contact.html')

#ADDING Paginator in Carlist ####
from django.core.paginator import Paginator
from django.db.models import Q

########FOR PAGINATION ###############
# def car_list(request):
#     # Query all cars from the database
#     cars = Car.objects.all()

#     # Set up pagination with 5 cars per page
#     paginator = Paginator(cars, 3)  # Change `5` to the number of cars you want per page
#     page_number = request.GET.get('page')  # Get the current page number from the query parameters
#     page_obj = paginator.get_page(page_number)  # Get the corresponding page

#     # Pass the page object to the template context
#     return render(request, 'carlist.html', {'page_obj': page_obj})

####################END ###############
def car_list(request):
    # Fetching query parameters
    query = request.GET.get('query', '')  # Search by name
    max_price = request.GET.get('max_price', '')  # Filter by max price
    
    # Base queryset
    cars = Car.objects.filter(availability_status=True)
    
    # Apply search and filter
    if query:
        cars = cars.filter(
            Q(make__icontains=query) | Q(model__icontains=query)
        )
    if max_price:
        try:
            max_price = float(max_price)
            cars = cars.filter(rental_price_per_day__lte=max_price)
        except ValueError:
            pass  # Ignore invalid max_price values
    
    # Pagination: Show 3 cars per page
    paginator = Paginator(cars, 3)  # 3 cars per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Context for the template
    context = {
        'page_obj': page_obj,
        'query': query,
        'max_price': max_price,
    }
    
    return render(request, 'carlist.html', context)


from django.contrib.auth.decorators import login_required
from django.contrib import messages
from datetime import datetime
from django.db import transaction


def book_car(request, car_id):
    car = get_object_or_404(Car, id=car_id)

    # Update car availability logic moved to Celery, no need to check here

    if request.method == "POST":
        # Extract and validate dates from the form
        start_date = request.POST.get('start_date')
        end_date = request.POST.get('end_date')
        location = request.POST.get('location')

        if not start_date or not end_date:
            return render(request, 'book_car.html', {
                'car': car,
                'error': 'Start, end dates and location are required.'
            })

        try:
            start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
            end_date = datetime.strptime(end_date, '%Y-%m-%d').date()
        except ValueError:
            return render(request, 'book_car.html', {
                'car': car,
                'error': 'Invalid date format.'
            })

        # Ensure start_date is before end_date
        if start_date >= end_date:
            return render(request, 'book_car.html', {
                'car': car,
                'error': 'End date must be after start date.'
            })

        rental_days = (end_date - start_date).days
        total_price = car.rental_price_per_day * rental_days

        # Create rental record and update car's availability atomically
        try:
            with transaction.atomic():
                rental = Rental.objects.create(
                    car=car,
                    customer=request.user,  
                    start_date=start_date,
                    end_date=end_date,
                    total_price=total_price,
                )
                car.availability_status = False
                car.save()

            # Redirect to the invoice view
            return redirect('invoice', rental_id=rental.id)
        except Exception as e:
            return render(request, 'book_car.html', {
                'car': car,
                'error': f"An error occurred: {str(e)}"
            })

    return render(request, 'book_car.html', {'car': car})

########    INVOICE #############
def invoice(request, rental_id):
    # Fetch the rental record or return a 404 if it doesn't exist
    rental = get_object_or_404(Rental, id=rental_id)
    car = rental.car  # Related car
    customer = rental.customer  # Related user
    # Ensure the invoice is created
    invoice, created = Invoice.objects.get_or_create(booking=rental)

    # Calculate rental days
    rental_days = (rental.end_date - rental.start_date).days + 1
    # Update invoice total price
    total_price = rental_days * rental.car.rental_price_per_day

    invoice.total_price = total_price
    invoice.save()

    # Create invoice details
    invoice_data = {
        'invoice_number': f"INV-{rental.id:06}",  # Example invoice format
        'rental': rental,
        'car': car,
        'customer': customer,
        'total_price': total_price,
        'start_date': rental.start_date,
        'end_date': rental.end_date,
        'rental_days': (rental.end_date - rental.start_date).days + 1,
        'issue_date': timezone.now(),
    }

    # Render the invoice page
    return render(request, 'invoice.html', invoice_data)


##Login Function
from django.contrib.auth import logout

from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login as auth_login
def login(request):
    if request.method == "POST":
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(request, username=username, password=password)
        if user:
            auth_login(request, user)
            messages.success(request,"Login Successful")
            return redirect('home')
        else:
            messages.error(request, " Invalid Usernamer and Password")

    return render (request, 'login.html')


def logout_task(request):
    logout(request)
    messages.success(request,"Logged Out Successfully")
    return redirect('login')


def register(request):
    if request.method == "POST":
        username = request.POST.get('username')
        email = request.POST.get('email')
        password1 = request.POST.get('password1')
        password2 = request.POST.get('password2')

        # Validation
        if password1 != password2:
            messages.error(request, "Passwords do not match.")
            return render(request, 'register.html')
        if User.objects.filter(username=username).exists():
            messages.error(request, "Username already exists.")
            return render(request, 'register.html')
        if User.objects.filter(email=email).exists():
            messages.error(request, "Email already in use.")
            return render(request, 'register.html')

        # Create user
        user = User.objects.create_user(username=username, email=email, password=password1)
        messages.success(request, "Registration successful! You can now log in.")

        # Send welcome email
        send_mail(
            

            f'Welcome to Our Service',  # Subject with username
            f'Hi {username},\n\nThank you for registering with us! We are excited to have you on board. Your Username is :: {username}!\n\nBest regards,\nThe Team',  # Email body
            'your_email@example.com',  # From
            [email],                   # To
            fail_silently=False,
        )
        return redirect('login')

    return render(request, 'register.html')


#this is to fetch the list of invoice created by logged in user #########
def invoice_list(request):
    # Fetch invoices where the logged-in user is the customer
    invoices = Invoice.objects.filter(booking__customer=request.user)
    return render(request, 'invoice_list.html', {'invoices': invoices})

# FOR THE ENQUIRY FORM SUBMISSION #
from django.conf import settings

def enquiry_form_submission(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        email = request.POST.get('email')
        phone = request.POST.get('phone')
        message = request.POST.get('message')

        subject = 'New Enquiry Submitted'
        email_body = f"""
        New enquiry submitted:

        Name: {name}
        Email: {email}
        Phone: {phone}

        Message:
        {message}
        """
        # Ensure settings.EMAIL_HOST_USER is not None or shadowed
        send_mail(subject, email_body, settings.EMAIL_HOST_USER, ['sanjeebsapkota18@gmail.com'])

        return render(request, 'enquiry_success.html')

    return render(request, 'enquiry.html')


# ### KHALTI PAYMENT GATEWAY INTEGRATION version 1 ###
# # 
import json
import requests
from django.conf import settings
from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse
from django.utils import timezone
from .models import Invoice

# # Khalti payment initiation view
# def initiate_khalti_payment(request, invoice_id):
#     invoice = get_object_or_404(Invoice, id=invoice_id)

#     khalti_url = "https://a.khalti.com/api/v2/epayment/initiate/"
#     headers = {
#         "Authorization": f"key {settings.KHALTI_SECRET_KEY}",  # Use the secret key from settings
#         "Content-Type": "application/json"
#     }

#     purchase_order_id = f"INV-{invoice.id:06}"

#     payload = {
#         "return_url": f"{settings.SITE_URL}/khalti/verify/{invoice.id}/",
#         "website_url": settings.SITE_URL,
#         "amount": int(invoice.total_price * 100),
#         "purchase_order_id": purchase_order_id,
#         "purchase_order_name": f"Rental Invoice {purchase_order_id}",
#         "customer_info": {
#             "name": request.user.get_full_name(),
#             "email": request.user.email,
#             "phone": request.user.profile.phone_number  # Uncomment if you have a phone number
#         },
#     }

#     try:
#         response = requests.post(khalti_url, headers=headers, json=payload)
#         response_data = response.json()

#         if response.status_code == 200:
#             return redirect(response_data["payment_url"])
#         else:
#             return JsonResponse({"error": response_data.get("detail", "Failed to initiate payment")})
#     except requests.RequestException as e:
#         return JsonResponse({"error": str(e)})

# # Khalti payment verification view
# def verify_khalti_payment(request, invoice_id):
#     invoice = get_object_or_404(Invoice, id=invoice_id)

#     pidx = request.GET.get("pidx")

#     if not pidx:
#         return JsonResponse({"error": "Invalid payment response"})

#     verify_url = "https://a.khalti.com/api/v2/payment/verify/"
#     headers = {
#         "Authorization": f"key {settings.KHALTI_SECRET_KEY}"
#     }

#     payload = {
#         "pidx": pidx
#     }

#     try:
#         response = requests.post(verify_url, headers=headers, json=payload)
#         response_data = response.json()

#         if response.status_code == 200 and response_data["status"] == "Completed":
#             invoice.is_paid = True
#             invoice.payment_date = timezone.now()
#             invoice.save()

#             return JsonResponse({"message": "Payment verified successfully"})
#         else:
#             return JsonResponse({"error": "Payment verification failed"})
#     except requests.RequestException as e:
#         return JsonResponse({"error": str(e)})


# # Khalti settings
# SITE_URL = "http://127.0.0.1:8000"  #  production site URL
# KHALTI_SECRET_KEY = "0fd148c3a04e489080b79cb9c54fdbb1"  




###########ESEWA PAYMENT VIEW ############
from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from .models import Rental, Payment
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
import requests

###### KHALTI VERSION 2 ########
def khalti_payment(request, rental_id):
    rental = get_object_or_404(Rental, id=rental_id)

    # Prepare data for frontend (Khalti requires client-side payment initialization)
    context = {
        'rental': rental,
        'public_key': '8e345dc558414cdfa3619a9cfbf6d2c5',  # Khalti Public Key
    }
    return render(request, 'khalti_payment.html', context)

@csrf_exempt
def khalti_verify(request):
    if request.method == "POST":
        token = request.POST.get("token")
        amount = request.POST.get("amount")  # Amount in paisa (e.g., Rs. 100 = 10000 paisa)
        rental_id = request.POST.get("rental_id")

        # Verify the payment using Khalti API
        url = "https://khalti.com/api/v2/payment/verify/"
        headers = {
            "Authorization": f"Key 0fd148c3a04e489080b79cb9c54fdbb1"  #  Khalti Secret Key
        }
        data = {
            "token": token,
            "amount": amount,
        }

        response = requests.post(url, headers=headers, data=data)

        if response.status_code == 200:
            response_data = response.json()

            # Mark payment as completed in your database
            rental = get_object_or_404(Rental, id=rental_id)
            payment = Payment.objects.create(
                rental=rental,
                user=request.user,
                amount=int(amount) / 100,  # Convert paisa to Rs.
                transaction_id=response_data['idx'],  # Khalti transaction ID
                status='Completed',
            )

            # Update the car's availability
            rental.car.availability_status = False
            rental.car.save()

            return JsonResponse({"success": True, "message": "Payment verified successfully!"})
        else:
            return JsonResponse({"success": False, "message": "Payment verification failed."})

    return JsonResponse({"success": False, "message": "Invalid request."})
