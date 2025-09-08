from django.contrib import admin
from django.urls import path, include
# ... (other imports)

urlpatterns = [
    path('admin/', admin.site.urls),
    
    # ... (other URL patterns)
    path('accounts/', include('django.contrib.auth.urls')),
    
    # Add support app URLs
    path('support/', include('support.urls')),
]