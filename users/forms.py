from django.contrib.auth.forms import UserCreationForm, PasswordChangeForm
from .models import CustomUser, KYC
from django import forms
from django.core.exceptions import ValidationError
import os

class CustomUserCreationForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = CustomUser
        fields = UserCreationForm.Meta.fields + ('first_name', 'last_name', 'email', 'phone_number', 'company_name')

class CustomPasswordChangeForm(PasswordChangeForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for fieldname, placeholder in [
            ('old_password', 'Current Password'),
            ('new_password1', 'New Password'),
            ('new_password2', 'Repeat New Password')
        ]:
            self.fields[fieldname].widget.attrs = {
                'class': 'appearance-none rounded-md relative block w-full px-3 py-2 border border-gray-300 placeholder-gray-500 text-gray-900 focus:outline-none focus:ring-green-500 focus:border-green-500 sm:text-sm',
                'placeholder': placeholder
            }
            self.fields[fieldname].help_text = ''
            self.fields[fieldname].label = ''


class ChangePhoneNumberForm(forms.ModelForm):
    class Meta:
        model = CustomUser
        fields = ['phone_number']
        widgets = {
            'phone_number': forms.TextInput(attrs={
                'class': 'appearance-none rounded-md relative block w-full px-3 py-2 border border-gray-300 placeholder-gray-500 text-gray-900 focus:outline-none focus:ring-green-500 focus:border-green-500 sm:text-sm',
                'placeholder': 'e.g., +254712345678'
            })
        }
        labels = {
            'phone_number': ''
        }

        
class KYCForm(forms.ModelForm):
    class Meta:
        model = KYC
        fields = ['tax_pin', 'certificate_of_incorporation', 'tax_compliance_certificate', 'cr12_form', 'business_permit']
        labels = {
            'tax_pin': 'Tax PIN Certificate',
            'certificate_of_incorporation': 'Certificate of Incorporation',
            'tax_compliance_certificate': 'Tax Compliance Certificate',
            'cr12_form': 'CR-12 Form',
            'business_permit': 'Business Permit',
        }
        widgets = {
            'tax_pin': forms.FileInput(attrs={'class': 'block w-full text-sm text-gray-500 file:mr-4 file:py-2 file:px-4 file:rounded-full file:border-0 file:text-sm file:font-semibold file:bg-green-100 file:text-green-700 hover:file:bg-green-200'}),
            'certificate_of_incorporation': forms.FileInput(attrs={'class': 'block w-full text-sm text-gray-500 file:mr-4 file:py-2 file:px-4 file:rounded-full file:border-0 file:text-sm file:font-semibold file:bg-green-100 file:text-green-700 hover:file:bg-green-200'}),
            'tax_compliance_certificate': forms.FileInput(attrs={'class': 'block w-full text-sm text-gray-500 file:mr-4 file:py-2 file:px-4 file:rounded-full file:border-0 file:text-sm file:font-semibold file:bg-green-100 file:text-green-700 hover:file:bg-green-200'}),
            'cr12_form': forms.FileInput(attrs={'class': 'block w-full text-sm text-gray-500 file:mr-4 file:py-2 file:px-4 file:rounded-full file:border-0 file:text-sm file:font-semibold file:bg-green-100 file:text-green-700 hover:file:bg-green-200'}),
            'business_permit': forms.FileInput(attrs={'class': 'block w-full text-sm text-gray-500 file:mr-4 file:py-2 file:px-4 file:rounded-full file:border-0 file:text-sm file:font-semibold file:bg-green-100 file:text-green-700 hover:file:bg-green-200'}),
        }

    def clean_file(self, field_name):
        file = self.cleaned_data.get(field_name, False)
        if file:
            ext = os.path.splitext(file.name)[1]
            if not ext.lower() in ['.pdf']:
                raise ValidationError("Only PDF files are accepted.")
        return file

    def clean_kra_pin(self):
        return self.clean_file('tax_pin')

    def clean_certificate_of_incorporation(self):
        return self.clean_file('certificate_of_incorporation')

    def clean_tax_compliance_certificate(self):
        return self.clean_file('tax_compliance_certificate')

    def clean_cr12_form(self):
        return self.clean_file('cr12_form')

    def clean_business_permit(self):
        return self.clean_file('business_permit')