from django.db.models.signals import pre_save
from django.dispatch import receiver
from django.urls import reverse
from .models import Order
from notifications.models import Notification

@receiver(pre_save, sender=Order)
def order_status_notification(sender, instance, **kwargs):
    if instance.pk:
        try:
            original = sender.objects.get(pk=instance.pk)
            if original.status != instance.status:
                Notification.objects.create(
                    user=instance.buyer,
                    message=f"The status of your order #{instance.id} has been updated to: {instance.status}.",
                    link=reverse('order_history')
                )
        except sender.DoesNotExist:
            pass

