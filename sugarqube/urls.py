from django.contrib import admin
from django.urls import path, include
from users import views as user_views # We need to import the views directly now

urlpatterns = [
    path('admin/', admin.site.urls),

    # App URLs
    path('', include('dashboard.urls')),
    path('blog/', include('blog.urls')),
    path('trading/', include('trading.urls')),
    
    # Custom registration URL
    path('register/', user_views.register, name='register'),

    # All other authentication URLs (login, logout, password reset, etc.)
    # will be handled by django.contrib.auth.urls under the default 'accounts/' prefix.
    path('accounts/', include('django.contrib.auth.urls')),
]