from django.db.models.signals import post_save
from django.dispatch import receiver
from django.urls import reverse
from django.contrib.auth import get_user_model
from .models import SugarPrice
from notifications.models import Notification

@receiver(post_save, sender=SugarPrice)
def price_shift_notification(sender, instance, created, **kwargs):
    """
    Creates a notification for all users when a new SugarPrice is created.
    """
    if created:
        User = get_user_model()
        all_users = User.objects.all()
        
        message = f"Market Update: The price of sugar is now KES {instance.amount} on {instance.date.strftime('%B %d')}."
        
        # Create a notification for every user
        for user in all_users:
            Notification.objects.create(
                user=user,
                message=message,
                link=reverse('market_trends') # Link to the trends page
            )