from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from apps.members.models import User

from .models import Notification


class NotificationModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email="test@example.com", password="testpass123", name="Test User"
        )

    def test_notification_creation(self):
        notification = Notification.objects.create(
            user=self.user, message="새로운 거래가 등록되었습니다.", is_read=False
        )
        self.assertEqual(notification.user, self.user)
        self.assertEqual(notification.message, "새로운 거래가 등록되었습니다.")
        self.assertFalse(notification.is_read)

    def test_notification_str_method(self):
        notification = Notification.objects.create(
            user=self.user,
            message="긴 메시지가 포함된 알림입니다. 이 메시지는 50자를 초과합니다.",
            is_read=True,
        )
        expected_str = (
            f"{self.user.email} - 긴 메시지가 포함된 알림입니다. 이 메시지는 50자를 초과합니다."
        )
        self.assertEqual(str(notification), expected_str)


class NotificationAPITest(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email="api@example.com", password="apitest123", name="API User"
        )
        self.other_user = User.objects.create_user(
            email="other@example.com",
            password="othertest123",
            name="Other User",
        )
        self.client.force_authenticate(user=self.user)

    def test_get_unread_notifications_list(self):
        Notification.objects.create(user=self.user, message="읽지 않은 알림", is_read=False)
        Notification.objects.create(user=self.user, message="읽은 알림", is_read=True)
        Notification.objects.create(user=self.other_user, message="다른 유저 알림", is_read=False)
        url = reverse("notification-unread-list")
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertFalse(response.data[0]["is_read"])
        self.assertEqual(response.data[0]["user"], self.user.id)

    def test_mark_notification_as_read(self):
        notification = Notification.objects.create(
            user=self.user, message="읽지 않은 알림", is_read=False
        )
        url = reverse("notification-mark-read", kwargs={"pk": notification.pk})
        response = self.client.patch(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        notification.refresh_from_db()
        self.assertTrue(notification.is_read)

    def test_get_notifications_list(self):
        url = reverse("notification-list")
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_create_notification(self):
        url = reverse("notification-list")
        data = {"user": self.user.id, "message": "테스트 알림 메시지", "is_read": False}
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Notification.objects.count(), 1)
        self.assertEqual(Notification.objects.get().message, "테스트 알림 메시지")

    def test_get_notification_detail(self):
        notification = Notification.objects.create(
            user=self.user, message="상세 조회 테스트 알림", is_read=False
        )
        url = reverse("notification-detail", kwargs={"pk": notification.pk})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["message"], "상세 조회 테스트 알림")

    def test_update_notification(self):
        notification = Notification.objects.create(
            user=self.user, message="읽지 않은 알림", is_read=False
        )
        url = reverse("notification-detail", kwargs={"pk": notification.pk})
        data = {"is_read": True}
        response = self.client.patch(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        notification.refresh_from_db()
        self.assertTrue(notification.is_read)

    def test_delete_notification(self):
        notification = Notification.objects.create(
            user=self.user, message="삭제할 알림", is_read=False
        )
        url = reverse("notification-detail", kwargs={"pk": notification.pk})
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Notification.objects.count(), 0)
