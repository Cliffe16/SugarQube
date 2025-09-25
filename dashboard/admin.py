from django.contrib import admin
from django.urls import reverse
from django.contrib.auth import get_user_model
from .models import SugarPrice
from notifications.models import Notification

@admin.register(SugarPrice)
class SugarPriceAdmin(admin.ModelAdmin):
    list_display = ('date', 'amount', 'rate')
    list_filter = ('date',)
    ordering = ('-date',)

    def save_model(self, request, obj, form, change):
        # First, save the object. The router correctly sends this to 'sugarprices'.
        super().save_model(request, obj, form, change)

        # Now, create notifications.
        if not change: # Only on creation
            try:
                User = get_user_model()
                # Explicitly query the 'default' database for users.
                all_users = User.objects.using('default').all()

                message = f"Market Update: The price of sugar is now KES {obj.amount} on {obj.date.strftime('%B %d')}."

                notifications_to_create = [
                    Notification(user=user, message=message, link=reverse('market_trends'))
                    for user in all_users
                ]

                if notifications_to_create:
                    # *** THE CORE FIX ***
                    # Explicitly tell bulk_create to use the 'default' database.
                    Notification.objects.using('default').bulk_create(notifications_to_create)

            except Exception as e:
                # The error message will now be more informative if something else goes wrong.
                print(f"Error creating price shift notifications: {e}")