from django.urls import path

from .views import (
    CategoryDetailView,
    CategoryListCreateView,
    CategoryRestoreView,
    CategoryTrashListView,
)

urlpatterns = [
    # 기존
    path("", CategoryListCreateView.as_view()),
    path("<int:category_id>/", CategoryDetailView.as_view()),
    # 휴지통/복구
    path("trash/", CategoryTrashListView.as_view()),
    path("<int:category_id>/restore/", CategoryRestoreView.as_view()),
]
