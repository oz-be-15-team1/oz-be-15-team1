from django.db.models import QuerySet
from .models import Category


class CategoryRepository:
    @staticmethod
    def list_alive(user_id: int) -> QuerySet[Category]:
        return Category.objects.filter(user_id=user_id, deleted_at__isnull=True)

    @staticmethod
    def list_deleted(user_id: int) -> QuerySet[Category]:
        return Category.objects.filter(user_id=user_id, deleted_at__isnull=False)

    @staticmethod
    def get_alive(user_id: int, category_id: int) -> Category:
        return Category.objects.get(id=category_id, user_id=user_id, deleted_at__isnull=True)

    @staticmethod
    def get_deleted(user_id: int, category_id: int) -> Category:
        return Category.objects.get(id=category_id, user_id=user_id, deleted_at__isnull=False)
