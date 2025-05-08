from activities.models import Notification

def notification_count(request):
    if request.user.is_authenticated:
        count = Notification.objects.filter(receiver=request.user, read_status=False).count()
        return {'notification_count': count}
    return {'notification_count': 0}