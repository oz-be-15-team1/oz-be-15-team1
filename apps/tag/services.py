from .repositories import TagRepository


class TagService:
    @staticmethod
    def soft_delete(user_id: int, tag_id: int) -> None:
        tag = TagRepository.get_alive(user_id, tag_id)
        tag.soft_delete()

    @staticmethod
    def restore(user_id: int, tag_id: int) -> None:
        tag = TagRepository.get_deleted(user_id, tag_id)
        tag.restore()
