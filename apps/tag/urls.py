from django.urls import path

from .views import (
    TagDetailView,
    TagListCreateView,
    TagRestoreView,
    TagTrashListView,
)

app_name = "tag"

urlpatterns = [
    path("tags/", TagListCreateView.as_view()),
    path("tags/<int:tag_id>/", TagDetailView.as_view()),
    path("tags/trash/", TagTrashListView.as_view()),
    path("tags/<int:tag_id>/restore/", TagRestoreView.as_view()),
]
