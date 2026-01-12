from django.db import models

from apps.common.models import SoftDeleteManager
from apps.members.models import User
from apps.trashcan.models import TrashableModel


class Notification(TrashableModel):
    """
    사용자 알림 모델.
    """

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="notifications")
    message = models.TextField()
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    #  soft delete 기본 매니저
    objects = SoftDeleteManager()
    all_objects = models.Manager()

    def __str__(self):
        return f"{self.user.email} - {self.message[:50]}"
