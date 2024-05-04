from django import forms
from django_countries.fields import CountryField
from django_countries.widgets import CountrySelectWidget


PAYMENT_CHOICES = (
    ('S', 'Stripe'),
    ('P', 'PayPal'),
    ('ps','paystack')
)


class CheckoutForm(forms.Form):
    street_address = forms.CharField(required=True, widget=forms.TextInput(attrs={
        'placeholder':'1234 main str',
        'class': 'form-control'
    }))
    apartment_address = forms.CharField(required=True, widget=forms.TextInput(attrs={
            'placeholder':'Apartment or Suite',
            'class': 'form-control'
        }))
    phone_number = forms.CharField(required=True, widget=forms.TextInput(attrs={
            'placeholder':'Phone Number',
            'class': 'form-control'
        }))
    set_default_shipping = forms.BooleanField(required=False)
    use_default_shipping = forms.BooleanField(required=False)
    
    billing_address = forms.CharField(required=True, widget=forms.TextInput(attrs={
            'placeholder':'Apartment or Suite',
            'class': 'form-control'
        }))
    street_address = forms.CharField(required=True, widget=forms.TextInput (attrs={
            'placeholder':'Apartment or Suite',
            'class': 'form-control'
        }))
    country = forms.CharField(required=True, widget=forms.TextInput (attrs={
            'placeholder':'country',
            'class': 'form-control'
        }))
    country_zip = forms.CharField(required=True)

    set_default_billing = forms.BooleanField(required=False)
    use_default_billing = forms.BooleanField(required=False)

    # payment_option = forms.ChoiceField(
    #     widget=forms.RadioSelect, choices=PAYMENT_CHOICES)


# class CheckoutForm(forms.Form):
#     shipping_address = forms.CharField(required=False)
#     shipping_address2 = forms.CharField(required=False)
#     shipping_country = forms.CharField(required=False)
#     shipping_zip = forms.CharField(required=False)
    
#     set_default_shipping = forms.BooleanField(required=False)
#     use_default_shipping = forms.BooleanField(required=False)
#     same_billing_address = forms.BooleanField(required=False)

#     billing_address = forms.CharField(required=False)
#     billing_address2 = forms.CharField(required=False)
#     billing_country = forms.CharField(required=False,)
#     billing_zip = forms.CharField(required=False)

#     set_default_billing = forms.BooleanField(required=False)
#     use_default_billing = forms.BooleanField(required=False)

#     payment_option = forms.ChoiceField(
#         widget=forms.RadioSelect, choices=PAYMENT_CHOICES)


class CouponForm(forms.Form):
    code = forms.CharField(widget=forms.TextInput(attrs={
        'class': 'form-control',
        'placeholder': 'Promo code',
        'aria-label': 'Recipient\'s username',
        'aria-describedby': 'basic-addon2'
    }))


class RefundForm(forms.Form):
    ref_code = forms.CharField()
    message = forms.CharField(widget=forms.Textarea(attrs={
        'rows': 4
    }))
    email = forms.EmailField()


class PaymentForm(forms.Form):
    stripeToken = forms.CharField(required=False)
    save = forms.BooleanField(required=False)
    use_default = forms.BooleanField(required=False)


from .models import UserProfile

class UserProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ['image']