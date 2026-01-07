from django.urls import include, path
from rest_framework.routers import DefaultRouter

from . import views

router = DefaultRouter()
router.register(r"notifications", views.NotificationViewSet)

urlpatterns = [
    path("", include(router.urls)),
    path(
        "notifications/unread/",
        views.UnreadNotificationListView.as_view(),
        name="notification-unread-list",
    ),
    path(
        "notifications/<int:pk>/read/",
        views.NotificationMarkReadView.as_view(),
        name="notification-mark-read",
    ),
]
