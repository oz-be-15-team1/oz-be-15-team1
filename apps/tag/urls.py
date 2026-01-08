from django.urls import path

from .views import (
    TagDetailView,
    TagListCreateView,
    TagRestoreView,
    TagTrashListView,
)

urlpatterns = [
    path("", TagListCreateView.as_view()),
    path("<int:tag_id>/", TagDetailView.as_view()),
    path("trash/", TagTrashListView.as_view()),
    path("<int:tag_id>/restore/", TagRestoreView.as_view()),
]
