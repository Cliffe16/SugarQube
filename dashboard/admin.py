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
        last_price = SugarPrice.objects.order_by('-date').first()

        # Save the new price object
        super().save_model(request, obj, form, change)

        # Check if the price has changed or if this is the first price entry
        if not last_price or obj.amount != last_price.amount:
            try:
                User = get_user_model()
                all_users = User.objects.using('credentials').all()

                message = f"Market Update: The price of sugar is now {obj.amount} on {obj.date.strftime('%B %d')}."

                notifications_to_create = [
                    Notification(user=user, message=message, link=reverse('market_trends'))
                    for user in all_users
                ]

                if notifications_to_create:
                    Notification.objects.using('credentials').bulk_create(notifications_to_create)

            except Exception as e:
                print(f"Error creating price shift notifications: {e}")