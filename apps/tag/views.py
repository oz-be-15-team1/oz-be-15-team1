from django.core.exceptions import ObjectDoesNotExist
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .repositories import TagRepository
from .serializers import TagCreateUpdateSerializer, TagReadSerializer
from .services import TagService


class TagListCreateView(APIView):
    permission_classes = [IsAuthenticated]

    serializer_class = TagReadSerializer

    def get(self, request):
        qs = TagRepository.list_alive(request.user.id)
        return Response(TagReadSerializer(qs, many=True).data)

    def post(self, request):
        serializer = TagCreateUpdateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        tag = serializer.save(user=request.user)
        return Response(
            TagReadSerializer(tag).data,
            status=status.HTTP_201_CREATED,
        )


class TagDetailView(APIView):
    permission_classes = [IsAuthenticated]

    serializer_class = TagReadSerializer

    def get(self, request, tag_id: int):
        try:
            tag = TagRepository.get_alive(request.user.id, tag_id)
        except ObjectDoesNotExist:
            return Response({"detail": "Not found."}, status=404)
        return Response(TagReadSerializer(tag).data)

    def patch(self, request, tag_id: int):
        try:
            tag = TagRepository.get_alive(request.user.id, tag_id)
        except ObjectDoesNotExist:
            return Response({"detail": "Not found."}, status=404)

        serializer = TagCreateUpdateSerializer(tag, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        tag = serializer.save()
        return Response(TagReadSerializer(tag).data)

    def delete(self, request, tag_id: int):
        try:
            TagService.soft_delete(request.user.id, tag_id)
        except ObjectDoesNotExist:
            return Response({"detail": "Not found."}, status=404)
        return Response(status=status.HTTP_204_NO_CONTENT)


class TagTrashListView(APIView):
    permission_classes = [IsAuthenticated]

    serializer_class = TagReadSerializer

    def get(self, request):
        qs = TagRepository.list_deleted(request.user.id)
        return Response(TagReadSerializer(qs, many=True).data)


class TagRestoreView(APIView):
    permission_classes = [IsAuthenticated]

    serializer_class = TagReadSerializer

    def post(self, request, tag_id: int):
        try:
            TagService.restore(request.user.id, tag_id)
        except ObjectDoesNotExist:
            return Response({"detail": "Not found."}, status=404)
        return Response(status=status.HTTP_200_OK)
