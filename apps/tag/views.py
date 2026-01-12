from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
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
    """
    태그 목록 조회 및 생성 API

    - GET: 사용자의 활성 태그 목록 조회
    - POST: 새로운 태그 생성

    요청 예시 (POST /api/tags/):
    {
        "name": "고정지출",
        "color": "#3366FF"
    }

    응답 예시 (201 Created):
    {
        "id": 1,
        "name": "고정지출",
        "color": "#3366FF",
        "created_at": "2026-01-08T10:00:00Z"
    }

    상태 코드:
    - 200 OK: 목록 조회 성공
    - 201 Created: 태그 생성 성공
    - 400 Bad Request: 유효성 검증 실패
    - 401 Unauthorized: 인증 실패

    인증: JWT Bearer 토큰 필요
    """

    permission_classes = [IsAuthenticated]
    serializer_class = TagReadSerializer

    @swagger_auto_schema(
        operation_summary="태그 목록 조회",
        operation_description="사용자의 모든 활성 태그를 조회합니다.",
        responses={
            200: openapi.Response("태그 목록 조회 성공", TagReadSerializer(many=True)),
            401: "인증 실패",
        },
        tags=["태그 관리"],
    )
    def get(self, request):
        qs = TagRepository.list_alive(request.user.id)
        return Response(TagReadSerializer(qs, many=True).data)

    @swagger_auto_schema(
        operation_summary="태그 생성",
        operation_description="새로운 태그를 생성합니다.",
        request_body=TagCreateUpdateSerializer,
        responses={
            201: openapi.Response("태그 생성 성공", TagReadSerializer),
            400: "유효성 검증 실패",
            401: "인증 실패",
        },
        tags=["태그 관리"],
    )
    def post(self, request):
        ser = TagCreateUpdateSerializer(data=request.data)
        ser.is_valid(raise_exception=True)
        obj = ser.save(user=request.user)
        return Response(TagReadSerializer(obj).data, status=status.HTTP_201_CREATED)


class TagDetailView(APIView):
    """
    태그 상세 조회, 수정, 삭제 API

    - GET: 특정 태그 상세 조회
    - PATCH: 태그 부분 수정
    - DELETE: 태그 삭제 (소프트 삭제)

    요청 예시 (PATCH /api/tags/{id}/):
    {
        "name": "변동지출",
        "color": "#FF3366"
    }

    응답 예시 (200 OK):
    {
        "id": 1,
        "name": "변동지출",
        "color": "#FF3366",
        "updated_at": "2026-01-08T11:00:00Z"
    }

    상태 코드:
    - 200 OK: 조회/수정 성공
    - 204 No Content: 삭제 성공
    - 400 Bad Request: 유효성 검증 실패
    - 401 Unauthorized: 인증 실패
    - 404 Not Found: 태그를 찾을 수 없음

    인증: JWT Bearer 토큰 필요
    """

    permission_classes = [IsAuthenticated]
    serializer_class = TagReadSerializer

    @swagger_auto_schema(
        operation_summary="태그 상세 조회",
        operation_description="특정 태그의 상세 정보를 조회합니다.",
        responses={
            200: openapi.Response("태그 조회 성공", TagReadSerializer),
            401: "인증 실패",
            404: "태그를 찾을 수 없음",
        },
        tags=["태그 관리"],
    )
    def get(self, request, tag_id: int):
        obj = TagRepository.get_alive(request.user.id, tag_id)
        return Response(TagReadSerializer(obj).data)

    @swagger_auto_schema(
        operation_summary="태그 수정",
        operation_description="태그 정보를 부분적으로 수정합니다.",
        request_body=TagCreateUpdateSerializer,
        responses={
            200: openapi.Response("태그 수정 성공", TagReadSerializer),
            400: "유효성 검증 실패",
            401: "인증 실패",
            404: "태그를 찾을 수 없음",
        },
        tags=["태그 관리"],
    )
    def patch(self, request, tag_id: int):
        obj = TagRepository.get_alive(request.user.id, tag_id)
        ser = TagCreateUpdateSerializer(obj, data=request.data, partial=True)
        ser.is_valid(raise_exception=True)
        obj = ser.save()
        return Response(TagReadSerializer(obj).data)

    @swagger_auto_schema(
        operation_summary="태그 삭제",
        operation_description="태그를 소프트 삭제합니다. 휴지통으로 이동됩니다.",
        responses={
            204: "태그 삭제 성공",
            401: "인증 실패",
            404: "태그를 찾을 수 없음",
        },
        tags=["태그 관리"],
    )
    def delete(self, request, tag_id: int):
        TrashService.soft_delete(Tag, request.user.id, tag_id)
        return Response(status=status.HTTP_204_NO_CONTENT)


class TagTrashListView(TrashListAPIView):
    model = Tag
    serializer_class = TagReadSerializer

    @swagger_auto_schema(
        operation_summary="태그 휴지통 목록 조회",
        operation_description="삭제된 태그 목록을 조회합니다.",
        responses={
            200: openapi.Response("휴지통 목록 조회 성공", TagReadSerializer(many=True)),
            401: "인증 실패",
        },
        tags=["태그 관리"],
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)


class TagRestoreView(RestoreAPIView):
    model = Tag

    @swagger_auto_schema(
        operation_summary="태그 복원",
        operation_description="휴지통의 태그를 복원합니다.",
        responses={
            200: "태그 복원 성공",
            401: "인증 실패",
            404: "태그를 찾을 수 없음",
        },
        tags=["태그 관리"],
    )
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)
