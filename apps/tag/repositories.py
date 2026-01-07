from django.db.models import QuerySet
from .models import Tag


class TagRepository:
    @staticmethod
    def list_alive(user_id: int) -> QuerySet[Tag]:
        return Tag.objects.filter(user_id=user_id, deleted_at__isnull=True)

    @staticmethod
    def list_deleted(user_id: int) -> QuerySet[Tag]:
        return Tag.objects.filter(user_id=user_id, deleted_at__isnull=False)

    @staticmethod
    def get_alive(user_id: int, tag_id: int) -> Tag:
        return Tag.objects.get(id=tag_id, user_id=user_id, deleted_at__isnull=True)

    @staticmethod
    def get_deleted(user_id: int, tag_id: int) -> Tag:
        return Tag.objects.get(id=tag_id, user_id=user_id, deleted_at__isnull=False)
