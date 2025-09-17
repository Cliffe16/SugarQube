from django.shortcuts import render, redirect
from django.contrib import messages
from .forms import CustomUserCreationForm, KYCForm
from .models import KYC
from django.contrib.auth.decorators import login_required

@login_required
def profile(request):
    return render(request, 'registration/profile.html')

def register(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            messages.success(request, f'Account created for {username}! You can now log in and upload your KYC documents for verification.')
            return redirect('login')
    else:
        form = CustomUserCreationForm()
    return render(request, 'registration/register.html', {'form': form})

@login_required
def kyc_upload(request):
    # This view will now be used by logged-in users to upload their documents
    if request.method == 'POST':
        # Check if a KYC profile already exists
        try:
            kyc_instance = request.user.kyc
            form = KYCForm(request.POST, request.FILES, instance=kyc_instance)
        except KYC.DoesNotExist:
            form = KYCForm(request.POST, request.FILES)

        if form.is_valid():
            kyc = form.save(commit=False)
            kyc.user = request.user
            kyc.save()
            messages.success(request, 'KYC documents uploaded successfully. Please wait for admin approval.')
            return redirect('profile')
    else:
        try:
            kyc_instance = request.user.kyc
            form = KYCForm(instance=kyc_instance)
        except:
            form = KYCForm()
            
    return render(request, 'registration/kyc_upload.html', {'form': form})