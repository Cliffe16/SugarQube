from django.db.models.signals import pre_save
from django.dispatch import receiver
from django.contrib.auth import get_user_model
from .models import SugarPrice
from notifications.models import Notification

@receiver(pre_save, sender=SugarPrice)
def exchange_rate_shift_notification(sender, instance, **kwargs):
    """
    Triggers a notification when the 'rate' field is updated.
    """
    if instance.pk:
        try:
            original = sender.objects.get(pk=instance.pk)
            if original.rate != instance.rate:
                User = get_user_model()
                all_users = User.objects.all()
                message = f"Currency Update: The exchange rate has been updated to {instance.rate}."

                notifications_to_create = [
                    Notification(user=user, message=message) for user in all_users
                ]

                if notifications_to_create:
                    Notification.objects.bulk_create(notifications_to_create)
        except sender.DoesNotExist:
            pass