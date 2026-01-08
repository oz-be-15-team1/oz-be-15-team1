from typing import Type

from django.db import models
from django.utils import timezone
from rest_framework.exceptions import NotFound


class TrashService:
    """
    공통 Soft Delete / Restore / Trash list 서비스

    모델에 아래 필드가 있어야 함:
    - deleted_at (DateTimeField, null=True)
    - user (ForeignKey) 또는 owner 같은 사용자 필드 (기본: user)
    """

    user_field_name = "user" 

    @classmethod
    def _base_qs(cls, model: Type[models.Model], user_id: int):
        if not hasattr(model, "deleted_at"):
            raise RuntimeError(f"{model.__name__} 모델에 deleted_at 필드가 없습니다.")
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
        """
            최적화 포인트:
        - 객체를 가져와서 save() 하지 않고, UPDATE 1번으로 처리
        - 이미 삭제된 경우에도 안전하게 동작(0 rows updated)
        """
        qs = cls._base_qs(model, user_id).filter(**{id_field: obj_id})
        # 존재 여부 확인(없는 경우 404)
        if not qs.exists():
            raise NotFound("Not found.")

        # deleted_at이 NULL인 경우만 삭제 처리 (중복 호출 방지)
        updated = qs.filter(deleted_at__isnull=True).update(deleted_at=timezone.now())

        # 리턴 타입 유지: 기존처럼 obj 반환
        # (상태가 이미 deleted였든 방금 deleted됐든 최종 상태를 반환)
        return qs.first()

    @classmethod
    def restore(cls, model: Type[models.Model], user_id: int, obj_id: int, id_field="id"):
        """
            최적화 포인트:
        - 객체를 가져와서 save() 하지 않고, UPDATE 1번으로 처리
        - 이미 복구된 경우에도 안전하게 동작(0 rows updated)
        """
        qs = cls._base_qs(model, user_id).filter(**{id_field: obj_id})
        if not qs.exists():
            raise NotFound("Not found.")

        # deleted_at이 NOT NULL인 경우만 복구 처리
        updated = qs.filter(deleted_at__isnull=False).update(deleted_at=None)

        return qs.first()
