from django.shortcuts import render, redirect
from django.contrib import messages
from .forms import CustomUserCreationForm, KYCForm, ChangePhoneNumberForm, CustomPasswordChangeForm
from .models import KYC, Seller
from django.contrib.auth.decorators import login_required
from django.core.mail import send_mail
from django.conf import settings
from django.contrib.auth import update_session_auth_hash, logout

@login_required
def profile(request):
    try:
        kyc_instance = request.user.kyc
    except KYC.DoesNotExist:
        kyc_instance = None

    if request.method == 'POST':
        # Check which form is being submitted
        form_type = request.POST.get('form_type')

        if form_type == 'kyc_form':
            instance = kyc_instance if kyc_instance else None
            kyc_form = KYCForm(request.POST, request.FILES, instance=instance)
            if kyc_form.is_valid():
                kyc = kyc_form.save(commit=False)
                kyc.user = request.user
                kyc.is_approved = False  # Explicitly set to pending on new upload/update
                kyc.save()
                messages.success(request, 'KYC documents uploaded successfully. They are now pending review.')
                return redirect('profile') # Redirect to refresh the page and show the new status
            else:
                messages.error(request, 'Please correct the errors in the KYC form.')
        
        elif form_type == 'password_form':
            password_form = CustomPasswordChangeForm(request.user, request.POST)
            if password_form.is_valid():
                user = password_form.save()
                update_session_auth_hash(request, user)  # Important!
                messages.success(request, 'Your password was successfully updated!')
                return redirect('profile') # Redirect after successful change
            else:
                messages.error(request, 'Please correct the password errors.')

        elif form_type == 'phone_form':
            phone_form = ChangePhoneNumberForm(request.POST, instance=request.user)
            if phone_form.is_valid():
                phone_form.save()
                messages.success(request, 'Your phone number has been updated.')
                return redirect('profile') # Redirect after successful change
            else:
                messages.error(request, 'Please correct the phone number errors.')
        
        # If any form has errors, it will fall through and re-render with the errors
    
    else: # GET request
        kyc_form = KYCForm(instance=kyc_instance)
        password_form = CustomPasswordChangeForm(request.user)
        phone_form = ChangePhoneNumberForm()

    context = {
        'kyc_instance': kyc_instance,
        'form': kyc_form if 'kyc_form' in request.POST else KYCForm(instance=kyc_instance),
        'password_form': password_form if 'password_form' in request.POST else CustomPasswordChangeForm(request.user),
        'phone_form': phone_form if 'phone_form' in request.POST else ChangePhoneNumberForm(instance=request.user)
    }
    return render(request, 'registration/profile.html', context)


def register(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            messages.success(request, f'Account successfully created for {username}! You can now log in to SugarQube.')
            return redirect('login')
    else:
        form = CustomUserCreationForm()
    return render(request, 'registration/register.html', {'form': form})

@login_required
def kyc_upload(request):
    # This view can now redirect to the main profile page
    return redirect('profile')

@login_required
def request_seller_account(request):
    if request.method == 'POST':
        user = request.user
        if user.is_verified_buyer:
            # Send email to admin
            subject = 'Seller Account Request'
            message = f'User {user.username} (email: {user.email}) has requested to become a seller.'
            from_email = settings.DEFAULT_FROM_EMAIL
            recipient_list = [admin[1] for admin in settings.ADMINS]
            send_mail(subject, message, from_email, recipient_list)
            messages.success(request, 'Your request to become a seller has been sent to the admin for approval.')
        else:
            messages.error(request, 'Only verified buyers can request a seller account.')
    return redirect('profile')

@login_required
def change_phone_number(request):
    if request.method == 'POST':
        form = ChangePhoneNumberForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Your phone number has been updated.')
            return redirect('profile')
    else:
        form = ChangePhoneNumberForm(instance=request.user)
    return render(request, 'registration/change_phone_number.html', {'form': form})

@login_required
def terminate_account(request):
    if request.method == 'POST':
        user = request.user
        choice = request.POST.get('termination_choice')

        if user.is_seller and user.is_verified_buyer and choice == 'seller':
            # Terminate only the seller account
            user.is_seller = False
            user.save()
            Seller.objects.filter(user=user).delete()
            messages.success(request, 'Your seller account has been successfully terminated.')
            return redirect('profile')
        else:
            # Terminate the entire account
            user.is_active = False
            user.save()
            logout(request)
            messages.success(request, 'Your account has been successfully terminated.')
            return redirect('home')

    return render(request, 'registration/terminate_account.html')