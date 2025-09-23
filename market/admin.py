from django.contrib import admin
from .models import SugarListing, Order
from users.models import CustomUser, Seller

@admin.register(SugarListing)
class SugarListingAdmin(admin.ModelAdmin):
    list_display = ['sugar_type', 'get_company_name', 'origin', 'price_per_bag', 'quantity_available', 'minimum_order_quantity']
    list_display_links = ['sugar_type', 'get_company_name', 'origin']
    list_filter = ['sugar_type', 'origin']
    search_fields = ['sugar_type', 'origin', 'specifications']

    def get_queryset(self, request):
        # Start with the base queryset from the correct database
        qs = super().get_queryset(request).using('sugarprices')
        # Get a list of unique seller IDs from the listings
        seller_ids = list(qs.values_list('seller_id', flat=True).distinct())
        # Fetch all related seller objects in a single query from the 'credentials' db
        sellers = Seller.objects.using('credentials').filter(pk__in=seller_ids).select_related('user')
        # Create a dictionary for easy lookup: {seller_id: company_name}
        seller_map = {seller.pk: seller.user.company_name for seller in sellers}
        # Attach the company name to each listing object
        for listing in qs:
            listing.company_name = seller_map.get(listing.seller_id, "N/A")
        return qs

    def get_company_name(self, obj):
        return getattr(obj, 'company_name', "N/A")
    get_company_name.short_description = 'Company Name'
    get_company_name.admin_order_field = 'seller__user__company_name'

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'get_buyer_username', 'listing', 'quantity', 'total_price', 'status', 'created_at')
    list_filter = ('status', 'created_at')
    search_fields = ('listing__sugar_type',)
    readonly_fields = ('total_price', 'created_at')

    def get_queryset(self, request):
        # Start with the base queryset from the correct database
        qs = super().get_queryset(request).using('sugarprices').select_related('listing')
        # Get a list of unique buyer IDs from the orders
        buyer_ids = list(qs.values_list('buyer_id', flat=True).distinct())
        # Fetch all related buyer objects in a single query from the 'credentials' db
        buyers = CustomUser.objects.using('credentials').filter(pk__in=buyer_ids)
        # Create a dictionary for easy lookup: {buyer_id: buyer_username}
        buyer_map = {buyer.pk: buyer.username for buyer in buyers}
        # Attach the buyer's username to each order object
        for order in qs:
            order.buyer_username = buyer_map.get(order.buyer_id, "N/A")
        return qs

    def get_buyer_username(self, obj):
        return getattr(obj, 'buyer_username', "N/A")
    get_buyer_username.short_description = 'Buyer'
    get_buyer_username.admin_order_field = 'buyer__username'