from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from .models import Notification

@login_required
def get_notifications(request):
    """
    API endpoint to fetch unread notifications for the logged-in user.
    """
    notifications = Notification.objects.filter(user=request.user, is_read=False)
    count = notifications.count()
    notifications_data = [{
        'id': n.id,
        'message': n.message,
        'timestamp': n.timestamp.strftime('%b %d, %Y, %I:%M %p'),
        'link': n.link
    } for n in notifications]

    return JsonResponse({
        'count': count,
        'notifications': notifications_data
    })

@login_required
def mark_as_read(request, notification_id):
    """
    API endpoint to mark a specific notification as read.
    """
    try:
        notification = Notification.objects.get(id=notification_id, user=request.user)
        notification.is_read = True
        notification.save()
        return JsonResponse({'status': 'success'})
    except Notification.DoesNotExist:
        return JsonResponse({'status': 'error', 'message': 'Notification not found'}, status=404)