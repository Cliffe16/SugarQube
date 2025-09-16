from django.contrib.auth.forms import UserCreationForm
from .models import CustomUser, KYC
from django import forms

class CustomUserCreationForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = CustomUser
        fields = UserCreationForm.Meta.fields + ('first_name', 'last_name', 'email', 'phone_number')
        
class KYCForm(forms.ModelForm):
    class Meta:
        model = KYC
        fields = ['kra_pin', 'certificate_of_incorporation', 'tax_compliance_certificate', 'cr12_form', 'business_permit']