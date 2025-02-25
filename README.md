Car availability is updated in real-time using Celery and Redis, providing a seamless user experience.
Spaces are all operations managed, meaning users can add or change rental locations integrally.
Resall is a simple platform where users can sign up and login using email/password.
Further registration requires confirmation by email.
It allows users to select a car from a reservation list, book it for a particular date/time and get a confirmation email.
**Email Notifications
**
Booking Confirmation: A confirmation email is sent to the user after a successful booking.
Celery: Asynchronous Background Task Management
Background tasks (sending email confirmations/reminders and so on) are also handled by Celery.
