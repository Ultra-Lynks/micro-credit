# # signals.py
# from .emails import send_subscription_expired_email
# from django.db.models.signals import post_save
# from django.dispatch import receiver
# from datetime import timedelta
# from django.utils import timezone
# from .models import Order

# @receiver(post_save, sender=Order)
# def check_subscription_expiry(sender, instance, **kwargs):
#     if instance.ordered and instance.ordered_date:
#         expiration_date = instance.ordered_date + instance.get_total_duration()
#         if expiration_date <= timezone.now():
#             # Call the function to send the email
#             send_subscription_expired_email(instance.user.email)