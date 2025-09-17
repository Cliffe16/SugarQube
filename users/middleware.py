from django.shortcuts import redirect
from django.urls import reverse

class KYCVerificationMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.user.is_authenticated and not request.user.is_verified_buyer:
            # Allow access to profile, logout, and admin
            if request.path not in [reverse('profile'), reverse('logout'), '/admin/', '/admin/login/']:
                return redirect('profile')
        response = self.get_response(request)
        return response