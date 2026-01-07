from django.db.models.signals import post_save
from django.dispatch import receiver

from apps.notification.models import Notification

from .models import Analysis


@receiver(post_save, sender=Analysis)
def create_analysis_notification(sender, instance, created, **kwargs):
    if not created:
        return
    about_label = instance.get_about_display()
    period_label = instance.get_type_display()
    message = f"{period_label} {about_label} 분석이 완료되었습니다. 그래프를 확인하세요."
    Notification.objects.create(user=instance.user, message=message, is_read=False)
