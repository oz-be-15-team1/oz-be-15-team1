from datetime import timedelta

from django.conf import settings
from django.utils import timezone

from apps.notification.models import Notification


def send_budget_alert(user, message):
    dedup_minutes = getattr(settings, "BUDGET_ALERT_DEDUP_MINUTES", 5)
    since = timezone.now() - timedelta(minutes=dedup_minutes)

    if Notification.objects.filter(
        user=user,
        message=message,
        created_at__gte=since,
    ).exists():
        return None

    notif = Notification.objects.create(user=user, message=message)
    print(f"{user}에게 알림 전송: {message}")
    return notif
