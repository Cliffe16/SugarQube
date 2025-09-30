from django.db.models.signals import pre_save, post_save, post_delete
from django.dispatch import receiver
from django.contrib.auth import get_user_model
from .models import SugarPrice
from notifications.models import Notification
from django.core.cache import cache

@receiver(pre_save, sender=SugarPrice)
def exchange_rate_shift_notification(sender, instance, **kwargs):
    """
    Triggers a notification only when the 'rate' field is updated.
    """
    if instance.pk:
        try:
            original = sender.objects.get(pk=instance.pk)
            # Only proceed if the rate has changed
            if original.rate != instance.rate:
                User = get_user_model()
                all_users = User.objects.using('credentials').all()
                message = f"Currency Update: The KES/USD exchange rate has been updated to {instance.rate}."

                notifications_to_create = [
                    Notification(user=user, message=message) for user in all_users
                ]

                if notifications_to_create:
                    Notification.objects.using('credentials').bulk_create(notifications_to_create)
        except sender.DoesNotExist:
            pass


@receiver(post_save, sender=SugarPrice)
def invalidate_prediction_cache_on_save(sender, instance, created, **kwargs):
    """
    Invalidate prediction caches when price data is modified.
    Trigger async cache warming.
    """
    # Clear prepared data cache
    cache.delete('prepared_sugar_data')
    
    # Clear all prediction caches
    for days in [7, 14, 30]:
        for model in ['auto', 'arima', 'ets', 'ma']:
            for ci in ['True', 'False']:
                cache_key = f'prediction_api_{days}_{model}_{ci}'
                cache.delete(cache_key)
    
    # Trigger async cache warming (only if Celery is available)
    try:
        from .tasks import prewarm_prediction_cache
        prewarm_prediction_cache.delay()
    except:
        pass  # Celery not available, skip async warming


@receiver(post_delete, sender=SugarPrice)
def invalidate_prediction_cache_on_delete(sender, instance, **kwargs):
    """
    Invalidate prediction caches when price data is deleted.
    """
    # Clear prepared data cache
    cache.delete('prepared_sugar_data')
    
    # Clear all prediction caches
    for days in [7, 14, 30]:
        for model in ['auto', 'arima', 'ets', 'ma']:
            for ci in ['True', 'False']:
                cache_key = f'prediction_api_{days}_{model}_{ci}'
                cache.delete(cache_key)
    
    # Trigger async cache warming
    try:
        from .tasks import prewarm_prediction_cache
        prewarm_prediction_cache.delay()
    except:
        pass