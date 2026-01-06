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
