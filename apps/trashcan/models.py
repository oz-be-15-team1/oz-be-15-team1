from django.conf import settings
from django.db import models
from django.utils import timezone


class TrashableModel(models.Model):
    """
    Soft delete(휴지통) 공통 베이스 모델
    - deleted_at 이 NULL이면 정상
    - deleted_at 이 값 있으면 휴지통
    """

    deleted_at = models.DateTimeField(null=True, blank=True, db_index=True)
    deleted_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="deleted_%(class)s_set",
    )

    class Meta:
        abstract = True

    @property
    def is_deleted(self) -> bool:
        return self.deleted_at is not None

    def trash(self, user=None):
        if self.deleted_at is None:
            self.deleted_at = timezone.now()
            if user and getattr(user, "is_authenticated", False):
                self.deleted_by = user
            self.save(update_fields=["deleted_at", "deleted_by"])

    def restore(self):
        if self.deleted_at is not None:
            self.deleted_at = None
            self.deleted_by = None
            self.save(update_fields=["deleted_at", "deleted_by"])
