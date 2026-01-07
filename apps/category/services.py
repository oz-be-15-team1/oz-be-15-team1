from .repositories import CategoryRepository


class CategoryService:
    @staticmethod
    def soft_delete(user_id: int, category_id: int) -> None:
        obj = CategoryRepository.get_alive(user_id, category_id)
        obj.soft_delete()

    @staticmethod
    def restore(user_id: int, category_id: int) -> None:
        obj = CategoryRepository.get_deleted(user_id, category_id)
        obj.restore()
