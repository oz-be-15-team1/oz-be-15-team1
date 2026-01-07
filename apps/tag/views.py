from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.trashcan.services import TrashService
from apps.trashcan.views import RestoreAPIView, TrashListAPIView

from .models import Tag
from .repositories import TagRepository
from .serializers import TagCreateUpdateSerializer, TagReadSerializer


class TagListCreateView(APIView):
    permission_classes = [IsAuthenticated]
    serializer_class = TagReadSerializer

    def get(self, request):
        qs = TagRepository.list_alive(request.user.id)
        return Response(TagReadSerializer(qs, many=True).data)

    def post(self, request):
        ser = TagCreateUpdateSerializer(data=request.data)
        ser.is_valid(raise_exception=True)
        obj = ser.save(user=request.user)
        return Response(TagReadSerializer(obj).data, status=status.HTTP_201_CREATED)


class TagDetailView(APIView):
    permission_classes = [IsAuthenticated]
    serializer_class = TagReadSerializer

    def get(self, request, tag_id: int):
        obj = TagRepository.get_alive(request.user.id, tag_id)
        return Response(TagReadSerializer(obj).data)

    def patch(self, request, tag_id: int):
        obj = TagRepository.get_alive(request.user.id, tag_id)
        ser = TagCreateUpdateSerializer(obj, data=request.data, partial=True)
        ser.is_valid(raise_exception=True)
        obj = ser.save()
        return Response(TagReadSerializer(obj).data)

    def delete(self, request, tag_id: int):
        TrashService.soft_delete(Tag, request.user.id, tag_id)
        return Response(status=status.HTTP_204_NO_CONTENT)


class TagTrashListView(TrashListAPIView):
    model = Tag
    serializer_class = TagReadSerializer

class TagRestoreView(RestoreAPIView):
    model = Tag
