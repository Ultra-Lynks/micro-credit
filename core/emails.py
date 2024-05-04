# emails.py

from django.core.mail import send_mail

def send_subscription_expired_email(subscriber_email):
    subject = 'Your subscription has expired'
    message = 'Your subscription has expired. Please renew to continue using our services.'
    from_email = 'loozeele@gmail.com.com'
    recipient_list = [subscriber_email]
    send_mail(subject, message, from_email, recipient_list)