from decimal import Decimal

from django.db.models import Avg, Count, Max, Min, Q, Sum
from django.db.models.functions import TruncDate, TruncMonth

from .models import Transaction


class TransactionRepository:
    # Transaction 모델에 대한 쿼리 최적화 패턴을 적용한 Repository

    @staticmethod
    def get_transactions_optimized(user):
        # select_related를 사용하여 연관된 account와 user를 한 번에 조회
        return Transaction.objects.select_related("account", "account__user").filter(
            account__user=user
        )

    @staticmethod
    def get_transactions_only_essential(user):
        # only를 사용하여 필수 필드만 조회 (리스트 뷰 등에 적합)
        return (
            Transaction.objects.select_related("account")
            .filter(account__user=user)
            .only("id", "amount", "direction", "occurred_at", "account__id", "account__name")
        )

    @staticmethod
    def get_transactions_defer_description(user):
        # defer를 사용하여 긴 텍스트 필드(description)를 나중에 로드
        return (
            Transaction.objects.select_related("account")
            .filter(account__user=user)
            .defer("description")
        )

    @staticmethod
    def get_daily_summary(user, start_date=None, end_date=None):
        # annotate + TruncDate를 사용하여 일별 거래 요약 조회
        qs = Transaction.objects.filter(account__user=user)

        if start_date:
            qs = qs.filter(occurred_at__gte=start_date)
        if end_date:
            qs = qs.filter(occurred_at__lte=end_date)

        return (
            qs.annotate(date=TruncDate("occurred_at"))
            .values("date")
            .annotate(
                total_count=Count("id"),
                total_income=Sum("amount", filter=Q(direction="income"), default=Decimal("0")),
                total_expense=Sum("amount", filter=Q(direction="expense"), default=Decimal("0")),
                avg_amount=Avg("amount"),
            )
            .order_by("date")
        )

    @staticmethod
    def get_monthly_summary(user, year=None):
        # annotate + TruncMonth를 사용하여 월별 거래 요약 조회
        qs = Transaction.objects.filter(account__user=user)

        if year:
            qs = qs.filter(occurred_at__year=year)

        return (
            qs.annotate(month=TruncMonth("occurred_at"))
            .values("month")
            .annotate(
                total_count=Count("id"),
                total_income=Sum("amount", filter=Q(direction="income"), default=Decimal("0")),
                total_expense=Sum("amount", filter=Q(direction="expense"), default=Decimal("0")),
            )
            .order_by("month")
        )

    @staticmethod
    def get_account_statistics(user, account_id):
        # aggregate를 사용하여 특정 계좌의 통계 정보를 한 번에 조회
        return Transaction.objects.filter(account__user=user, account_id=account_id).aggregate(
            total_transactions=Count("id"),
            total_income=Sum("amount", filter=Q(direction="income"), default=Decimal("0")),
            total_expense=Sum("amount", filter=Q(direction="expense"), default=Decimal("0")),
            avg_transaction=Avg("amount"),
            max_transaction=Max("amount"),
            min_transaction=Min("amount"),
        )

    @staticmethod
    def get_transactions_values_list(user):
        # values_list를 사용하여 튜플 형태로 필요한 데이터만 조회
        # 내부 처리용으로 적합
        return Transaction.objects.filter(account__user=user).values_list(
            "id", "amount", "direction", "occurred_at"
        )

    @staticmethod
    def get_direction_summary(user):
        # values + annotate를 사용하여 거래 타입별 집계
        return (
            Transaction.objects.filter(account__user=user)
            .values("direction")
            .annotate(count=Count("id"), total_amount=Sum("amount"), avg_amount=Avg("amount"))
            .order_by("direction")
        )
