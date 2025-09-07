from django.urls import path
from . import views

urlpatterns = [
    path('', views.market_trends, name='market_trends'),
]