# market/signals.py
from django.db import transaction
from django.db.models.signals import pre_save
from django.dispatch import receiver
from django.urls import reverse
from .models import Order
from notifications.models import Notification

def create_order_status_notification(buyer, order_id, status):
    """Creates a notification for an order status change."""
    Notification.objects.using('default').create(
        user=buyer,
        message=f"The status of your order #{order_id} has been updated to: {status}.",
        link=reverse('order_history')
    )

@receiver(pre_save, sender=Order)
def order_status_notification(sender, instance, **kwargs):
    """
    Triggers a notification when an order's status changes.
    """
    if instance.pk:
        try:
            original = sender.objects.get(pk=instance.pk)
            if original.status != instance.status:
                transaction.on_commit(lambda: create_order_status_notification(instance.buyer, instance.id, instance.status))
        except sender.DoesNotExist:
            pass