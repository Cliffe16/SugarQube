from django.contrib import admin
from .models import SupportTicket
from users.models import CustomUser

@admin.register(SupportTicket)
class SupportTicketAdmin(admin.ModelAdmin):
    list_display = ('ticket_id', 'get_user', 'subject', 'status', 'created_at')
    list_filter = ('status', 'created_at')
    search_fields = ('ticket_id', 'subject')
    readonly_fields = ('ticket_id', 'created_at')

    def get_queryset(self, request):
        # Start with the base queryset from the correct database
        qs = super().get_queryset(request).using('default')
        # Get a list of unique user IDs from the tickets
        user_ids = list(qs.values_list('user_id', flat=True).distinct())
        # Fetch all related user objects in a single query from the 'credentials' db
        users = CustomUser.objects.using('credentials').filter(pk__in=user_ids)
        # Create a dictionary for easy lookup: {user_id: user_username}
        user_map = {user.pk: user.username for user in users}
        # Attach the username to each ticket object
        for ticket in qs:
            ticket.user_username = user_map.get(ticket.user_id, "N/A")
        return qs

    def get_user(self, obj):
        return getattr(obj, 'user_username', "N/A")
    get_user.short_description = 'User'
    get_user.admin_order_field = 'user__username'