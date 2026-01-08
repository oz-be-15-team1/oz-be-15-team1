from django.db.models import QuerySet
from django.utils import timezone

from .models import Tag


class TagRepository:
    _LIST_ONLY_FIELDS = ("id", "user_id", "name", "color", "deleted_at", "created_at")

    @staticmethod
    def list_alive(user_id: int) -> QuerySet[Tag]:
        # 정상 목록: 삭제 안 된 것만 + 필요한 필드만 + 이름 정렬
        return (
            Tag.objects
            .filter(user_id=user_id, deleted_at__isnull=True)
            .only(*TagRepository._LIST_ONLY_FIELDS)
            .order_by("name")
        )

    @staticmethod
    def list_deleted(user_id: int) -> QuerySet[Tag]:
        # 휴지통 목록: 삭제된 것만 + 필요한 필드만 + 최근 삭제 순
        return (
            Tag.objects
            .filter(user_id=user_id, deleted_at__isnull=False)
            .only(*TagRepository._LIST_ONLY_FIELDS)
            .order_by("-deleted_at")
        )

    @staticmethod
    def get_alive(user_id: int, tag_id: int) -> Tag:
        # get은 단건이므로 기존처럼 유지
        return Tag.objects.get(id=tag_id, user_id=user_id, deleted_at__isnull=True)

    @staticmethod
    def get_deleted(user_id: int, tag_id: int) -> Tag:
        return Tag.objects.get(id=tag_id, user_id=user_id, deleted_at__isnull=False)

    @staticmethod
    def soft_delete(user_id: int, tag_id: int) -> int:
        #  휴지통으로 보내기: UPDATE 1번
        return (
            Tag.objects
            .filter(id=tag_id, user_id=user_id, deleted_at__isnull=True)
            .update(deleted_at=timezone.now())
        )

    @staticmethod
    def restore(user_id: int, tag_id: int) -> int:
        #  복구: UPDATE 1번
        return (
            Tag.objects
            .filter(id=tag_id, user_id=user_id, deleted_at__isnull=False)
            .update(deleted_at=None)
        )
