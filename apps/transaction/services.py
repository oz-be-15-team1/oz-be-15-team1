from decimal import Decimal

from django.db import transaction
from rest_framework.exceptions import PermissionDenied, ValidationError

from apps.account.models import Account

from .models import Transaction


def create_transaction(user, *, account_id, amount, direction, method, description, occurred_at):
    # account_id는 정수 PK 또는 Account 인스턴스일 수 있음.
    # 안전하게 PK를 얻어 select_for_update로 잠금 조회 수행
    pk = account_id.id if hasattr(account_id, "id") else account_id
    try:
        account = Account.objects.select_for_update().get(pk=pk)
    except Account.DoesNotExist:
        raise ValidationError("계좌가 없습니다")

    # 조회된 계좌가 요청 사용자 소유인지 확인
    if account.user_id != user.id:
        # 소유자가 아니면 권한 예외
        raise PermissionDenied("계좌 정보가 일치하지 않습니다")

    # amount를 Decimal로 변환
    amount = Decimal(amount)

    # 수입(income)은 잔액을 증가시키고, 그외는 잔액을 감소
    if direction == "income":
        # income인 경우 잔액 더하기
        new_balance = account.balance + amount
    else:
        # expense/transfer 등은 잔액 빼기
        new_balance = account.balance - amount

    # 트랜잭션 블록으로 Transaction 생성과 Account 갱신을 원자적으로 수행
    with transaction.atomic():
        # Transaction 레코드 생성
        tx = Transaction.objects.create(
            account=account,
            amount=amount,
            balance_after=new_balance,
            direction=direction,
            method=method,
            description=description or "",
            occurred_at=occurred_at,
        )

        # Account 모델의 balance를 갱신하고 저장
        account.balance = new_balance
        account.save(update_fields=["balance"])

    # 생성된 Transaction 인스턴스를 반환
    return tx
