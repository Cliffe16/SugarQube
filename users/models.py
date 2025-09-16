from django.contrib.auth.models import AbstractUser
from django.db import models

class CustomUser(AbstractUser):
    is_verified_buyer = models.BooleanField(default=False)
    company_name = models.CharField(max_length=255, blank=True, null=True)
    phone_number = models.CharField(max_length=20, blank=True, null=True)
    is_seller = models.BooleanField(default=False)

    def __str__(self):
        return self.username

class KYC(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name='kyc')
    tax_pin = models.FileField(upload_to='kyc_documents/')
    certificate_of_incorporation = models.FileField(upload_to='kyc_documents/')
    tax_compliance_certificate = models.FileField(upload_to='kyc_documents/')
    cr12_form = models.FileField(upload_to='kyc_documents/')
    business_permit = models.FileField(upload_to='kyc_documents/')
    is_approved = models.BooleanField(default=False)

    def __str__(self):
        return f"KYC for {self.user.username}"

class Seller(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name='seller_profile')

    def __str__(self):
        return self.user.username