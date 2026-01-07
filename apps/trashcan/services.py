# trashcan/services.py
from typing import Type
from django.db import models
from django.utils import timezone
from rest_framework.exceptions import NotFound, PermissionDenied


class TrashService:
    """
    공통 Soft Delete / Restore / Trash list 서비스

    모델에 아래 필드가 있어야 함:
    - deleted_at (DateTimeField, null=True)
    - user (ForeignKey) 또는 owner 같은 사용자 필드 (기본: user)
    """

    user_field_name = "user"  # 프로젝트가 owner이면 "owner"로 바꾸면 됨

    @classmethod
    def _base_qs(cls, model: Type[models.Model], user_id: int):
        if not hasattr(model, "deleted_at"):
            raise RuntimeError(f"{model.__name__} 모델에 deleted_at 필드가 없습니다.")
        # 사용자 소유 데이터만 대상으로 (user_id)
        return model.objects.filter(**{f"{cls.user_field_name}_id": user_id})

    @classmethod
    def list_alive(cls, model: Type[models.Model], user_id: int):
        return cls._base_qs(model, user_id).filter(deleted_at__isnull=True)

    @classmethod
    def list_deleted(cls, model: Type[models.Model], user_id: int):
        return cls._base_qs(model, user_id).filter(deleted_at__isnull=False)

    @classmethod
    def get_alive(cls, model: Type[models.Model], user_id: int, obj_id: int, id_field="id"):
        obj = cls.list_alive(model, user_id).filter(**{id_field: obj_id}).first()
        if not obj:
            raise NotFound("Not found.")
        return obj

    @classmethod
    def soft_delete(cls, model: Type[models.Model], user_id: int, obj_id: int, id_field="id"):
        obj = cls._base_qs(model, user_id).filter(**{id_field: obj_id}).first()
        if not obj:
            raise NotFound("Not found.")
        if obj.deleted_at is None:
            obj.deleted_at = timezone.now()
            obj.save(update_fields=["deleted_at"])
        return obj

    @classmethod
    def restore(cls, model: Type[models.Model], user_id: int, obj_id: int, id_field="id"):
        obj = cls._base_qs(model, user_id).filter(**{id_field: obj_id}).first()
        if not obj:
            raise NotFound("Not found.")
        if obj.deleted_at is not None:
            obj.deleted_at = None
            obj.save(update_fields=["deleted_at"])
        return obj
