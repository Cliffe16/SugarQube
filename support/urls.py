from django.contrib import admin
from django.urls import path, include
from . import views

urlpatterns = [
    path('admin/', admin.site.urls),
    
    # ... (other URL patterns)
    path('accounts/', include('django.contrib.auth.urls')),
    
    # Add support app URLs
    path('', views.support_page, name='support_page'),
    path('submit/', views.submit_ticket, name='submit_ticket'),
]