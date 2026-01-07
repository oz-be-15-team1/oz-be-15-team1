from decimal import Decimal

from rest_framework.reverse import reverse
from rest_framework.test import APITestCase

from apps.account.models import Account
from apps.members.models import User


# 계좌 관련 API를 검증하는 테스트 클래스 정의
class AccountAPITests(APITestCase):
    # 각 테스트 전에 공통 데이터 생성
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
            account_number="123-456",
        )
        # 다른 사용자의 계좌 생성
        Account.objects.create(
            user=self.other_user,
            name="Other Account",
            source_type="cash",
            balance=Decimal("500.00"),
        )

        # 테스트 클라이언트를 기본 사용자로 인증
        self.client.force_authenticate(self.user)

    # 목록 조회 시 본인 계좌만 반환되는지 확인
    def test_list_accounts_returns_only_user_accounts(self):
        # 같은 사용자의 추가 계좌 생성
        Account.objects.create(
            user=self.user,
            name="Second Account",
            source_type="card",
            balance=Decimal("250.00"),
            card_number="9999",
        )

        # 계좌 목록 엔드포인트 URL 생성
        url = reverse("accounts-list")
        # 인증된 사용자로 GET 요청
        response = self.client.get(url)

        # 응답 코드 확인
        self.assertEqual(response.status_code, 200)
        # 사용자 계좌 두 건만 반환되는지 확인
        self.assertEqual(len(response.data), 2)
        # 반환된 id 집합 계산
        returned_ids = {item["id"] for item in response.data}
        # DB에서 사용자 계좌 id 집합과 동일한지 검증
        self.assertSetEqual(returned_ids, set(Account.objects.filter(user=self.user).values_list("id", flat=True)))

    # 계좌 생성 시 소유자 설정과 201 응답을 확인
    def test_create_account_sets_owner_and_returns_201(self):
        # 계좌 생성 엔드포인트 URL 생성
        url = reverse("accounts-list")
        # 생성 요청 페이로드 구성
        payload = {
            "name": "New Account",
            "source_type": "bank",
            "balance": "300.50",
            "account_number": "321-654",
            "bank_code": "001",
            "account_type": "checking",
        }

        # POST 요청으로 계좌 생성 시도
        response = self.client.post(url, payload, format="json")

        # 생성 성공 응답 코드 확인
        self.assertEqual(response.status_code, 201)
        # 현재 사용자 계좌가 두 건인지 확인
        self.assertEqual(Account.objects.filter(user=self.user).count(), 2)
        # 생성된 계좌 객체 조회
        created = Account.objects.get(id=response.data["id"])
        # 소유자가 요청 사용자와 동일한지 검증
        self.assertEqual(created.user, self.user)
        # 이름과 잔액이 요청대로 저장되었는지 확인
        self.assertEqual(created.name, "New Account")
        self.assertEqual(created.balance, Decimal("300.50"))

    # 단일 계좌 조회가 정상 동작하는지 확인
    def test_retrieve_account(self):
        # 상세 조회 엔드포인트 URL 생성
        url = reverse("accounts-detail", args=[self.account.id])
        # GET 요청으로 상세 조회
        response = self.client.get(url)

        # 응답 코드와 반환 데이터 검증
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["id"], self.account.id)
        self.assertEqual(response.data["name"], "Main Account")

    # 계좌 부분 수정(PATCH)이 적용되는지 확인
    def test_partial_update_account_updates_fields(self):
        # 상세 엔드포인트 URL 생성
        url = reverse("accounts-detail", args=[self.account.id])
        # 수정할 필드 페이로드
        payload = {
            "name": "Updated Account Name",
            "balance": "1500.00",
        }

        # PATCH 요청 수행
        response = self.client.patch(url, payload, format="json")

        # 200 응답과 필드 변경 여부 확인
        self.assertEqual(response.status_code, 200)
        self.account.refresh_from_db()
        self.assertEqual(self.account.name, "Updated Account Name")
        self.assertEqual(self.account.balance, Decimal("1500.00"))

    # 전체 수정(PUT)이 적용되는지 확인
    def test_full_update_account(self):
        # 상세 엔드포인트 URL 생성
        url = reverse("accounts-detail", args=[self.account.id])
        # 전체 필드 페이로드
        payload = {
            "name": "Completely New Account",
            "source_type": "card",
            "balance": "2000.00",
            "card_company": "Samsung",
            "card_number": "1234-5678",
        }

        # PUT 요청 수행
        response = self.client.put(url, payload, format="json")

        # 200 응답과 모든 필드 변경 여부 확인
        self.assertEqual(response.status_code, 200)
        self.account.refresh_from_db()
        self.assertEqual(self.account.name, "Completely New Account")
        self.assertEqual(self.account.source_type, "card")
        self.assertEqual(self.account.balance, Decimal("2000.00"))

    # 계좌 삭제가 가능한지 확인
    def test_delete_account(self):
        # 삭제 엔드포인트 URL 생성
        url = reverse("accounts-detail", args=[self.account.id])
        # DELETE 요청 수행
        response = self.client.delete(url)

        # 204 응답과 실제 삭제 여부 확인
        self.assertEqual(response.status_code, 204)
        self.assertFalse(Account.objects.filter(id=self.account.id).exists())

    # 인증되지 않은 요청이 거절되는지 확인
    def test_unauthenticated_requests_are_rejected(self):
        # 클라이언트 인증 해제
        self.client.force_authenticate(user=None)
        # 목록 URL 생성
        url = reverse("accounts-list")
        # 인증 없이 GET 요청
        response = self.client.get(url)
        # 401 또는 403 여부 확인
        self.assertIn(response.status_code, (401, 403))

        # 상세 URL 생성
        detail_url = reverse("accounts-detail", args=[self.account.id])
        # 인증 없이 상세 GET 요청
        response = self.client.get(detail_url)
        # 401 또는 403 여부 확인
        self.assertIn(response.status_code, (401, 403))
