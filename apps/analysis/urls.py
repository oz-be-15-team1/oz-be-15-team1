from django.urls import include, path
from rest_framework.routers import DefaultRouter

from . import views

router = DefaultRouter()
router.register(r"", views.AnalysisViewSet, basename="analysis")

urlpatterns = [
    path("period/", views.AnalysisListView.as_view(), name="analysis-period-list"),
    path("run/", views.AnalysisRunView.as_view(), name="analysis-run"),
    path(
        "tasks/<str:task_id>/", views.AnalysisTaskStatusView.as_view(), name="analysis-task-status"
    ),
    path("", include(router.urls)),
]
