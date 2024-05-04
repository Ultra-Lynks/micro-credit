from base64 import urlsafe_b64decode
from django.views import generic
from .models import Blog
import random
import string
import json
import stripe

from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import ObjectDoesNotExist
from django.shortcuts import redirect
from django.shortcuts import render, get_object_or_404
from django.utils import timezone
from django.views.generic import ListView, DetailView, View, TemplateView
from django.db.models import Q # new
from django.shortcuts import render, redirect
from admin_datta.forms import RegistrationForm, LoginForm, UserPasswordChangeForm, UserPasswordResetForm, UserSetPasswordForm
from django.contrib.auth.views import LoginView, PasswordChangeView, PasswordResetConfirmView, PasswordResetView
from django.views.generic import CreateView
from django.contrib.auth import logout
import requests
from django.shortcuts import render, redirect
from django.views import View
from django.core.exceptions import ObjectDoesNotExist
from django.contrib import messages
from .models import Order, Address, OrderItem ,Gallery # Import OrderItem model
from .forms import CheckoutForm  # Assuming you have a CheckoutForm
from django.conf import settings  # Import your project settings

# from .paystack import Paystack
from .forms import CheckoutForm, CouponForm, RefundForm, PaymentForm, UserProfileForm
from .models import Item, OrderItem, Order, Address, Payment, Coupon, Refund, UserProfile, Header
STRIPE_SECRET_KEY = 'sk_test_51MeelOFNCZIiiBouiLDQCHBJXShE6YYyHuk22hqolzbNHYxoa9bUIUQk9kHxQLgI1VSFDiwqHj5TWuZvWG9moMnJ002JPUI5IU'
STRIPE_PUBLIC_KEY = 'pk_test_51MeelOFNCZIiiBouxAXvfAESTEVjnRpkIE9Dgi9wnxNviMKwHWvEPQEG2NBapdtQcfblAiTKvfVIuF34eBc2ZsTs00AP1jwgp4'

STRIPE_PUBLIC_KEY = ''
STRIPE_SECRET_KEY = ''

stripe.api_key = STRIPE_SECRET_KEY
import random
import string
from django.shortcuts import render, get_object_or_404
from django.core.exceptions import ObjectDoesNotExist
from django.views.generic import ListView, DetailView, View
from .models import Item, OrderItem, Order, Address, Payment
from django.shortcuts import redirect
from django.utils import timezone
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from .forms import CheckoutForm
from pypaystack2 import Paystack
from django.http import JsonResponse
import json
from .filters import ItemFilter
from django.views import generic
from django.db.models import Sum, Q
from .models import Item
from datetime import date
from .filters import OrderFilter
# Create your views here.

# def search_products(request):
# 	if request.method == 'POST':
# 		search_str = json.loads(request.body).get('searchText')

# 		results = Item.objects.filter(title__istartswith=search_str)|Item.objects.filter(category__istartswith=search_str)

# 		data = results.values()
# 		return JsonResponse(list(data), safe=False)
import requests
from requests.exceptions import RequestException
import time
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import Order  # Import your Order model
from .serializers import OrderSerializer  # Create a serializer for your Order model

max_retries = 3
retry_delay = 2  # seconds

for attempt in range(max_retries):
    try:
        response = requests.get("https://live.swooveapi.com/bulk-estimate/create-bulk-estimate")
        if response.status_code == 200:
            # Successful response, process data
            break
    except RequestException as e:
        print(f"Attempt {attempt+1} failed: {e}")
        if attempt < max_retries - 1:
            print(f"Retrying in {retry_delay} seconds...")
            time.sleep(retry_delay)
        else:
            print("Max retries exceeded.")

def create_ref_code():
	return ''.join(random.choices(string.ascii_lowercase + string.digits, k=20))

def products(request):
	context = {
		
	}
	return render(request, "product-page.html", context)

def is_valid_form(values):
	valid = True
	for field in values:
		if field == '':
			valid = False
	return valid




class SendOrderToSwoove(APIView):
    def post(self, request, *args, **kwargs):
        order_id = request.POST.get('order_id')  # Get the order ID from the POST data
        try:
            order = Order.objects.get(id=order_id)
        except Order.DoesNotExist:
            return Response({"message": "Order not found"}, status=status.HTTP_404_NOT_FOUND)

        headers = {
            "Authorization": f"Bearer {settings.SWOOVE_LIVE_API_KEY}"  # Use your live API key
        }
        swoove_order_data = {
            "delivery_list": [
                {
            "pickup": {
                "type": "string",
                "value": order.shipping_address.street_address,
                "contact": {
                    "name": order.shipping_address.user.username,
                    "mobile": order.shipping_address.phone_number,
                    "email": order.shipping_address.user.email
                },
                "country_code": order.shipping_address.country.code,
                "lat": None,
                "lng": None,
                "location": None
            },
            "dropoff": {
                "type": "string",
                "value": order.billing_address.street_address,
                "contact": {
                    "name": order.billing_address.user.username,
                    "mobile": order.billing_address.phone_number,
                    "email": order.billing_address.user.email
                },
                "country_code": order.billing_address.country.code,
                "lat": None,
                "lng": None,
                "location": None
            },
            "items": [],
            "contact": {
                "name": None,
                "mobile": order.shipping_address.phone_number,
                "email": None
            },
            "instructions": None,
            "reference": "string",
            "estimate_id": "string"
        }
            ],
            # ... other order details ...
        }

        # Add items to the Swoove order data
        for order_item in order.items.all():
            item_data = {
                "name": order_item.item.title,
                "quantity": order_item.quantity,
                # ... other item details ...
            }
            swoove_order_data["delivery_list"][0]["items"].append(item_data)

        response = requests.post(
            "https://live.swooveapi.com/bulk-estimate/create-bulk-estimate",
            json=swoove_order_data,
            headers=headers
        )

        if response.status_code == 200:
            # Successfully sent order to Swoove
            return Response({"message": "Order sent to Swoove"}, status=status.HTTP_200_OK)
        else:
            # Failed to send order to Swoove
            return Response({"message": "Failed to send order to Swoove"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

# ...
# class SendOrderToSwoove(APIView):
    
#     def post(self, request, *args, **kwargs):
#         order_id = request.data.get('order_id')  # Get the order ID from the request
#         try:
#             order = Order.objects.get(id=order_id)
#         except Order.DoesNotExist:
#             return Response({"message": "Order not found"}, status=status.HTTP_404_NOT_FOUND)

#         headers = {
#             "Authorization": f"Bearer {settings.s}"  # Use your live API key
#         }
#         swoove_order_data = {
#             "delivery_list": [
#                  {
#             "pickup": {
#                 "type": "string",
#                 "value": order.shipping_address.street_address,
#                 "contact": {
#                     "name": order.shipping_address.user.username,
#                     "mobile": order.shipping_address.phone_number,
#                     "email": order.shipping_address.user.email
#                 },
#                 "country_code": order.shipping_address.country.code,
#                 "lat": None,
#                 "lng": None,
#                 "location": None
#             },
#             "dropoff": {
#                 "type": "string",
#                 "value": order.billing_address.street_address,
#                 "contact": {
#                     "name": order.billing_address.user.username,
#                     "mobile": order.billing_address.phone_number,
#                     "email": order.billing_address.user.email
#                 },
#                 "country_code": order.billing_address.country.code,
#                 "lat": None,
#                 "lng": None,
#                 "location": None
#             },
#             "items": [],
#             "contact": {
#                 "name": None,
#                 "mobile": order.shipping_address.phone_number,
#                 "email": None
#             },
#             "instructions": None,
#             "reference": "string",
#             "estimate_id": "string"
#         }
#             ],
#             # ... other order details ...
#         }

#         # Add items to the Swoove order data
#         for order_item in order.items.all():
#             item_data = {
#                 "name": order_item.item.title,
#                 "quantity": order_item.quantity,
#                 # ... other item details ...
#             }
#             swoove_order_data["delivery_list"][0]["items"].append(item_data)

#         response = requests.post(
#             "https://live.swooveapi.com/bulk-estimate/create-bulk-estimate",
#             json=swoove_order_data,
#             headers=headers
#         )

#         if response.status_code == 200:
#             # Successfully sent order to Swoove
#             return Response({"message": "Order sent to Swoove"}, status=status.HTTP_200_OK)
#         else:
#             # Failed to send order to Swoove
#             return Response({"message": "Failed to send order to Swoove"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)



class CheckoutView(View):
    def get(self, *args, **kwargs):
        try:
            order = Order.objects.get(user=self.request.user, ordered=False)
            form = CheckoutForm()
            context = {
                'form': form,
                'order': order
            }
            shipping_address_qs = Address.objects.filter(
                user=self.request.user,
                default=True
            )
            if shipping_address_qs.exists():
                context.update({'default_shipping_address': shipping_address_qs[0]})

        except ObjectDoesNotExist:
            messages.info(self.request, "You do not have an active order")
            return redirect("core:checkout")
        

        return render(self.request, "cyrus/checkout.html", context)
    
    
    def purchase_cost_and_plan(request, order_id):
        order = Order.objects.get(pk=order_id)
        total_cost = sum(order_item.get_total_item_price() for order_item in order.items.all())
    
    # Calculate the cost breakdown for 2 to 4 months
        months = [2, 3, 4]
        monthly_costs = [total_cost / m for m in months]

        return render(request, 'cyrus/checkout.html', {'order': order, 'total_cost': total_cost, 'months_and_costs': zip(months, monthly_costs)})

    def post(self, *args, **kwargs):
        form = CheckoutForm(self.request.POST or None)
        try:
            order = Order.objects.get(user=self.request.user, ordered=False)
            if form.is_valid():
                use_default_shipping = form.cleaned_data.get('use_default_shipping')
                if use_default_shipping:
                    address_qs = Address.objects.filter(
                        user=self.request.user,
                        default=True
                    )
                    if address_qs.exists():
                        shipping_address = address_qs[0]
                        order.shipping_address = shipping_address
                        order.save()
                    else:
                        messages.info(self.request, "No default address")
                        return redirect("core:checkout")
                else:
                    street_address = form.cleaned_data.get('street_address')
                    apartment_address = form.cleaned_data.get('apartment_address')
                    phone_number = form.cleaned_data.get('phone_number')

                    if is_valid_form([street_address, apartment_address, phone_number]):
                        shipping_address = Address(
                            user=self.request.user,
                            street_address=street_address,
                            apartment_address=apartment_address,
                            phone_number=phone_number,
                        )
                        shipping_address.save()
                        order.shipping_address = shipping_address
                        order.save()

                        set_default_shipping = form.cleaned_data.get('set_default_shipping')
                        if set_default_shipping:
                            shipping_address.default = True
                            shipping_address.save()

                        # Update ordered_date in the order model
                        order.ordered_date = timezone.now()
                        order.save()

                        # Send the order to Swoove API
                        send_order_to_swoove = SendOrderToSwoove()
                        response = send_order_to_swoove.post(request=self.request, order_id=order.id)

                        if response.status_code == 200:
                            # Successfully sent order to Swoove
                            return redirect('core:order_success')
                        else:
                            # Failed to send order to Swoove
                            messages.error(self.request, "Failed to send order to Swoove")
                            return redirect('core:f_checkout')
                    else:
                        messages.info(self.request, "Please fill in the required fields")
                return redirect('core:f_checkout')
        except ObjectDoesNotExist:
            messages.error(self.request, "You do not have active orders")
            return redirect('core:checkout')

class ItemDetailView(DetailView):
	model = Item
	template_name = "product-page.html"

@login_required
def add_to_cart(request, slug):
	item = get_object_or_404(Item, slug=slug)
	order_item, created = OrderItem.objects.get_or_create(
		item=item,
		user=request.user,
		ordered=False
		)
	order_qs = Order.objects.filter(user=request.user, ordered=False)
	if order_qs.exists():
		order = order_qs[0]
		if order.items.filter(item__slug=item.slug).exists():
			order_item.quantity += 1
			order_item.save()
			messages.info(request, "This item was quantity was updated")
			return redirect('order_summary')
		else:
			messages.info(request, "This item was added to your cart")
			order.items.add(order_item)
			return redirect('order_summary')
	else:
		ordered_date = timezone.now()
		order = Order.objects.create(user=request.user, ordered_date=ordered_date)
		order.items.add(order_item)
		messages.info(request, "This item was added to your cart")
		return redirect('core:order_summary')
	
@login_required
def remove_from_cart(request,slug):
	item = get_object_or_404(Item, slug=slug)
	order_qs = Order.objects.filter(user=request.user, ordered=False)
	if order_qs.exists():
		order = order_qs[0]
		if order.items.filter(item__slug=item.slug).exists():
			order_item = OrderItem.objects.filter(
					item=item,
					user=request.user,
					ordered=False
			)[0]
			order.items.remove(order_item)
			messages.info(request, "This item was removed from your cart")
			return redirect('core:order-summary')
		else:
			messages.info(request, "This item is not in your cart")
			return redirect('core:shop', slug=slug)	
	else:
		messages.info(request, "You do not have an active order")
		return redirect('core:shop', slug=slug)
	
class OrderSummaryView(LoginRequiredMixin, View):
	def get(self, *args, **kwargs):
		try:
			order = Order.objects.get(user=self.request.user, ordered=False)
			context ={
				'object': order
			}
			return render(self.request, 'cyrus/cart.html', context)
		except ObjectDoesNotExist:
			messages.error(self.request, "You do not have an active order")
			return redirect("/")
		

@login_required
def remove_single_item_from_cart(request,slug):
	item = get_object_or_404(Item, slug=slug)
	order_qs = Order.objects.filter(user=request.user, ordered=False)
	if order_qs.exists():
		order = order_qs[0]
		if order.items.filter(item__slug=item.slug).exists():
			order_item = OrderItem.objects.filter(
					item=item,
					user=request.user,
					ordered=False
			)[0]
			if order_item.quantity > 1:
				order_item.quantity -= 1
				order_item.save()
			else:
				order.items.remove(order_item)
			messages.info(request, "This item quantity was updated")
			return redirect('order_summary')
		else:
			messages.info(request, "This item is not in your cart")
			return redirect('product_page', slug=slug)	
	else:
		messages.info(request, "You do not have an active order")
		return redirect('product_page', slug=slug)



def final_checkout(request):
	order = Order.objects.get(user=request.user, ordered=False)
	if order.shipping_address:
		context = {
					'order':order,
					}
		return render(request, 'final_checkout.html', context)
	else:
		messages.warning(request, "You have not added an address")
		return redirect("checkout")
		


class PaymentView(View):
	def get(self, *args, **kwargs):
		transaction = Paystack(authorization_key = 'sk_live_ab3832c3b9fc0b1c655e1145f2d15ba234947589')
		response = transaction.verify(kwargs['id'])
		data = JsonResponse(response, safe=False)

		if response[3]:
			try:
				order = Order.objects.get(user=self.request.user, ordered=False)
				payment = Payment()
				payment.paystack_id = kwargs['id']
				payment.user = self.request.user
				payment.amount = order.get_total()
				payment.save()

				order_items = order.items.all()
				order_items.update(ordered=True)
				for item in order_items:
					item.save()

				order.ordered = True
				order.payment = payment
				order.ref_code = create_ref_code()
				order.save()

				messages.success(self.request, "order was successful")
				return redirect("/")
			except ObjectDoesNotExist:
				messages.success(self.request, "Your order was successful")
				return redirect("/")
		else:
			messages.danger(self.request, "Could not verify the transaction")
			return redirect("/")


# class HomeView(ListView):
#     def get(self, *args, **kwargs):
#     Items = Item.objects.all()
#     myfilter = ItemFilter(self.request.GET, queryset = Items)
#     Items = myfilter.qs
#     context = {'Item':Items, 'myfilter':myfilter}
#     return render(self.request, "home.html", context)
	

class Appad(TemplateView): 
    template_name = "cyrus/app.html"



class HomeView(ListView):
    
    
    
    # def get_context_data(self,*args, **kwargs):
    #     context = super(HomeView, self).get_context_data(*args,**kwargs)
    #     context['items'] = Item.objects.all()
    #     context['items.count'] = Item.objects.all().count()
    #     context['myfilter'] = ItemFilter.qs
    #     return context
    
    def get(self, *args, **kwargs):
        Items = Item.objects.all()
        Headers = Header.objects.all()
        myfilter = ItemFilter(self.request.GET, queryset = Items)
        count = Item.objects.all().count()
        Items = myfilter.qs
        context = {'Item':Items, 'myfilter':myfilter, 'count':count, 'Header':Headers}
        return render(self.request, "cyrus/shop.html", context)


# def Home(request):
#     # Query all posts
#     search_post = request.GET.get('search')
    
#     if search_post:
#         items = Item.objects.filter(Q(title__icontains=search_post) & Q(content__icontains=search_post))
#     else:
#     # If not searched, return default posts
#         items = Item.objects.all()

#     return render(request, 'home.html', {'items': items})

class IndexView(ListView):
    
    def get(self, *args, **kwargs):
        Items = Item.objects.all()
        myfilter = ItemFilter(self.request.GET, queryset = Items)
        count = Item.objects.all().count()
        Items = myfilter.qs
        out_of_stock_items_count = 0
        items = Item.objects.all()
        Headers = Header.objects.all()

        for item in items:
            total_quantity_sold = OrderItem.objects.filter(item=item, order__ordered=True).aggregate(total_quantity=Sum('quantity'))['total_quantity']
            if total_quantity_sold is None:
                total_quantity_sold = 0
            available_quantity = item.quantity - total_quantity_sold if item.quantity else 0
            if available_quantity <= 0:
                out_of_stock_items_count += 1
        context = {'Item':Items, 'myfilter':myfilter, 'count':count, 'out_of_stock_items_count':out_of_stock_items_count, 'Header':Headers}
        return render(self.request, "cyrus/index.html", context)


# def index(request):
#     # Query all posts
#     search_post = request.GET.get('search')
    
#     if search_post:
#         items = Item.objects.filter(Q(title__icontains=search_post) & Q(content__icontains=search_post))
#     else:
#     # If not searched, return default posts
#         items = Item.objects.all()

#     return render(request, 'index.html', {'items': items})


class OrderSummaryView(LoginRequiredMixin, View):
    def get(self, *args, **kwargs):
        try:
            order = Order.objects.get(user=self.request.user, ordered=False)
            context = {
                'object': order
            }
            return render(self.request, 'cyrus/cart.html', context)
        except ObjectDoesNotExist:
            messages.warning(self.request, "You do not have an active order")
            return redirect("/")

class Fq(TemplateView): 
    template_name = "store/fq.html"



from django.shortcuts import render, redirect
from .models import UserProfile, Order
from .forms import UserProfileForm
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView

def user_profile_view(request):
    if request.method == 'POST':
        user_profile = UserProfile.objects.get(user=request.user)
        form = UserProfileForm(request.POST, instance=user_profile)
        if form.is_valid():
            print("Form is valid. Saving...")
            instance = form.save()
            print("Form saved:", instance)
        return redirect('core:userc')
              # Redirect to the profile page after form submission
    else:
        user_profile = UserProfile.objects.get(user=request.user)
        form = UserProfileForm(instance=user_profile)

    orders = Order.objects.filter(user=request.user).order_by('-ordered_date')

    context = {
        'user_profile': user_profile,
        'form': form,
        'orders': orders,
    }

    return render(request, 'store/user.html', context)


from django.http import JsonResponse
from django.views import View
import requests

from django.shortcuts import get_object_or_404
from .models import Order

import requests
from django.shortcuts import render, redirect
from django.http import JsonResponse
from .models import UserProfile, Item, Order

def create_order(request):
    if request.method == 'POST':
        # Create the order
        user = request.user  # Assuming the user is authenticated
        order = Order.objects.create(user=user)
        
        # Add items to the order (you should modify this based on your logic)
        items = Item.objects.all()  # Fetch all available items
        for item in items:
            order.items.create(item=item, quantity=1)
        
        # Send the order to Swoove
        if order.send_order_to_swoove():
            return JsonResponse({'success': True})
        else:
            return JsonResponse({'success': False})
    
    return render(request, 'create_order.html')

def order_details(request, order_id):
    try:
        order = Order.objects.get(id=order_id)
    except Order.DoesNotExist:
        return JsonResponse({'error': 'Order not found'}, status=404)
    
    # Fetch order details from Swoove using the Swoove API
    headers = {
        "Authorization": f"Bearer {settings.SWOOVE_API_KEY}"
    }
    response = requests.get(
        f"https://api.swoove.delivery/v2/orders/{order_id}",
        headers=headers
    )
    
    if response.status_code == 200:
        swoove_order_data = response.json()
        return JsonResponse(swoove_order_data)
    else:
        return JsonResponse({'error': 'Failed to fetch order details from Swoove'}, status=500)



class ItemDetailView(DetailView):
    model = Item
    template_name = "product.html"
    
    ''' def get(self, *args, **kwargs):
        Items = Item.objects.all()
        context = {'Item':Items}
        return render(self.request, "product.html", context) '''


@login_required
def add_to_cart(request, slug):
    item = get_object_or_404(Item, slug=slug)
    order_item, created = OrderItem.objects.get_or_create(
        item=item,
        user=request.user,
        ordered=False
    )
    order_qs = Order.objects.filter(user=request.user, ordered=False)
    if order_qs.exists():
        order = order_qs[0]
        # check if the order item is in the order
        if order.items.filter(item__slug=item.slug).exists():
            order_item.quantity += 1
            order_item.save()
            messages.info(request, "This item quantity was updated.")
            return redirect("core:order-summary")
        else:
            order.items.add(order_item)
            messages.info(request, "This item was added to your cart.")
            return redirect("core:order-summary")
    else:
        ordered_date = timezone.now()
        order = Order.objects.create(
            user=request.user, ordered_date=ordered_date)
        order.items.add(order_item)
        messages.info(request, "This item was added to your cart.")
        return redirect("core:order-summary")


@login_required
def add_to_cart(request, slug):
    item = get_object_or_404(Item, slug=slug)
    order_item, created = OrderItem.objects.get_or_create(
        item=item,
        user=request.user,
        ordered=False
    )
    order_qs = Order.objects.filter(user=request.user, ordered=False)
    if order_qs.exists():
        order = order_qs[0]
        if order.items.filter(item__slug=item.slug).exists():
            order_item.quantity += 1
            order_item.save()
        else:
            order.items.add(order_item)
        messages.success(request, "This item was added to your cart.")
    else:
        ordered_date = timezone.now()
        order = Order.objects.create(user=request.user, ordered_date=ordered_date)
        order.items.add(order_item)
        messages.success(request, "This item was added to your cart.")
    return redirect("core:order-summary")



@login_required
def remove_single_item_from_cart(request, slug):
    item = get_object_or_404(Item, slug=slug)
    order_qs = Order.objects.filter(
        user=request.user,
        ordered=False
    )
    if order_qs.exists():
        order = order_qs[0]
        # check if the order item is in the order
        if order.items.filter(item__slug=item.slug).exists():
            order_item = OrderItem.objects.filter(
                item=item,
                user=request.user,
                ordered=False
            )[0]
            if order_item.quantity > 1:
                order_item.quantity -= 1
                order_item.save()
            else:
                order.items.remove(order_item)
            messages.info(request, "This item quantity was updated.")
            return redirect("core:order-summary")
        else:
            messages.info(request, "This item was not in your cart")
            return redirect("core:product", slug=slug)
    else:
        messages.info(request, "You do not have an active order")
        return redirect("core:product", slug=slug)


def get_coupon(request, code):
    try:
        coupon = Coupon.objects.get(code=code)
        return coupon
    except ObjectDoesNotExist:
        messages.info(request, "This coupon does not exist")
        return redirect("core:checkout")


class AddCouponView(View):
    def post(self, *args, **kwargs):
        form = CouponForm(self.request.POST or None)
        if form.is_valid():
            try:
                code = form.cleaned_data.get('code')
                order = Order.objects.get(
                    user=self.request.user, ordered=False)
                order.coupon = get_coupon(self.request, code)
                order.save()
                messages.success(self.request, "Successfully added coupon")
                return redirect("core:checkout")
            except ObjectDoesNotExist:
                messages.info(self.request, "You do not have an active order")
                return redirect("core:checkout")


class RequestRefundView(View):
    def get(self, *args, **kwargs):
        form = RefundForm()
        context = {
            'form': form
        }
        return render(self.request, "request_refund.html", context)

    def post(self, *args, **kwargs):
        form = RefundForm(self.request.POST)
        if form.is_valid():
            ref_code = form.cleaned_data.get('ref_code')
            message = form.cleaned_data.get('message')
            email = form.cleaned_data.get('email')
            # edit the order
            try:
                order = Order.objects.get(ref_code=ref_code)
                order.refund_requested = True
                order.save()

                # store the refund
                refund = Refund()
                refund.order = order
                refund.reason = message
                refund.email = email
                refund.save()

                messages.info(self.request, "Your request was received.")
                return redirect("core:request-refund")

            except ObjectDoesNotExist:
                messages.info(self.request, "This order does not exist.")
                return redirect("core:request-refund")


class BlogList(generic.ListView):
    queryset = Blog.objects.filter(status=1).order_by('-created_on')
    template_name = 'cyrus/blog.html'


class BlogDetail(generic.DetailView):
    model = Blog
    template_name = 'cyrus/blog_details.html'

class Service(generic.TemplateView):
    template_name = 'cyrus/services.html'

class About(generic.TemplateView):
    template_name = 'cyrus/about.html'

class ImageGallery(generic.TemplateView):
    model = Gallery
    template_name = 'cyrus/gallery.html'

class Apply(generic.TemplateView):
    template_name = 'cyrus/apply.html'

class App(generic.TemplateView):
    template_name = 'cyrus/thankyou.html'

class Contact(generic.TemplateView):
    template_name = 'cyrus/contact.html'
    
# session = stripe.checkout.Session.create(
#   success_url="https://loozeele-app.herokuapp.com/order/success",
#   success_url="https://loozeele-app.herokuapp.com/order/success?session_id={CHECKOUT_SESSION_ID}",
#   # other options...,
# )


# import os
# import stripe

# from flask import Flask, request, render_template_string

# app = Flask(__name__)

# # Set your secret key. Remember to switch to your live secret key in production.
# # See your keys here: https://dashboard.stripe.com/apikeys
# stripe.api_key = settings.STRIPE_SECRET_KEY

# @app.route('/order/success', methods=['GET'])
# def order_success():
#   session = stripe.checkout.Session.retrieve(request.args.get('session_id'))
#   customer = stripe.Customer.retrieve(session.customer)

#   return render_template_string('<html><body><h1>Thanks for your order, {{customer.name}}!</h1></body></html>', customer=customer)

# if __name__== '__main__':
#   app.run(port=4242)
# payments/views.py

class SuccessView(generic.TemplateView):
    template_name = 'success.html'


class CancelledView(generic.TemplateView):
    template_name = 'cancelled.html'


# class SearchResultsView(ListView):
#     model = Item
#     template_name = 'home.html'
    
#     def get_queryset(self):  # new
#         query = self.request.GET.get("q")
#         object_list = Item.objects.filter(
#             Q(title__icontains=query) | Q(label__icontains=query)
#         )
#         return object_list
from django.contrib.auth.models import User
from django.contrib.sessions.models import Session
from django.utils import timezone
from django.http import Http404


def get_all_logged_in_users():
    # Query all non-expired sessions
    # use timezone.now() instead of datetime.now() in latest versions of Django
    sessions = Session.objects.filter(expire_date__gte=timezone.now())
    uid_list = []

    # Build a list of user ids from that query
    for session in sessions:
        data = session.get_decoded()
        uid_list.append(data.get('_auth_user_id', None))

    # Query all logged in users based on id list
    return User.objects.filter(id__in=uid_list)


class SearchView(ListView):
    model = Item
    template_name = "search.html"
    def get(self, request, *args, **kwargs):
        q = request.GET.get('q', '')
        self.results = Item.objects.filter(text__icontains=q, desc__icontains = q, title__icontains = q)
        return super().get(request, *args, **kwargs)

    def get_context_data(self,*args, **kwargs):
        context = super(SearchView, self).get_context_data(*args,**kwargs)
        context['items'] = Item.objects.all()
        return context

from django.contrib import admin
admin.site.login = login_required(admin.site.login)
from django.contrib.auth.decorators import login_required

admin.site.login = login_required(admin.site.login)
# def index(request):
#     users = User.objects.all()
#     context = {
#         'segment': 'index',
#         'users': users
#     }
#     return render(request, "pages/index.html", context)

def index(request):
  users = User.objects.all()
  orders = Order.objects.all()
  context = {
    'segment': 'index',
    'users': users,
    'orders': orders
  }
  if request.user.is_staff:
      return render(request, "pages/index.html", context)
  else:
      raise Http404()


from django.views import generic
from django.db.models import Sum, Q
from .models import Item
from datetime import date
from .filters import OrderFilter


from django.views import View
from datetime import date

from django.db.models import Sum
from django.shortcuts import render
from django.views import generic
from .models import Item, OrderItem, Order

class DashboardView(generic.TemplateView):
    template_name = 'admin/index.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        today = date.today()
        today_revenue = 0
        orders = Order.objects.filter(ordered_date__date=today, ordered=True)
        for order in orders:
            order_items = OrderItem.objects.filter(order=order)
            for order_item in order_items:
                item = order_item.item
                price = item.price if not item.discount_price else item.discount_price
                total_price = order_item.quantity * price
                today_revenue += total_price
        total_money_made = 0
        orders = Order.objects.filter(ordered=True)
        for order in orders:
            order_items = OrderItem.objects.filter(order=order)
            for order_item in order_items:
                item = order_item.item
                price = item.price if not item.discount_price else item.discount_price
                total_price = order_item.quantity * price
                total_money_made += total_price
        
        total_items_sold = 0
        orders = Order.objects.filter(ordered=True)
        for order in orders:
            order_items = OrderItem.objects.filter(order=order)
            for order_item in order_items:
                total_items_sold += order_item.quantity
        
        out_of_stock_items_count = 0
        items = Item.objects.all()

        for item in items:
            # Get the total quantity sold for this item across all orders
            total_quantity_sold = OrderItem.objects.filter(item=item, order__ordered=True).aggregate(total_quantity=Sum('quantity'))['total_quantity']

            if total_quantity_sold is None:
                total_quantity_sold = 0

            # Calculate the available quantity
            available_quantity = item.quantity - total_quantity_sold if item.quantity else 0

            if available_quantity <= 0:
                out_of_stock_items_count += 1

        context['out_of_stock_items_count'] = out_of_stock_items_count
        # ... other context data ...

        context['total_items_sold'] = total_items_sold

        context['total_money_made'] = total_money_made

        context['today_revenue'] = today_revenue
        # ... other context data ...

        return context




import requests
from django.http import JsonResponse


def get_paystack_transactions(request):
    # Set your Paystack API key
    api_key = "sk_live_ab3832c3b9fc0b1c655e1145f2d15ba234947589"

    # Make a GET request to Paystack API to fetch the transactions
    url = "https://api.paystack.co/transaction"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    response = requests.get(url, headers=headers)

    # Check if the request was successful
    if response.status_code == 200:
        data = response.json()
        transactions = data['data']

        # Extract the desired fields from each transaction
        processed_transactions = []
        for transaction in transactions:
            processed_transaction = {
                'amount': transaction['amount'] / 100,  # Convert amount from kobo to naira
                'customer': transaction['customer']['email'],
                'reference': transaction['reference'],
                'channel': transaction['channel'],
                'paid_on': transaction['paid_at']
            }
            processed_transactions.append(processed_transaction)

        # Return the processed transactions as JSON response
        return JsonResponse({'transactions': processed_transactions})
    else:
        return JsonResponse({'error': 'Failed to fetch transactions'}, status=500)


def show_transactions(request):
    return render(request, 'pages/transactions.html')
# Components
# @login_required(login_url='/accounts/login/')
# def bc_button(request):
#   context = {
#     'parent': 'basic_components',
#     'segment': 'button'
#   }
#   return render(request, "pages/components/bc_button.html", context)

# @login_required(login_url='/accounts/login/')
# def bc_badges(request):
#   context = {
#     'parent': 'basic_components',
#     'segment': 'badges'
#   }
#   return render(request, "pages/components/bc_badges.html", context)

# @login_required(login_url='/accounts/login/')
# def bc_breadcrumb_pagination(request):
#   context = {
#     'parent': 'basic_components',
#     'segment': 'breadcrumbs_&_pagination'
#   }
#   return render(request, "pages/components/bc_breadcrumb-pagination.html", context)

# @login_required(login_url='/accounts/login/')
# def bc_collapse(request):
#   context = {
#     'parent': 'basic_components',
#     'segment': 'collapse'
#   }
#   return render(request, "pages/components/bc_collapse.html", context)

# @login_required(login_url='/accounts/login/')
# def bc_tabs(request):
#   context = {
#     'parent': 'basic_components',
#     'segment': 'navs_&_tabs'
#   }
#   return render(request, "pages/components/bc_tabs.html", context)

# @login_required(login_url='/accounts/login/')
# def bc_typography(request):
#   context = {
#     'parent': 'basic_components',
#     'segment': 'typography'
#   }
#   return render(request, "pages/components/bc_typography.html", context)

# @login_required(login_url='/accounts/login/')
# def icon_feather(request):
#   context = {
#     'parent': 'basic_components',
#     'segment': 'feather_icon'
#   }
#   return render(request, "pages/components/icon-feather.html", context)


# # Forms and Tables
# @login_required(login_url='/accounts/login/')
# def form_elements(request):
#   context = {
#     'parent': 'form_components',
#     'segment': 'form_elements'
#   }
#   return render(request, 'pages/form_elements.html', context)

# @login_required(login_url='/accounts/login/')
# def basic_tables(request):
#   context = {
#     'parent': 'tables',
#     'segment': 'basic_tables'
#   }
#   return render(request, 'pages/tbl_bootstrap.html', context)
def morris_chart(request):
  context = {
    'parent': 'chart',
    'segment': 'morris_chart'
  }
  if request.user.is_staff:
      return render(request, 'pages/chart-morris.html', context)
  else:
      raise Http404()

# Chart and Maps
@login_required(login_url='/accounts/login/')
# def morris_chart(request):
#   context = {
#     'parent': 'chart',
#     'segment': 'morris_chart'
#   }
#   if request.user.is_staff:
#       return render(request, "account/signup.html")
#   else:
#       raise Http404()
#   return render(request, 'pages/chart-morris.html', context)

@login_required(login_url='/accounts/login/')
def google_maps(request):
  context = {
    'parent': 'maps',
    'segment': 'google_maps'
  }
  return render(request, 'pages/map-google.html', context)

# Authentication
class UserRegistrationView(CreateView):
  template_name = 'accounts/auth-signup.html'
  form_class = RegistrationForm
  success_url = '/accounts/login/'

class UserLoginView(LoginView):
  template_name = 'accounts/auth-signin.html'
  form_class = LoginForm

class UserPasswordResetView(PasswordResetView):
  template_name = 'accounts/auth-reset-password.html'
  form_class = UserPasswordResetForm

class UserPasswrodResetConfirmView(PasswordResetConfirmView):
  template_name = 'accounts/auth-password-reset-confirm.html'
  form_class = UserSetPasswordForm

class UserPasswordChangeView(PasswordChangeView):
  template_name = 'accounts/auth-change-password.html'
  form_class = UserPasswordChangeForm

def logout_view(request):
  logout(request)
  return redirect('/accounts/login/')

@login_required(login_url='/accounts/login/')
def profile(request):
  context = {
    'segment': 'profile',
  }
  return render(request, 'pages/profile.html', context)

@login_required(login_url='/accounts/login/')
def sample_page(request):
  context = {
    'segment': 'sample_page',
  }
  return render(request, 'pages/sample-page.html', context)




from django.contrib.auth import get_user_model
User = get_user_model()
users = User.objects.all()
