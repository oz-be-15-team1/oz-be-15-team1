from django.db import models
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .services import TrashService


class TrashListAPIView(APIView):
    """
    GET /<resource>/trash/
    하위 클래스에서 model, serializer_class 지정하면 됨.
    """

    permission_classes = [IsAuthenticated]
    model: type[models.Model] = None
    serializer_class = None
    id_field = "id"

    def get(self, request):
        qs = TrashService.list_deleted(self.model, request.user.id)
        return Response(self.serializer_class(qs, many=True).data)


class RestoreAPIView(APIView):
    """
    POST /<resource>/{id}/restore/
    하위 클래스에서 model 지정하면 됨.
    """

    permission_classes = [IsAuthenticated]
    model: type[models.Model] = None
    id_field = "id"

    def post(self, request, **kwargs):
        obj_id = kwargs.get("obj_id") or kwargs.get("id") or kwargs.get("pk")
        TrashService.restore(self.model, request.user.id, obj_id, id_field=self.id_field)
        return Response(status=200)
