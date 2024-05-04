from django.urls import path
from django.contrib.auth import views as auth_views
from . import views
from .views import (
    Fq,
    ItemDetailView,
    CheckoutView,
    HomeView,
    OrderSummaryView,
    add_to_cart,
    remove_from_cart,
    remove_single_item_from_cart,
    PaymentView,
    AddCouponView,
    IndexView,
    RequestRefundView,
    BlogList,
    BlogDetail,
    About,
    Contact,
    SearchView,
    get_paystack_transactions, 
    show_transactions, 
    UserLoginView ,
    Appad,

)

app_name = 'core'

urlpatterns = [
    path('shop/', HomeView.as_view(), name='shop'),
    path('', IndexView.as_view(), name='home'),
    path('gallery/',views.ImageGallery.as_view(),name='gallery'),
    path('apply/',views.Apply.as_view(),name='apply'),
    path('transactions/', show_transactions, name='transactions'),
    path('paystack/transactions/', get_paystack_transactions, name='paystack_transactions'),
    path('final-checkout/', views.final_checkout, name='f_checkout'),
    path('dashboard/', views.DashboardView.as_view(), name='dashboard'),
    path('accounts/login/', views.UserLoginView.as_view(), name='login'),
    path('accounts/logout/', views.logout_view, name='logout'),
    path('accounts/register/', views.UserRegistrationView.as_view(), name='register'),
    path('accounts/password-change/', views.UserPasswordChangeView.as_view(), name='password_change'),
    path('accounts/password-change-done/', auth_views.PasswordChangeDoneView.as_view(
        template_name='accounts/password_change_done.html'
    ), name="password_change_done" ),
    path('accounts/password-reset/', views.UserPasswordResetView.as_view(), name='password_reset'),
    path('accounts/password-reset-confirm/<uidb64>/<token>/', 
        views.UserPasswrodResetConfirmView.as_view(), name='password_reset_confirm'),
    path('accounts/password-reset-done/', auth_views.PasswordResetDoneView.as_view(
        template_name='accounts/password_reset_done.html'
    ), name='password_reset_done'),
    path('accounts/password-reset-complete/', auth_views.PasswordResetCompleteView.as_view(
        template_name='accounts/password_reset_complete.html'
    ), name='password_reset_complete'),
    path('accounts/register/', views.UserRegistrationView.as_view(), name='register'),
    path('accounts/login/', views.UserLoginView.as_view(), name='login'),
    path('accounts/logout/', views.logout_view, name='logout'),
    path('accounts/password-change/', views.UserPasswordChangeView.as_view(), name='password_change'),
    path('accounts/password-change-done/', auth_views.PasswordChangeDoneView.as_view(
        template_name='accounts/auth-password-change-done.html'
    ), name="password_change_done"),
    path('accounts/password-reset/', views.UserPasswordResetView.as_view(), name='password_reset'),
    path('accounts/password-reset-confirm/<uidb64>/<token>/',
        views.UserPasswrodResetConfirmView.as_view(), name="password_reset_confirm"
    ),
    path('accounts/password-reset-done/', auth_views.PasswordResetDoneView.as_view(
        template_name='accounts/auth-password-reset-done.html'
    ), name='password_reset_done'),
    path('accounts/password-reset-complete/', auth_views.PasswordResetCompleteView.as_view(
        template_name='accounts/auth-password-reset-complete.html'
    ), name='password_reset_complete'),
    path('profile/', views.profile, name='profile'),
    path('userc/', views.user_profile_view, name='userc'),
    path('fg/', Fq.as_view(), name='fq'),
    path('sample-page/', views.sample_page, name='sample_page'),
    path("search/", SearchView.as_view(), name="search_results"),
    path('about/', About.as_view(), name='about'),
    path('app/', views.App.as_view(), name='app'),
    path('contact/', Contact.as_view(), name='contact'),
    path('checkout/', CheckoutView.as_view(), name='checkout'),
    path('order-summary/', OrderSummaryView.as_view(), name='order-summary'),
    path('product/<slug>/', ItemDetailView.as_view(), name='product'),
    path('add-to-cart/<slug>/', add_to_cart, name='add-to-cart'),
    path('add-coupon/', AddCouponView.as_view(), name='add-coupon'),
    path('remove-from-cart/<slug>/', remove_from_cart, name='remove-from-cart'),
    path('remove-item-from-cart/<slug>/', remove_single_item_from_cart,
         name='remove-single-item-from-cart'),
    path('payment/<payment_option>/', PaymentView.as_view(), name='payment'),
    path('request-refund/', RequestRefundView.as_view(), name='request-refund'),
    path('blog/', BlogList.as_view(), name='blog'),
    path('service/', views.Service.as_view(), name='service'),
    path('<slug:slug>/', BlogDetail.as_view(), name='blog_detail'),
    path('create_order/', views.create_order, name='create_order'),
    path('order_details/<int:order_id>/', views.order_details, name='order_details'),
    
    
]
