from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.conf import settings
from django.db import models
from django.db.models import Sum
from django.shortcuts import reverse
from django.utils.text import slugify
from django_countries.fields import CountryField
import requests
from django.conf import settings


CATEGORY_CHOICES = (
    ('Electronics', 'Electronics'),
    ('Clothing', 'Clothing'),
    ('Furniture', 'Furniture'),
    ('Watches', 'Watches'),
    ('Shoes', 'Shoes'),
)


LABEL_CHOICES = (
    ('Electronics', 'Electronics'),
    ('Clothing', 'Clothing'),
    ('Furniture', 'Furniture'),
    ('Watches', 'Watches'),
    ('Shoes', 'Shoes'),
)

ADDRESS_CHOICES = (
    ('B', 'Billing'),
    ('S', 'Shipping'),
)

CATEGORY_SALES = (
    ('Electronics', 'Electronics'),
    ('Clothing', 'Clothing'),
    ('Furniture', 'Furniture'),
    ('Watches', 'Watches'),
    ('Shoes', 'Shoes'),
)

class UserProfile(models.Model):
    image = models.ImageField(blank=True, null=True)
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    stripe_customer_id = models.CharField(max_length=50, blank=True, null=True)
    one_click_purchasing = models.BooleanField(default=False)

    def __str__(self):  # Correct method name
        return self.user.username


class Header(models.Model):
    title = models.CharField(max_length=100)
    category = models.CharField(choices=CATEGORY_CHOICES, max_length=20)
    slug = models.SlugField(max_length=2044)
    image = models.ImageField()

    def __str__(self):  # Correct method name
        return self.title


class Item(models.Model):
    title = models.CharField(max_length=100)
    quantity = models.FloatField(blank=True, null=True)
    price = models.FloatField()
    discount_price = models.FloatField(blank=True, null=True)
    category = models.CharField(choices=CATEGORY_CHOICES, max_length=20)
    sales_category = models.CharField(choices=CATEGORY_SALES, max_length=20)
    label = models.CharField(choices=LABEL_CHOICES, max_length=20)
    slug = models.SlugField(max_length=2044)
    description = models.TextField(max_length=2022)
    image = models.ImageField()
    preview1 = models.ImageField(blank=True, null=True)
    preview2 = models.ImageField(blank=True, null=True)
    preview3 = models.ImageField(blank=True, null=True)

    def __str__(self):  # Correct method name
        return self.title

    # ... Other methods ...

    def save(self, *args, **kwargs):  # new
        if not self.slug:
            self.slug = slugify(self.title)
        return super().save(*args, **kwargs)
    
    def get_absolute_url(self):
        return reverse("core:add-to-cart", kwargs={
            'slug': self.slug
        })

    def get_add_to_cart_url(self):
        return reverse("core:add-to-cart", kwargs={
            'slug': self.slug
        })

    def get_remove_from_cart_url(self):
        return reverse("core:remove-from-cart", kwargs={
            'slug': self.slug
        })
        
    
class OrderItem(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL,
                             on_delete=models.CASCADE)
    ordered = models.BooleanField(default=False)
    item = models.ForeignKey(Item, on_delete=models.CASCADE)
    quantity = models.IntegerField(default=1)

    def __str__(self):
        return f"{self.quantity} of {self.item.title}"

    def get_total_item_price(self):
        return self.quantity * self.item.price

    def get_total_discount_item_price(self):
        return self.quantity * self.item.discount_price

    def get_amount_saved(self):
        return self.get_total_item_price() - self.get_total_discount_item_price()

    def get_final_price(self):
        if self.item.discount_price:
            return self.get_total_discount_item_price()
        return self.get_total_item_price()


class Order(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL,
                             on_delete=models.CASCADE)
    ref_code = models.CharField(max_length=20, blank=True, null=True)
    items = models.ManyToManyField(OrderItem)
    start_date = models.DateTimeField(auto_now_add=True)
    ordered_date = models.DateTimeField()
    ordered = models.BooleanField(default=False)
    shipping_address = models.ForeignKey(
        'Address', related_name='shipping_address', on_delete=models.SET_NULL, blank=True, null=True)
    billing_address = models.ForeignKey(
        'Address', related_name='billing_address', on_delete=models.SET_NULL, blank=True, null=True)
    payment = models.ForeignKey(
        'Payment', on_delete=models.SET_NULL, blank=True, null=True)
    coupon = models.ForeignKey(
        'Coupon', on_delete=models.SET_NULL, blank=True, null=True)
    STATUS_CHOICES = (
        ('C', 'Cart'),
        ('B', 'Billing Address Added'),
        ('P', 'Payment Processing'),
        ('D', 'Being Delivered'),
        ('R', 'Received'),
        ('F', 'Refunded'),
    )

    status = models.CharField(max_length=1, choices=STATUS_CHOICES, default='C')

    '''
    1. Item added to cart
    2. Adding a billing address
    (Failed checkout)
    3. Payment
    (Preprocessing, processing, packaging etc.)
    4. Being delivered
    5. Received
    6. Refunds
    '''
    def get_status_display(self):
        return dict(self.STATUS_CHOICES)[self.status]

    def __str__(self):
        return self.user.username

    def get_total(self):
        total = 0
        for order_item in self.items.all():
            total += order_item.get_final_price()
        if self.coupon:
            total -= self.coupon.amount
        return total
    
    def send_order_to_swoove(self):
        swoove_order_data = {
            "delivery_list": [
                {
                    "pickup": {
                        "type": "pickup",
                        "value": "pickup address",  # Replace with actual pickup address
                        "contact": {
                            "name": "pickup contact name",  # Replace with pickup contact name
                            "mobile": "pickup contact mobile",  # Replace with pickup contact mobile
                            "email": "pickup contact email"  # Replace with pickup contact email
                        },
                        "country_code": "GH",  # Replace with pickup country code
                        "lat": "pickup latitude",  # Replace with pickup latitude
                        "lng": "pickup longitude",  # Replace with pickup longitude
                        "location": "pickup location"  # Replace with pickup location
                    },
                    "dropoff": {
                        "type": "dropoff",
                        "value": "dropoff address",  # Replace with actual dropoff address
                        "contact": {
                            "name": "dropoff contact name",  # Replace with dropoff contact name
                            "mobile": "dropoff contact mobile",  # Replace with dropoff contact mobile
                            "email": "dropoff contact email"  # Replace with dropoff contact email
                        },
                        "country_code": "GH",  # Replace with dropoff country code
                        "lat": "dropoff latitude",  # Replace with dropoff latitude
                        "lng": "dropoff longitude",  # Replace with dropoff longitude
                        "location": "dropoff location"  # Replace with dropoff location
                    },
                    "items": [
                        {
                            # Add item details here
                        }
                    ],
                    "contacts": {
                        "name": "contact name",  # Replace with contact name
                        "mobile": "contact mobile",  # Replace with contact mobile
                        "email": "contact email"  # Replace with contact email
                    },
                    "instructions": "Special instructions",
                    "reference": str(self.id)  # Use the order ID as the reference
                }
            ],
            "estimate_id": "string"  # Estimate ID from Swoove
        }

        headers = {
            "Authorization": f"Bearer {settings.SWOOVE_API_KEY}"
        }

        response = requests.post(
            "https://api.swoove.delivery/v2/orders",
            json=swoove_order_data,
            headers=headers
        )

        if response.status_code == 200:
            # Update your order status or save relevant information if needed
            self.is_sent_to_swoove = True
            self.save()
            return True
        else:
            return False


class Address(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL,
                             on_delete=models.CASCADE)
    street_address = models.CharField(max_length=100, blank=False, null=False)
    apartment_address = models.CharField(max_length=100, blank=False, null=False)
    phone_number = models.CharField(max_length=200, blank=False, null=False)
    country = CountryField(multiple=False)
    zip = models.CharField(max_length=100)
    # address_type = models.CharField(max_length=1, choices=ADDRESS_CHOICES)
    default = models.BooleanField(default=False)

    def __str__(self):
        return self.user.username

    class Meta:
        verbose_name_plural = 'Addresses'


class Payment(models.Model):
    paystack_id = models.CharField(max_length=50)
    user = models.ForeignKey(settings.AUTH_USER_MODEL,
                             on_delete=models.SET_NULL, blank=True, null=True)
    amount = models.FloatField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.user.username


class Coupon(models.Model):
    code = models.CharField(max_length=15)
    amount = models.FloatField()

    def __str__(self):
        return self.code


class Refund(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    reason = models.TextField()
    accepted = models.BooleanField(default=False)
    email = models.EmailField()

    def __str__(self):
        return f"{self.pk}"


def userprofile_receiver(sender, instance, created, *args, **kwargs):
    if created:
        userprofile = UserProfile.objects.create(user=instance)


post_save.connect(userprofile_receiver, sender=settings.AUTH_USER_MODEL)


STATUS = (
    (0, "Draft"),
    (1, "Publish")
)


class Blog(models.Model):
    title = models.CharField(max_length=200, unique=True)
    image = models.ImageField()
    slug = models.SlugField(max_length=200, unique=True)
    author = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='blog_posts')
    updated_on = models.DateTimeField(auto_now=True)
    content = models.TextField()
    created_on = models.DateTimeField(auto_now_add=True)
    status = models.IntegerField(choices=STATUS, default=0)

    class Meta:
        ordering = ['-created_on']

    def __str__(self):
        return self.title




from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
import secrets
from .paystack  import  Paystack

# Create your models here.
class UserWallet(models.Model):
    user = models.OneToOneField(User, null=True, on_delete=models.CASCADE)
    currency = models.CharField(max_length=50, default='NGN')
    created_at = models.DateTimeField(default=timezone.now, null=True)

    def __str__(self):
        return self.user.__str__()

class Payments(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, blank=True, null=True)
    amount = models.PositiveIntegerField()
    ref = models.CharField(max_length=200)
    email = models.EmailField()
    verified = models.BooleanField(default=False)
    date_created = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ('-date_created',)

    def __str__(self):
        return f"Payment: {self.amount}"

    def save(self, *args, **kwargs):
        while not self.ref:
            ref = secrets.token_urlsafe(50)
            object_with_similar_ref = Payments.objects.filter(ref=ref)
            if not object_with_similar_ref:
                self.ref = ref
                
        super().save(*args, **kwargs)
    
    def amount_value(self):
        return int(self.amount) * 100
    
    def verify_payment(self):
        paystack = Paystack()
        status, result = paystack.verify_payment(self.ref, self.amount)
        if status:
            if result['amount'] / 100 == self.amount:
                self.verified = True
            self.save()
        if self.verified:
            return True
        return False



class Gallery(models.Model):
    title = models.CharField(max_length=200, unique=True)
    image = models.ImageField(upload_to='users/%Y/%m/%d/', blank=True)
    image2 = models.ImageField(upload_to='users/%Y/%m/%d/', blank=True)
    
    def __str__(self):
        return self.title