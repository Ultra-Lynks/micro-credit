from django.contrib import admin

from .models import Item, OrderItem, Order, Payment, Coupon, Refund, Address, UserProfile, Blog, UserProfile, Header
from .models  import  Payments, UserWallet



def make_refund_accepted(modeladmin, request, queryset):
    queryset.update(refund_requested=False, refund_granted=True)


make_refund_accepted.short_description = 'Update orders to refund granted'

class  PaymentsAdmin(admin.ModelAdmin):
    list_display  = ["id", "ref", 'amount', "verified", "date_created"]


class  ItemAdmin(admin.ModelAdmin):
    list_display  = ["title", "price", 'discount_price', "category", "sales_category","label", "slug", 'description', "image", "preview1", "preview2", 'preview3',
                     ]
    list_filter = ['title',
                    'price',
                    'category',
                    'description',
                    'discount_price']
    search_fields = [
        'title',
        'category'
        'price'
    ]

class OrderAdmin(admin.ModelAdmin):
    list_display = ['user',
                    'ordered',
                    'get_status_display',  # Display human-readable status
                    'shipping_address',
                    'billing_address',
                    'payment',
                    'coupon'
                    ]
    list_display_links = [
        'user',
        'shipping_address',
        'billing_address',
        'payment',
        'coupon'
    ]
    list_filter = ['ordered',
                   'status',  # Filter by status instead of individual fields
                   ]
    search_fields = [
        'user__username',
        'ref_code'
    ]
    actions = [make_refund_accepted]  # Assuming make_refund_accepted is defined



class AddressAdmin(admin.ModelAdmin):
    list_display = [
        'user',
        'street_address',
        'apartment_address',
        'country',
        'zip',
        'default'
    ]
    list_filter = ['default', 'country']
    search_fields = ['user', 'street_address', 'apartment_address', 'zip']


class BlogAdmin(admin.ModelAdmin):
    list_display = ('title', 'slug', 'status', 'created_on')
    list_filter = ("status",)
    search_fields = ['title', 'content']
    prepopulated_fields = {'slug': ('title',)}

@admin.register(Header)
class HeaderAdmin(admin.ModelAdmin):
    list_display = ['title', 'category', 'slug']
    search_fields = ['title', 'slug']
    prepopulated_fields = {'slug': ('title',)}  # Auto-generate slug based on title

# Register any other models or admin classes if needed



@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ['user','image', 'stripe_customer_id', 'one_click_purchasing']
    search_fields = ['user__username', 'stripe_customer_id']

admin.site.register(Item,ItemAdmin)
admin.site.register(OrderItem)
admin.site.register(Order, OrderAdmin)
admin.site.register(Payment)
admin.site.register(Coupon)
admin.site.register(Refund)
admin.site.register(Address, AddressAdmin)
admin.site.register(Blog, BlogAdmin)
admin.site.register(Payments, PaymentsAdmin)
admin.site.register(UserWallet)
