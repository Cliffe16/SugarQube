# support/signals.py
from django.db import transaction
from django.db.models.signals import pre_save
from django.dispatch import receiver
from django.urls import reverse
from .models import SupportTicket
from notifications.models import Notification

def create_ticket_resolved_notification(user, subject):
    """Creates a notification when a support ticket is resolved."""
    Notification.objects.using('default').create(
        user=user,
        message=f"Your support ticket '{subject}' has been resolved.",
        link=reverse('support_page')
    )

@receiver(pre_save, sender=SupportTicket)
def support_ticket_notification(sender, instance, **kwargs):
    """
    Triggers a notification when a ticket's status changes to 'Resolved'.
    """
    if instance.pk:
        try:
            original = sender.objects.get(pk=instance.pk)
            if original.status != 'Resolved' and instance.status == 'Resolved':
                transaction.on_commit(lambda: create_ticket_resolved_notification(instance.user, instance.subject))
        except sender.DoesNotExist:
            pass