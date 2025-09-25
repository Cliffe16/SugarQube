from django.urls import path
from . import views

urlpatterns = [
    path('api/get/', views.get_notifications, name='get_notifications'),
    path('api/mark-read/<int:notification_id>/', views.mark_as_read, name='mark_notification_as_read'),
]