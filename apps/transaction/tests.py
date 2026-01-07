from decimal import Decimal

from django.utils import timezone
from rest_framework.reverse import reverse
from rest_framework.test import APITestCase

from apps.account.models import Account
from apps.members.models import User
from apps.transaction.models import Transaction


# 거래 관련 API를 검증하는 테스트 클래스 정의
class TransactionAPITests(APITestCase):
    # 각 테스트 실행 전 공통 데이터 설정
    def setUp(self):
        # 기본 사용자 생성
        self.user = User.objects.create_user(
            email="user@example.com",
            password="testpass123",
            name="Test User",
            nickname="tester",
        )
        # 다른 사용자 생성
        self.other_user = User.objects.create_user(
            email="other@example.com",
            password="testpass123",
            name="Other User",
            nickname="other",
        )

        # 기본 사용자의 계좌 생성
        self.account = Account.objects.create(
            user=self.user,
            name="Main Account",
            source_type="bank",
            balance=Decimal("1000.00"),
        )
        # 다른 사용자의 계좌 생성
        self.other_account = Account.objects.create(
            user=self.other_user,
            name="Other Account",
            source_type="cash",
            balance=Decimal("800.00"),
        )

        # 기본 거래 한 건 생성
        self.transaction = Transaction.objects.create(
            account=self.account,
            amount=Decimal("100.00"),
            balance_after=Decimal("900.00"),
            direction="expense",
            method="card",
            description="Groceries",
            occurred_at=timezone.now(),
        )

        # 테스트 클라이언트를 기본 사용자로 인증
        self.client.force_authenticate(self.user)

    # 사용자 범위와 direction 필터가 적용되는지 확인
    def test_list_transactions_filters_by_user_and_direction(self):
        # 같은 사용자 수입 거래 추가
        Transaction.objects.create(
            account=self.account,
            amount=Decimal("200.00"),
            balance_after=Decimal("1100.00"),
            direction="income",
            method="cash",
            description="Salary",
            occurred_at=timezone.now(),
        )
        # 다른 사용자 거래 추가
        Transaction.objects.create(
            account=self.other_account,
            amount=Decimal("50.00"),
            balance_after=Decimal("750.00"),
            direction="expense",
            method="cash",
            description="Other user expense",
            occurred_at=timezone.now(),
        )

        # 거래 목록 URL 생성
        url = reverse("transactions-list")
        # direction=income 필터로 GET 요청
        response = self.client.get(url, {"direction": "income"})

        # 응답 코드와 반환 건수 확인
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 1)
        # 반환된 거래 방향과 계좌가 기대와 일치하는지 확인
        self.assertEqual(response.data[0]["direction"], "income")
        self.assertEqual(response.data[0]["account"], self.account.id)

    # 단일 거래 조회가 정상 동작하는지 확인
    def test_retrieve_transaction(self):
        # 상세 조회 엔드포인트 URL 생성
        url = reverse("transactions-detail", args=[self.transaction.id])
        # GET 요청으로 상세 조회
        response = self.client.get(url)

        # 응답 코드와 반환 데이터 검증
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["id"], self.transaction.id)
        self.assertEqual(response.data["amount"], "100.00")
        self.assertEqual(response.data["direction"], "expense")
        self.assertEqual(response.data["description"], "Groceries")

    # 타인의 거래 조회 시 접근이 거부되는지 확인
    def test_retrieve_other_users_transaction_returns_404(self):
        # 다른 사용자의 거래 생성
        other_transaction = Transaction.objects.create(
            account=self.other_account,
            amount=Decimal("50.00"),
            balance_after=Decimal("750.00"),
            direction="expense",
            method="cash",
            description="Other user transaction",
            occurred_at=timezone.now(),
        )

        # 다른 사용자의 거래 상세 조회 시도
        url = reverse("transactions-detail", args=[other_transaction.id])
        response = self.client.get(url)

        # 404 응답 확인 (본인 거래가 아니므로 조회 불가)
        self.assertEqual(response.status_code, 404)

    # 거래 생성 시 잔액 반영과 201 응답을 확인
    def test_create_transaction_updates_balance_and_returns_201(self):
        # 거래 생성 URL 생성
        url = reverse("transactions-list")
        # 생성 요청 페이로드 구성
        payload = {
            "account": self.account.id,
            "amount": "150.00",
            "direction": "income",
            "method": "transfer",
            "description": "Refund",
            "occurred_at": timezone.now().isoformat(),
        }

        # POST 요청으로 거래 생성 시도
        response = self.client.post(url, payload, format="json")

        # 201 응답 확인
        self.assertEqual(response.status_code, 201)
        # 생성된 거래 조회
        created = Transaction.objects.get(id=response.data["id"])
        # 계좌 최신 상태 반영
        self.account.refresh_from_db()
        # 거래와 계좌 잔액이 기대대로 증가했는지 확인
        self.assertEqual(created.balance_after, Decimal("1150.00"))
        self.assertEqual(self.account.balance, Decimal("1150.00"))

    # 타인의 계좌로 생성 요청 시 거절되는지 확인
    def test_create_transaction_with_other_users_account_returns_403(self):
        # 거래 생성 URL 생성
        url = reverse("transactions-list")
        # 다른 사용자의 계좌로 생성 요청 페이로드
        payload = {
            "account": self.other_account.id,
            "amount": "20.00",
            "direction": "expense",
            "method": "cash",
            "description": "Not allowed",
            "occurred_at": timezone.now().isoformat(),
        }

        # POST 요청 수행
        response = self.client.post(url, payload, format="json")

        # 403 응답인지 확인
        self.assertEqual(response.status_code, 403)

    # 부분 수정(PATCH)이 적용되는지 확인
    def test_partial_update_transaction_updates_fields(self):
        # 상세 엔드포인트 URL 생성
        url = reverse("transactions-detail", args=[self.transaction.id])
        # 수정할 필드 페이로드
        payload = {
            "description": "Updated description",
            "method": "bank",
        }

        # PATCH 요청 수행
        response = self.client.patch(url, payload, format="json")

        # 200 응답과 필드 변경 여부 확인
        self.assertEqual(response.status_code, 200)
        self.transaction.refresh_from_db()
        self.assertEqual(self.transaction.description, "Updated description")
        self.assertEqual(self.transaction.method, "bank")

    # 거래 삭제가 정상 동작하는지 확인
    def test_delete_transaction(self):
        # 삭제 엔드포인트 URL 생성
        url = reverse("transactions-detail", args=[self.transaction.id])
        # DELETE 요청 수행
        response = self.client.delete(url)

        # 204 응답과 실제 삭제 여부 확인
        self.assertEqual(response.status_code, 204)
        self.assertFalse(Transaction.objects.filter(id=self.transaction.id).exists())

    # 인증되지 않은 요청이 거절되는지 확인
    def test_unauthenticated_requests_are_rejected(self):
        # 인증 해제
        self.client.force_authenticate(user=None)
        # 목록 URL 생성
        url = reverse("transactions-list")
        # 인증 없이 GET 요청
        response = self.client.get(url)
        # 401 또는 403 여부 확인
        self.assertIn(response.status_code, (401, 403))
