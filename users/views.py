from django.shortcuts import render, redirect
from django.contrib import messages
from .forms import CustomUserCreationForm  # Import the new form

def register(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)  # Use the new form
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            messages.success(request, f'Account created for {username}! You can now log in.')
            return redirect('login')
    else:
        form = CustomUserCreationForm()  # Use the new form
    return render(request, 'registration/register.html', {'form': form})