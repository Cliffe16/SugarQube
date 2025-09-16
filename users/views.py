from django.shortcuts import render, redirect
from django.contrib import messages
from .forms import CustomUserCreationForm, KYCForm
from django.contrib.auth.decorators import login_required

def register(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)  
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            messages.success(request, f'Account created for {username}! You can now log in.')
            return redirect('login')
    else:
        form = CustomUserCreationForm()  
    return render(request, 'registration/register.html', {'form': form})

@login_required
def kyc_upload(request):
    if request.method == 'POST':
        form = KYCForm(request.POST, request.FILES)
        if form.is_valid():
            kyc = form.save(commit=False)
            kyc.user = request.user
            kyc.save()
            messages.success(request, 'KYC documents uploaded successfully. Please wait for admin approval.')
            return redirect('market_trends')
    else:
        form = KYCForm()
    return render(request, 'registration/kyc_upload.html', {'form': form})