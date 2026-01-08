from django.db import models
from django.conf import settings


class BudgetScopeType(models.TextChoices):
    ALL = "ALL", "All"
    ACCOUNT = "ACCOUNT", "Account"
    CATEGORY = "CATEGORY", "Category"
    TAG = "TAG", "Tag"


class ThresholdType(models.TextChoices):
    PERCENT = "PERCENT", "Percent"
    AMOUNT = "AMOUNT", "Amount"


class Budget(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, db_column="user_id")
    name = models.CharField(max_length=255)
    period_start = models.DateField()
    period_end = models.DateField()
    amount_limit = models.DecimalField(max_digits=14, decimal_places=2)
    scope_type = models.CharField(max_length=20, choices=BudgetScopeType.choices)
    scope_ref_id = models.BigIntegerField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    deleted_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = "budgets"


class BudgetAlertRule(models.Model):
    budget = models.ForeignKey(Budget, on_delete=models.CASCADE, db_column="budget_id", related_name="alert_rules")
    threshold_type = models.CharField(max_length=20, choices=ThresholdType.choices)
    threshold_value = models.DecimalField(max_digits=14, decimal_places=2)
    is_enabled = models.BooleanField(default=True)
    last_triggered_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "budget_alert_rules"


class BudgetAlertEvent(models.Model):
    """
    "알림을 보냈다" 기록(중복 방지 + 알림 목록에 쓰기 좋음)
    """
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, db_column="user_id")
    budget = models.ForeignKey(Budget, on_delete=models.CASCADE, db_column="budget_id")
    rule = models.ForeignKey(BudgetAlertRule, on_delete=models.CASCADE, db_column="rule_id")

    spent = models.DecimalField(max_digits=14, decimal_places=2)
    budget_limit = models.DecimalField(max_digits=14, decimal_places=2)
    triggered_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "budget_alert_events"
        indexes = [
            models.Index(fields=["user", "budget", "rule", "triggered_at"]),
        ]
