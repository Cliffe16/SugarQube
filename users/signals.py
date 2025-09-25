from django.db.models.signals import pre_save
from django.dispatch import receiver
from django.urls import reverse
from .models import CustomUser
from notifications.models import Notification

@receiver(pre_save, sender=CustomUser)
def user_verification_notification(sender, instance, **kwargs):
    if instance.pk:
        try:
            original = sender.objects.get(pk=instance.pk)
            if original.is_verified_buyer != instance.is_verified_buyer and instance.is_verified_buyer:
                Notification.objects.create(
                    user=instance,
                    message="Congratulations! Your account has been verified as a buyer.",
                    link=reverse('profile')
                )
            if original.is_verified_seller != instance.is_verified_seller and instance.is_verified_seller:
                Notification.objects.create(
                    user=instance,
                    message="Congratulations! Your account has been verified as a seller.",
                    link=reverse('profile')
                )
        except sender.DoesNotExist:
            pass # Object is new, so no original to compare to