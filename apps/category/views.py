from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.trashcan.services import TrashService
from apps.trashcan.views import RestoreAPIView, TrashListAPIView

from .models import Category
from .repositories import CategoryRepository
from .serializers import CategoryCreateUpdateSerializer, CategoryReadSerializer


class CategoryListCreateView(APIView):
    permission_classes = [IsAuthenticated]
    serializer_class = CategoryReadSerializer

    def get(self, request):
        qs = CategoryRepository.list_alive(request.user.id)
        return Response(CategoryReadSerializer(qs, many=True).data)

    def post(self, request):
        ser = CategoryCreateUpdateSerializer(data=request.data)
        ser.is_valid(raise_exception=True)
        obj = ser.save(user=request.user)
        return Response(CategoryReadSerializer(obj).data, status=status.HTTP_201_CREATED)


class CategoryDetailView(APIView):
    permission_classes = [IsAuthenticated]
    serializer_class = CategoryReadSerializer

    def get(self, request, category_id: int):
        obj = CategoryRepository.get_alive(request.user.id, category_id)
        return Response(CategoryReadSerializer(obj).data)

    def patch(self, request, category_id: int):
        obj = CategoryRepository.get_alive(request.user.id, category_id)
        ser = CategoryCreateUpdateSerializer(obj, data=request.data, partial=True)
        ser.is_valid(raise_exception=True)
        obj = ser.save()
        return Response(CategoryReadSerializer(obj).data)

    def delete(self, request, category_id: int):
        TrashService.soft_delete(Category, request.user.id, category_id)
        return Response(status=status.HTTP_204_NO_CONTENT)

class CategoryTrashListView(TrashListAPIView):
    model = Category
    serializer_class = CategoryReadSerializer

class CategoryRestoreView(RestoreAPIView):
    model = Category
