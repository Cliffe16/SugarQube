from django.contrib.auth.models import AbstractUser
from django.db import models

class CustomUser(AbstractUser):
    is_verified_buyer = models.BooleanField(default=False)
    company_details = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.username