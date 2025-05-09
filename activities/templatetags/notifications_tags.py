from django import template
from activities.models import Notification

register = template.Library()

@register.simple_tag(takes_context=True)
def get_notifications(context):
    user = context['request'].user
    if user.is_authenticated:
        return Notification.objects.filter(receiver=user, read_status=False).order_by('-creation_date')[:10]
    return []
