from django.urls import path
from . import views
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('profile/', views.profile, name='profile'),
    path('request_seller_account/', views.request_seller_account, name='request_seller_account'),
    path('terminate/', views.terminate_account, name='terminate_account'),
]