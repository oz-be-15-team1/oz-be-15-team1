from django.urls import path
from .views import (
    CategoryDetailView,
    CategoryListCreateView,
    CategoryRestoreView,
    CategoryTrashListView,
)

app_name = "category"

urlpatterns = [
    path("categories/", CategoryListCreateView.as_view()),
    path("categories/<int:category_id>/", CategoryDetailView.as_view()),
    path("categories/trash/", CategoryTrashListView.as_view()),
    path("categories/<int:category_id>/restore/", CategoryRestoreView.as_view()),
]
