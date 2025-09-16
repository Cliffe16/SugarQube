from django.contrib.auth.forms import UserCreationForm
from .models import CustomUser, KYC
from django import forms
from django.core.exceptions import ValidationError
import os

class CustomUserCreationForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = CustomUser
        fields = UserCreationForm.Meta.fields + ('first_name', 'last_name', 'email', 'phone_number', 'company_name')

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