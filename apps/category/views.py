from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
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
    """
    카테고리 목록 조회 및 생성 API

    - GET: 사용자의 활성 카테고리 목록 조회
    - POST: 새로운 카테고리 생성

    요청 예시 (POST /api/categories/):
    {
        "name": "식비",
        "color": "#FF5733",
        "icon": "🍔"
    }

    응답 예시 (201 Created):
    {
        "id": 1,
        "name": "식비",
        "color": "#FF5733",
        "icon": "🍔",
        "created_at": "2026-01-08T10:00:00Z"
    }

    상태 코드:
    - 200 OK: 목록 조회 성공
    - 201 Created: 카테고리 생성 성공
    - 400 Bad Request: 유효성 검증 실패
    - 401 Unauthorized: 인증 실패

    인증: JWT Bearer 토큰 필요
    """

    permission_classes = [IsAuthenticated]
    serializer_class = CategoryReadSerializer

    @swagger_auto_schema(
        operation_summary="카테고리 목록 조회",
        operation_description="사용자의 모든 활성 카테고리를 조회합니다.",
        responses={
            200: openapi.Response("카테고리 목록 조회 성공", CategoryReadSerializer(many=True)),
            401: "인증 실패",
        },
        tags=["카테고리 관리"],
    )
    def get(self, request):
        qs = CategoryRepository.list_alive(request.user.id)
        return Response(CategoryReadSerializer(qs, many=True).data)

    @swagger_auto_schema(
        operation_summary="카테고리 생성",
        operation_description="새로운 카테고리를 생성합니다.",
        request_body=CategoryCreateUpdateSerializer,
        responses={
            201: openapi.Response("카테고리 생성 성공", CategoryReadSerializer),
            400: "유효성 검증 실패",
            401: "인증 실패",
        },
        tags=["카테고리 관리"],
    )
    def post(self, request):
        ser = CategoryCreateUpdateSerializer(data=request.data)
        ser.is_valid(raise_exception=True)
        obj = ser.save(user=request.user)
        return Response(CategoryReadSerializer(obj).data, status=status.HTTP_201_CREATED)


class CategoryDetailView(APIView):
    """
    카테고리 상세 조회, 수정, 삭제 API

    - GET: 특정 카테고리 상세 조회
    - PATCH: 카테고리 부분 수정
    - DELETE: 카테고리 삭제 (소프트 삭제)

    요청 예시 (PATCH /api/categories/{id}/):
    {
        "name": "외식비",
        "color": "#33FF57"
    }

    응답 예시 (200 OK):
    {
        "id": 1,
        "name": "외식비",
        "color": "#33FF57",
        "icon": "🍔",
        "updated_at": "2026-01-08T11:00:00Z"
    }

    상태 코드:
    - 200 OK: 조회/수정 성공
    - 204 No Content: 삭제 성공
    - 400 Bad Request: 유효성 검증 실패
    - 401 Unauthorized: 인증 실패
    - 404 Not Found: 카테고리를 찾을 수 없음

    인증: JWT Bearer 토큰 필요
    """

    permission_classes = [IsAuthenticated]
    serializer_class = CategoryReadSerializer

    @swagger_auto_schema(
        operation_summary="카테고리 상세 조회",
        operation_description="특정 카테고리의 상세 정보를 조회합니다.",
        responses={
            200: openapi.Response("카테고리 조회 성공", CategoryReadSerializer),
            401: "인증 실패",
            404: "카테고리를 찾을 수 없음",
        },
        tags=["카테고리 관리"],
    )
    def get(self, request, category_id: int):
        obj = CategoryRepository.get_alive(request.user.id, category_id)
        return Response(CategoryReadSerializer(obj).data)

    @swagger_auto_schema(
        operation_summary="카테고리 수정",
        operation_description="카테고리 정보를 부분적으로 수정합니다.",
        request_body=CategoryCreateUpdateSerializer,
        responses={
            200: openapi.Response("카테고리 수정 성공", CategoryReadSerializer),
            400: "유효성 검증 실패",
            401: "인증 실패",
            404: "카테고리를 찾을 수 없음",
        },
        tags=["카테고리 관리"],
    )
    def patch(self, request, category_id: int):
        obj = CategoryRepository.get_alive(request.user.id, category_id)
        ser = CategoryCreateUpdateSerializer(obj, data=request.data, partial=True)
        ser.is_valid(raise_exception=True)
        obj = ser.save()
        return Response(CategoryReadSerializer(obj).data)

    @swagger_auto_schema(
        operation_summary="카테고리 삭제",
        operation_description="카테고리를 소프트 삭제합니다. 휴지통으로 이동됩니다.",
        responses={
            204: "카테고리 삭제 성공",
            401: "인증 실패",
            404: "카테고리를 찾을 수 없음",
        },
        tags=["카테고리 관리"],
    )
    def delete(self, request, category_id: int):
        TrashService.soft_delete(Category, request.user.id, category_id)
        return Response(status=status.HTTP_204_NO_CONTENT)


class CategoryTrashListView(TrashListAPIView):
    model = Category
    serializer_class = CategoryReadSerializer


class CategoryRestoreView(RestoreAPIView):
    model = Category
