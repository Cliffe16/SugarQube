from django.contrib import admin
from .models import SugarListing, Order

@admin.register(SugarListing)
class SugarListingAdmin(admin.ModelAdmin):
    list_display = ['seller', 'sugar_type', 'origin', 'price_per_bag', 'quantity_available', 'minimum_order_quantity']
    list_display_links = ['seller', 'sugar_type', 'origin']
    list_filter = ['sugar_type', 'origin', 'seller']
    search_fields = ['seller__user__username', 'sugar_type', 'origin', 'specifications']
    

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['id', 'buyer', 'listing', 'quantity', 'total_price', 'status', 'created_at']
    list_filter = ['status', 'created_at']
    search_fields = ['buyer__username', 'listing__sugar_type']
    readonly_fields = ['total_price', 'created_at']