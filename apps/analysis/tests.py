from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from apps.members.models import User

from .models import Analysis


class AnalysisModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email="test@example.com", password="testpass123", name="Test User", nickname="testuser"
        )

    def test_analysis_creation(self):
        analysis = Analysis.objects.create(
            user=self.user,
            about="total_expense",
            type="monthly",
            period_start="2024-01-01",
            period_end="2024-01-31",
            description="월별 총 지출 분석",
        )
        self.assertEqual(analysis.user, self.user)
        self.assertEqual(analysis.about, "total_expense")
        self.assertEqual(analysis.type, "monthly")
        self.assertEqual(str(analysis), f"{self.user.email} - total_expense (monthly)")

    def test_analysis_str_method(self):
        analysis = Analysis.objects.create(
            user=self.user,
            about="total_income",
            type="weekly",
            period_start="2024-01-01",
            period_end="2024-01-07",
            description="주별 총 수입 분석",
        )
        expected_str = f"{self.user.email} - total_income (weekly)"
        self.assertEqual(str(analysis), expected_str)


class AnalysisAPITest(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email="api@example.com", password="apitest123", name="API User", nickname="apiuser"
        )
        self.other_user = User.objects.create_user(
            email="other@example.com",
            password="othertest123",
            name="Other User",
            nickname="otheruser",
        )
        self.client.force_authenticate(user=self.user)

    def test_get_analyses_list(self):
        url = reverse("analysis-list")
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_create_analysis(self):
        url = reverse("analysis-list")
        data = {
            "user": self.user.id,
            "about": "category_expense",
            "type": "monthly",
            "period_start": "2024-01-01",
            "period_end": "2024-01-31",
            "description": "카테고리별 지출 분석",
        }
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Analysis.objects.count(), 1)
        self.assertEqual(Analysis.objects.get().about, "category_expense")

    def test_get_analysis_detail(self):
        analysis = Analysis.objects.create(
            user=self.user,
            about="account_balance",
            type="weekly",
            period_start="2024-01-01",
            period_end="2024-01-07",
            description="계좌 잔액 분석",
        )
        url = reverse("analysis-detail", kwargs={"pk": analysis.pk})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["about"], "account_balance")

    def test_update_analysis(self):
        analysis = Analysis.objects.create(
            user=self.user,
            about="total_expense",
            type="monthly",
            period_start="2024-01-01",
            period_end="2024-01-31",
            description="원래 설명",
        )
        url = reverse("analysis-detail", kwargs={"pk": analysis.pk})
        data = {"description": "수정된 설명"}
        response = self.client.patch(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        analysis.refresh_from_db()
        self.assertEqual(analysis.description, "수정된 설명")

    def test_delete_analysis(self):
        analysis = Analysis.objects.create(
            user=self.user,
            about="total_income",
            type="weekly",
            period_start="2024-01-01",
            period_end="2024-01-07",
            description="삭제할 분석",
        )
        url = reverse("analysis-detail", kwargs={"pk": analysis.pk})
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Analysis.objects.count(), 0)

    def test_get_analysis_list_by_period_type(self):
        Analysis.objects.create(
            user=self.user,
            about="total_expense",
            type="weekly",
            period_start="2024-01-01",
            period_end="2024-01-07",
            description="주간 분석",
        )
        Analysis.objects.create(
            user=self.user,
            about="total_income",
            type="monthly",
            period_start="2024-01-01",
            period_end="2024-01-31",
            description="월간 분석",
        )
        Analysis.objects.create(
            user=self.other_user,
            about="category_expense",
            type="weekly",
            period_start="2024-01-01",
            period_end="2024-01-07",
            description="다른 유저 주간 분석",
        )
        url = reverse("analysis-period-list")
        response = self.client.get(url, {"type": "weekly"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["type"], "weekly")
        self.assertEqual(response.data[0]["user"], self.user.id)


class AnalyzerTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email="analyzer@example.com",
            password="testpass123",
            name="Analyzer User",
            nickname="analyzer",
        )
        # 계좌 생성
        from apps.account.models import Account

        self.account = Account.objects.create(
            user=self.user,
            name="테스트 계좌",
            source_type="bank",
            balance=1000000,
            account_number="123-456-789",
            bank_code="001",
        )
        # 거래 내역 생성
        from datetime import datetime

        from apps.transaction.models import Transaction

        Transaction.objects.create(
            account=self.account,
            amount=50000,
            balance_after=950000,
            direction="expense",
            method="식비",
            description="점심 식사",
            occurred_at=datetime(2024, 1, 15, 12, 0),
        )
        Transaction.objects.create(
            account=self.account,
            amount=100000,
            balance_after=1050000,
            direction="income",
            method="급여",
            description="월급",
            occurred_at=datetime(2024, 1, 1, 9, 0),
        )

    def test_analyzer_creation(self):
        from .analyzers import Analyzer

        analyzer = Analyzer(self.user)
        self.assertEqual(analyzer.user, self.user)

    def test_get_transactions_in_period(self):
        from .analyzers import Analyzer

        analyzer = Analyzer(self.user)
        transactions = analyzer.get_transactions_in_period("2024-01-01", "2024-01-31")
        self.assertEqual(transactions.count(), 2)

    def test_create_dataframe(self):
        from .analyzers import Analyzer

        analyzer = Analyzer(self.user)
        transactions = analyzer.get_transactions_in_period("2024-01-01", "2024-01-31")
        df = analyzer.create_dataframe(transactions)
        self.assertEqual(len(df), 2)
        self.assertIn("date", df.columns)
        self.assertIn("amount", df.columns)

    def test_run_analysis_total_expense(self):
        from .analyzers import Analyzer

        analyzer = Analyzer(self.user)
        analysis = analyzer.run_analysis("total_expense", "monthly", "2024-01-01", "2024-01-31")
        self.assertEqual(analysis.user, self.user)
        self.assertEqual(analysis.about, "total_expense")
        self.assertEqual(analysis.type, "monthly")
        self.assertIsNotNone(analysis.result_image)
        self.assertIn("총 지출", analysis.description)

    def test_run_analysis_no_transactions(self):
        from .analyzers import Analyzer

        analyzer = Analyzer(self.user)
        with self.assertRaises(ValueError):
            analyzer.run_analysis("total_expense", "monthly", "2023-01-01", "2023-01-31")
