from apps.trashcan.services import TrashService

from .models import Category


class CategoryService:
    @staticmethod
    def soft_delete(user_id: int, category_id: int) -> None:
        TrashService.soft_delete(Category, user_id, category_id)

    @staticmethod
    def restore(user_id: int, category_id: int) -> None:
        TrashService.restore(Category, user_id, category_id)
