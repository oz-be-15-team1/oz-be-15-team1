from django.conf import settings
from django.db import models
from django.utils import timezone


class Category(models.Model):
    class Kind(models.TextChoices):
        INCOME = "INCOME", "INCOME"
        EXPENSE = "EXPENSE", "EXPENSE"

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="categories",
        null=True,
        blank=True,
    )
    parent = models.ForeignKey(
        "self", null=True, blank=True, on_delete=models.SET_NULL, related_name="children"
    )

    name = models.CharField(max_length=50)
    kind = models.CharField(max_length=10, choices=Kind.choices)
    sort_order = models.IntegerField(default=0)

    created_at = models.DateTimeField(auto_now_add=True)
    deleted_at = models.DateTimeField(null=True, blank=True)

    def soft_delete(self):
        if self.deleted_at is None:
            self.deleted_at = timezone.now()
            self.save(update_fields=["deleted_at"])

    def restore(self):
        if self.deleted_at is not None:
            self.deleted_at = None
            self.save(update_fields=["deleted_at"])

    class Meta:
        indexes = [
            models.Index(fields=["user", "deleted_at"]),
            models.Index(fields=["user", "kind", "deleted_at"]),
        ]
        ordering = ["sort_order", "id"]

    def __str__(self) -> str:
        return self.name
