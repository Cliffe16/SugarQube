from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser

@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    list_display = ['username', 'email', 'first_name', 'last_name', 'is_verified_buyer', 'is_staff']
    list_filter = ['is_verified_buyer', 'is_staff', 'is_superuser', 'is_active', 'date_joined']
    fieldsets = UserAdmin.fieldsets + (
        ('Additional Info', {'fields': ('is_verified_buyer', 'company_details')}),
    )