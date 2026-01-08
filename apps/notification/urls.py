from django.urls import include, path
from rest_framework.routers import DefaultRouter

from . import views

router = DefaultRouter()
router.register(r"", views.NotificationViewSet, basename="notification")

urlpatterns = [
    path(
        "unread/",
        views.UnreadNotificationListView.as_view(),
        name="notification-unread-list",
    ),
    path(
        "<int:pk>/read/",
        views.NotificationMarkReadView.as_view(),
        name="notification-mark-read",
    ),
    path("", include(router.urls)),
]
