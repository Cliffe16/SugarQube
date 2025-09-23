from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser, KYC, Seller
from market.models import SugarListing

class KYCInline(admin.StackedInline):
    model = KYC
    can_delete = False
    verbose_name_plural = 'KYC Documents'
    extra = 0

@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    inlines = (KYCInline,)
    list_display = ['username', 'email', 'first_name', 'last_name', 'is_verified_buyer', 'is_seller', 'is_staff']
    list_filter = ['is_verified_buyer', 'is_seller', 'is_staff', 'is_superuser', 'is_active', 'date_joined']
    fieldsets = UserAdmin.fieldsets + (
        ('Additional Info', {'fields': ('is_verified_buyer', 'is_seller', 'company_name')}),
    )

    def save_model(self, request, obj, form, change):
        """
        When a user is marked as a seller, automatically create their seller profile.
        """
        super().save_model(request, obj, form, change)
        if obj.is_seller:
            Seller.objects.get_or_create(user=obj)
        else:
            # If the is_seller box is unchecked, you may want to remove the seller profile
            Seller.objects.filter(user=obj).delete()

@admin.register(KYC)
class KYCAdmin(admin.ModelAdmin):
    list_display = ['user', 'is_approved']
    list_filter = ['is_approved']

@admin.register(Seller)
class SellerAdmin(admin.ModelAdmin):
    list_display = ['user', 'company_name', 'available_listings_count']

    def company_name(self, obj):
        return obj.user.company_name
    company_name.short_description = 'Company Name'

    def available_listings_count(self, obj):
        return SugarListing.objects.filter(seller=obj).count()
    available_listings_count.short_description = 'Available Listings'