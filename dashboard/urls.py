from django.urls import path
from . import views
from . import prediction_models

urlpatterns = [
    path('', views.market_trends, name='market_trends'),
    path('api/predict/', prediction_models.api_predict, name='api_predict'),

]