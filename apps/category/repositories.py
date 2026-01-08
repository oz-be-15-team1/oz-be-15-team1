from django.db.models import QuerySet
from django.utils import timezone

from .models import Category


class CategoryRepository:
    # 목록 화면에서 보통 필요한 필드만 읽도록 제한
    _LIST_ONLY_FIELDS = ("id", "user_id", "name", "kind", "parent_id", "deleted_at", "created_at")

    @staticmethod
    def list_alive(user_id: int) -> QuerySet[Category]:
        # 정상 목록: 삭제 안 된 것만 + 필요한 필드만 + 이름 정렬
        return (
            Category.objects
            .filter(user_id=user_id, deleted_at__isnull=True)
            .only(*CategoryRepository._LIST_ONLY_FIELDS)
            .order_by("name")
        )

    @staticmethod
    def list_deleted(user_id: int) -> QuerySet[Category]:
        # 휴지통 목록: 삭제된 것만 + 필요한 필드만 + 최근 삭제 순
        return (
            Category.objects
            .filter(user_id=user_id, deleted_at__isnull=False)
            .only(*CategoryRepository._LIST_ONLY_FIELDS)
            .order_by("-deleted_at")
        )

    @staticmethod
    def get_alive(user_id: int, category_id: int) -> Category:
        # 단건 조회는 기존처럼 유지 
        return Category.objects.get(id=category_id, user_id=user_id, deleted_at__isnull=True)

    @staticmethod
    def get_deleted(user_id: int, category_id: int) -> Category:
        return Category.objects.get(id=category_id, user_id=user_id, deleted_at__isnull=False)


    @staticmethod
    def soft_delete(user_id: int, category_id: int) -> int:
        # 휴지통으로 보내기: UPDATE 1번
        return (
            Category.objects
            .filter(id=category_id, user_id=user_id, deleted_at__isnull=True)
            .update(deleted_at=timezone.now())
        )

    @staticmethod
    def restore(user_id: int, category_id: int) -> int:
        # 복구: UPDATE 1번
        return (
            Category.objects
            .filter(id=category_id, user_id=user_id, deleted_at__isnull=False)
            .update(deleted_at=None)
        )
