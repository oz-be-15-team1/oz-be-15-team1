from django.urls import include, path
from rest_framework.routers import DefaultRouter

from . import views

router = DefaultRouter()
router.register(r"", views.AnalysisViewSet, basename="analysis")

urlpatterns = [
    path("period/", views.AnalysisListView.as_view(), name="analysis-period-list"),
    path("", include(router.urls)),
]
