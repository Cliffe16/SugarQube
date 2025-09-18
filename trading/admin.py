from django.contrib import admin
from .models import SugarListing, Order

@admin.register(SugarListing)
class SugarListingAdmin(admin.ModelAdmin):
    list_display = ['sugar_type', 'company_name', 'origin', 'price_per_bag', 'quantity_available', 'minimum_order_quantity']
    list_display_links = ['sugar_type', 'company_name', 'origin']
    list_filter = ['sugar_type', 'origin', 'seller__user__company_name']
    search_fields = ['seller__user__company_name', 'sugar_type', 'origin', 'specifications']
    
    def company_name(self, obj):
        if obj.seller:
            return obj.seller.user.company_name
        return "N/A"
    company_name.short_description = 'Company Name'
    

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['id', 'buyer', 'listing', 'quantity', 'total_price', 'status', 'created_at']
    list_filter = ['status', 'created_at']
    search_fields = ['buyer__username', 'listing__sugar_type']
    readonly_fields = ['total_price', 'created_at']