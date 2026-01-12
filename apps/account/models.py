from django.db import models

from apps.members.models import User
from apps.trashcan.models import TrashableModel


class Account(TrashableModel):
    id: int
    SOURCE_TYPE_CHOICES = [
        ("bank", "Bank"),
        ("card", "Card"),
        ("cash", "Cash"),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="accounts")

    name = models.CharField(max_length=50)
    source_type = models.CharField(max_length=10, choices=SOURCE_TYPE_CHOICES)
    balance = models.DecimalField(max_digits=14, decimal_places=2)
    is_active = models.BooleanField(default=True)

    account_number = models.CharField(max_length=32, blank=True)
    account_type = models.CharField(max_length=30, blank=True)

    card_company = models.CharField(max_length=30, blank=True)
    card_number = models.CharField(max_length=32, blank=True)
    billing_day = models.IntegerField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.email} - {self.name}"
