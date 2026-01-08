# apps/budget/services.py

from __future__ import annotations

from decimal import Decimal
from typing import Optional

from django.apps import apps
from django.db import transaction
from django.db.models import Sum
from django.utils import timezone

from .models import (
    Budget,
    BudgetAlertEvent,
    BudgetAlertRule,
    BudgetScopeType,
    ThresholdType,
)


def _get_transaction_model():
    # apps.transaction.models.Transaction
    return apps.get_model("transaction", "Transaction")


def _get_transaction_tag_model():
    # 있을 때만 사용 (프로젝트에 없으면 호출하지 말 것)
    return apps.get_model("transaction", "TransactionTag")


def is_expense(tx) -> bool:
    """
    현재 Transaction 모델: direction(income/expense/transfer)
    레거시 대응: type이 있을 수도 있어 같이 체크
    """
    value = getattr(tx, "direction", None)
    if value is None:
        value = getattr(tx, "type", None)
    return str(value).lower() in ("expense", "out", "spend")


def _tx_date(tx) -> Optional[timezone.datetime.date]:
    """
    Budget.period_start/end가 date라서 occurred_at의 date로 비교.
    """
    occurred_at = getattr(tx, "occurred_at", None)
    if occurred_at is None:
        # 레거시 필드 대응
        transacted_on = getattr(tx, "transacted_on", None)
        if transacted_on is None:
            return None
        # transacted_on이 date일 수도, datetime일 수도 있으니 안전 처리
        return transacted_on if hasattr(transacted_on, "year") and not hasattr(transacted_on, "date") else transacted_on.date()

    # occurred_at이 aware datetime이라면 .date() 가능
    return occurred_at.date()


def calculate_spent_for_budget(budget: Budget) -> Decimal:
    """
    budget 기간(period_start~period_end) 내의 '지출(expense)' 합계를 계산.
    scope_type에 따라 account 단위 필터링까지 적용.
    """
    Transaction = _get_transaction_model()

    # Transaction 모델은 user_id가 없고 account FK를 통해 user에 연결됨
    qs = Transaction.objects.filter(
        account__user_id=budget.user_id,
        occurred_at__date__gte=budget.period_start,
        occurred_at__date__lte=budget.period_end,
        direction="expense",
    )

    # scope 처리 (ALL/ACCOUNT는 확실)
    if budget.scope_type == BudgetScopeType.ALL:
        pass

    elif budget.scope_type == BudgetScopeType.ACCOUNT:
        qs = qs.filter(account_id=budget.scope_ref_id)

    elif budget.scope_type == BudgetScopeType.CATEGORY:
        # Transaction에 category 필드가 있을 때만 적용
        # (네가 보여준 Transaction 필드 목록에는 category가 없었음)
        if any(f.name == "category" for f in Transaction._meta.fields):
            qs = qs.filter(category_id=budget.scope_ref_id)
        else:
            return Decimal("0")

    elif budget.scope_type == BudgetScopeType.TAG:
        # TransactionTag 모델이 실제로 존재할 때만
        try:
            TransactionTag = _get_transaction_tag_model()
        except Exception:
            return Decimal("0")
        tx_ids = (
            TransactionTag.objects
            .filter(tag_id=budget.scope_ref_id)
            .values_list("transaction_id", flat=True)
        )
        qs = qs.filter(id__in=tx_ids)

    else:
        return Decimal("0")

    agg = qs.aggregate(total=Sum("amount"))
    return agg["total"] or Decimal("0")


def rule_should_trigger(spent: Decimal, budget_limit: Decimal, rule: BudgetAlertRule) -> bool:
    """
    ThresholdType은 모델 Enum/choices 기준으로 비교.
    - PERCENT: (spent / limit) * 100 >= threshold_value
    - AMOUNT: spent >= threshold_value
    """
    # 혹시 threshold_type이 문자열로 저장돼도 대응
    ttype = rule.threshold_type
    if isinstance(ttype, str):
        ttype_norm = ttype.upper()
    else:
        # Enum이면 value가 문자열일 가능성
        ttype_norm = str(ttype).upper()

    if ttype_norm == str(ThresholdType.PERCENT).upper() or ttype_norm == "PERCENT":
        if budget_limit is None or Decimal(budget_limit) == 0:
            return False
        target = Decimal(budget_limit) * (Decimal(rule.threshold_value) / Decimal("100"))
        return Decimal(spent) >= target

    if ttype_norm == str(ThresholdType.AMOUNT).upper() or ttype_norm == "AMOUNT":
        return Decimal(spent) >= Decimal(rule.threshold_value)

    return False


def trigger_budget_alerts_for_transaction(tx) -> None:
    """
    실시간: 거래가 저장된 직후 호출될 함수
    """
    if not is_expense(tx):
        return

    tx_date = _tx_date(tx)
    if not tx_date:
        return

    # Transaction 모델은 tx.user_id가 없으므로 account로 user 추출
    user_id = getattr(tx, "user_id", None)
    if user_id is None:
        account = getattr(tx, "account", None)
        user_id = getattr(account, "user_id", None)

    if not user_id:
        return

    # 이번 거래 날짜에 해당하는 예산만 검사
    budgets = Budget.objects.filter(
        user_id=user_id,
        deleted_at__isnull=True,
        period_start__lte=tx_date,
        period_end__gte=tx_date,
    )

    for budget in budgets:
        spent = calculate_spent_for_budget(budget)
        limit = Decimal(budget.amount_limit)

        # 룰들을 트랜잭션+락으로 처리해서 "중복 알림" 방지
        _check_and_trigger_rules_atomic(budget=budget, spent=spent, budget_limit=limit)


@transaction.atomic
def _check_and_trigger_rules_atomic(*, budget: Budget, spent: Decimal, budget_limit: Decimal) -> None:
    """
    - 룰 row lock(select_for_update)으로 중복 알림 방지
    - last_triggered_at이 있으면 이미 트리거된 룰로 간주(현재 요구사항: 딱 1번만)
    """
    rules = (
        BudgetAlertRule.objects
        .select_for_update()
        .filter(budget_id=budget.id, is_enabled=True)
    )

    now = timezone.now()

    for rule in rules:
        # 이미 한 번 울렸으면 스킵
        if rule.last_triggered_at is not None:
            continue

        if not rule_should_trigger(spent, budget_limit, rule):
            continue

        # 1) 트리거 기록(이벤트)
        BudgetAlertEvent.objects.create(
            user_id=budget.user_id,
            budget_id=budget.id,
            rule_id=rule.id,
            spent=spent,
            budget_limit=budget_limit,
        )

        # 2) 룰 업데이트(“딱 1번만” 보장)
        rule.last_triggered_at = now
        rule.save(update_fields=["last_triggered_at"])

        # 3) 실제 알림 전송
        _send_notification_safely(
            user_id=budget.user_id,
            budget_id=budget.id,
            rule_id=rule.id,
            spent=spent,
            budget_limit=budget_limit,
            threshold_type=rule.threshold_type,
            threshold_value=rule.threshold_value,
        )


def _send_notification_safely(**payload) -> None:
    """
    notification 앱을 건드리지 않기 위해:
    - '있으면' 가져와서 호출
    - 없으면 아무것도 안 함
    """
    try:
        from apps.notification import services as notif_services
        if hasattr(notif_services, "send_budget_alert"):
            notif_services.send_budget_alert(**payload)
    except Exception:
        # 알림 실패가 거래 저장을 실패시키면 안 되므로 예외 삼킴(원하면 로깅 추가)
        return
