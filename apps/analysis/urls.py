from django.urls import include, path
from rest_framework.routers import DefaultRouter

from . import views

router = DefaultRouter()
router.register(r"analyses", views.AnalysisViewSet)

urlpatterns = [
    path("analyses/period/", views.AnalysisListView.as_view(), name="analysis-period-list"),
    path("", include(router.urls)),
]
