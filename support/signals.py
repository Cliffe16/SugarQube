from django.db.models.signals import pre_save
from django.dispatch import receiver
from django.urls import reverse
from .models import SupportTicket
from notifications.models import Notification

@receiver(pre_save, sender=SupportTicket)
def support_ticket_notification(sender, instance, **kwargs):
    if instance.pk:
        try:
            original = sender.objects.get(pk=instance.pk)
            if original.status != instance.status and instance.status == 'Resolved':
                Notification.objects.create(
                    user=instance.user,
                    message=f"Your support ticket '{instance.subject}' has been resolved.",
                    link=reverse('support_page')
                )
        except sender.DoesNotExist:
            pass