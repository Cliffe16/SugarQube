from django.db import transaction
from django.db.models.signals import pre_save
from django.dispatch import receiver
from django.urls import reverse
from .models import CustomUser
from notifications.models import Notification

def create_verification_notification(user, message):
    """Creates a notification and lets the router handle the database."""
    # Remove .using('default') and let the router direct the query
    Notification.objects.create(
        user=user,
        message=message,
        link=reverse('profile')
    )

@receiver(pre_save, sender=CustomUser)
def user_verification_notification(sender, instance, **kwargs):
    """
    Triggers a notification when a user's verification status changes to True.
    """
    if instance.pk:
        try:
            # The user object is fetched from the 'credentials' db by the router
            original = sender.objects.get(pk=instance.pk)
            
            # Notify on becoming a verified buyer
            if not original.is_verified_buyer and instance.is_verified_buyer:
                message = "Congratulations! Your account has been verified as a buyer."
                transaction.on_commit(lambda: create_verification_notification(instance, message))
            
            # Notify on becoming a seller
            if not original.is_seller and instance.is_seller:
                message = "Congratulations! Your account has been approved as a seller."
                transaction.on_commit(lambda: create_verification_notification(instance, message))

        except sender.DoesNotExist:
            pass # Object is new, so no original to compare to