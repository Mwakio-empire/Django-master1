from django.conf import settings
from django.conf.urls.static import static
from django.urls import path
from . import views
from django.contrib.auth import views as auth_views
from .views import verify_email, order_detail

urlpatterns = [
    path('', views.index, name='index'),
    path('cart/add/<uuid:product_id>/', views.add_to_cart, name='add_to_cart'),
    
    path('cart/remove/<uuid:product_id>/', views.remove_from_cart, name='remove_from_cart'),
    path('cart/update/<uuid:product_id>/', views.update_cart_item, name='update_cart_item'),
    path('signup/', views.signup_view, name='signup'),
    path('product/<uuid:product_id>/', views.product_detail, name='product_detail'),

#activating the account after signup
    path('activate/<uidb64>/<token>/', views.activate_account, name='activate_account'),


    path('order/<uuid:order_id>/', views.order_detail, name='order_detail'),

    path('cart/', views.view_cart, name='view_cart'),    
    
    path('checkout/', views.checkout, name='checkout'),

    
    path('cart/', views.view_cart, name='view_cart'),
    
    path('products/', views.product_list, name='product_list'),
    path('contact/', views.contact, name='contact'),
    path('privacy_policy/', views.privacy_policy, name='privacy_policy'),
    path('terms_of_service/', views.terms_of_service, name='terms_of_service'),
    path('faqs/', views.faqs, name='faqs'),
    path('subscribe_newsletter/', views.subscribe_newsletter, name='subscribe_newsletter'),
    path('about/', views.about, name='about'),
    path('rate-product/<uuid:product_id>/', views.rate_product, name='rate_product'),
    path('product/<uuid:product_id>/add_comment/', views.add_comment, name='add_comment'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.custom_logout_view, name='logout'),
    
    path('verify/<str:code>/', verify_email, name='verify_email'),  # URL to handle email verification
    path('profile/', views.profile, name='profile'),
    path('update_profile/', views.update_profile, name='update_profile'),
    path('order/<uuid:order_id>/', order_detail, name='order_detail'),
    path('mpesa/callback/', views.mpesa_callback, name='mpesa_callback'),

    # Password reset URLs
    path('password_reset/', auth_views.PasswordResetView.as_view(template_name='registration/password_reset.html'), name='password_reset'),
    path('password_reset/done/', auth_views.PasswordResetDoneView.as_view(template_name='registration/password_reset_done.html'), name='password_reset_done'),
    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(template_name='registration/password_reset_confirm.html'), name='password_reset_confirm'),
    path('reset/done/', auth_views.PasswordResetCompleteView.as_view(template_name='registration/password_reset_complete.html'), name='password_reset_complete'),

    # Include two-factor URLs here if needed.
]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
