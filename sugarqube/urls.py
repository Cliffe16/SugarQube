from django.contrib import admin
from django.urls import path, include
from django.views.generic import TemplateView
from django.conf import settings
from django.conf.urls.static import static
from users import views as user_views
from dashboard import views as dashboard_views  
from django.shortcuts import redirect

def root_redirect(request):
    """Root URL handler - shows landing page or redirects to dashboard"""
    if request.user.is_authenticated:
        return redirect('market_trends')
    else:
        from django.shortcuts import render
        return render(request, 'landing_page.html')

urlpatterns = [
    path('admin/', admin.site.urls),
    
    # Root URL - handles authenticated vs non-authenticated users
    path('', root_redirect, name='home'),
    
    path('landing-chart-data/', dashboard_views.landing_chart_data, name='landing_chart_data'),
    
    # Dashboard URLs (with 'dashboard/' prefix)
    path('dashboard/', include('dashboard.urls')),
    path('blog/', include('blog.urls')),
    path('trading/', include('trading.urls')),
    
    # Authentication URLs
    path('register/', user_views.register, name='register'),
    path('verification/', user_views.kyc_upload, name='verification'),
    path('accounts/', include('django.contrib.auth.urls')),
]

# CKEditor URLs
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
