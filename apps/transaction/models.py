from django.db import models

from apps.account.models import Account
from apps.common.models import SoftDeleteManager
from apps.tag.models import Tag
from apps.trashcan.models import TrashableModel


class Transaction(TrashableModel):
    id: int
    DIRECTION_CHOICES = [
        ("income", "Income"),
        ("expense", "Expense"),
        ("transfer", "Transfer"),
    ]

    account = models.ForeignKey(Account, on_delete=models.CASCADE, related_name="transactions")

    amount = models.DecimalField(max_digits=14, decimal_places=2)
    balance_after = models.DecimalField(max_digits=14, decimal_places=2)

    direction = models.CharField(max_length=10, choices=DIRECTION_CHOICES)
    method = models.CharField(max_length=20)
    description = models.CharField(max_length=255, blank=True)

    tags = models.ManyToManyField(Tag, related_name="transactions", blank=True)

    occurred_at = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    #  soft delete 기본 매니저
    objects = SoftDeleteManager()
    all_objects = models.Manager()

    def __str__(self):
        return f"{self.account.name} - {self.amount} ({self.direction})"
