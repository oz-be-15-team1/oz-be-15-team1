from decimal import Decimal

from django.db.models import Count, Q, Sum

from .models import Account


class AccountRepository:
    # Account 모델에 대한 쿼리 최적화 패턴을 적용한 Repository

    @staticmethod
    def get_accounts_with_stats(user):
        # annotate를 사용하여 계좌별 거래 건수와 총액을 한 번의 쿼리로 조회
        return (
            Account.objects
            .filter(user=user)
            .select_related('user')
            .annotate(
                transaction_count=Count('transactions'),
                total_income=Sum(
                    'transactions__amount',
                    filter=Q(transactions__direction='income'),
                    default=Decimal('0')
                ),
                total_expense=Sum(
                    'transactions__amount',
                    filter=Q(transactions__direction='expense'),
                    default=Decimal('0')
                )
            )
        )

    @staticmethod
    def get_active_accounts_only_fields(user):
        # only를 사용하여 필요한 필드만 조회 (메모리 최적화)
        return (
            Account.objects
            .filter(user=user, is_active=True)
            .only('id', 'name', 'source_type', 'balance')
        )

    @staticmethod
    def get_accounts_defer_timestamps(user):
        # defer를 사용하여 타임스탬프 필드를 제외하고 조회
        # 리스트 조회 시 created_at, updated_at이 필요 없는 경우 사용
        return (
            Account.objects
            .filter(user=user)
            .select_related('user')
            .defer('created_at', 'updated_at')
        )

    @staticmethod
    def get_accounts_summary_values(user):
        # values를 사용하여 딕셔너리 형태로 필요한 데이터만 조회
        # API 응답이 아닌 내부 로직에서 사용할 때 유용
        return (
            Account.objects
            .filter(user=user)
            .values('id', 'name', 'balance', 'source_type')
        )

    @staticmethod
    def get_total_balance_by_source_type(user):
        # aggregate를 사용하여 source_type별 총 잔액 집계
        return (
            Account.objects
            .filter(user=user, is_active=True)
            .values('source_type')
            .annotate(total_balance=Sum('balance'))
            .order_by('source_type')
        )
