from apps.trashcan.services import TrashService

from .models import Tag


class TagService:
    @staticmethod
    def soft_delete(user_id: int, tag_id: int) -> None:
        TrashService.soft_delete(Tag, user_id, tag_id)

    @staticmethod
    def restore(user_id: int, tag_id: int) -> None:
        TrashService.restore(Tag, user_id, tag_id)
