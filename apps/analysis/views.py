from django_celery_results.models import TaskResult
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import generics, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.trashcan.services import TrashService

from .models import Analysis
from .serializers import AnalysisSerializer
from .tasks import run_user_analysis


class AnalysisViewSet(viewsets.ModelViewSet):
    """
    분석 관리 API

    사용자의 거래 분석 데이터를 조회, 생성, 수정, 삭제할 수 있습니다.

    인증: JWT Bearer 토큰 필요
    """

    serializer_class = AnalysisSerializer

    def get_queryset(self):
        return TrashService.list_alive(Analysis, self.request.user.id)

    @swagger_auto_schema(
        operation_summary="분석 목록 조회",
        operation_description="모든 분석 데이터를 조회합니다.",
        responses={
            200: openapi.Response("분석 목록 조회 성공", AnalysisSerializer(many=True)),
            401: "인증 실패",
        },
        tags=["분석 관리"],
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="분석 조회",
        operation_description="특정 분석 데이터를 조회합니다.",
        responses={
            200: openapi.Response("분석 조회 성공", AnalysisSerializer),
            401: "인증 실패",
            404: "분석 데이터를 찾을 수 없음",
        },
        tags=["분석 관리"],
    )
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="분석 생성",
        operation_description="새로운 분석 데이터를 생성합니다.",
        request_body=AnalysisSerializer,
        responses={
            201: openapi.Response("분석 생성 성공", AnalysisSerializer),
            400: "유효성 검증 실패",
            401: "인증 실패",
        },
        tags=["분석 관리"],
    )
    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="분석 전체 수정",
        operation_description="분석 데이터를 전체 수정합니다.",
        request_body=AnalysisSerializer,
        responses={
            200: openapi.Response("분석 수정 성공", AnalysisSerializer),
            400: "유효성 검증 실패",
            401: "인증 실패",
            404: "분석 데이터를 찾을 수 없음",
        },
        tags=["분석 관리"],
    )
    def update(self, request, *args, **kwargs):
        return super().update(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="분석 부분 수정",
        operation_description="분석 데이터를 부분 수정합니다.",
        request_body=AnalysisSerializer,
        responses={
            200: openapi.Response("분석 수정 성공", AnalysisSerializer),
            400: "유효성 검증 실패",
            401: "인증 실패",
            404: "분석 데이터를 찾을 수 없음",
        },
        tags=["분석 관리"],
    )
    def partial_update(self, request, *args, **kwargs):
        return super().partial_update(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="분석 삭제",
        operation_description="분석 데이터를 삭제합니다(휴지통으로 이동).",
        responses={
            204: "분석 삭제 성공",
            401: "인증 실패",
            404: "분석 데이터를 찾을 수 없음",
        },
        tags=["분석 관리"],
    )
    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        TrashService.soft_delete(Analysis, request.user.id, instance.id)
        return Response(status=status.HTTP_204_NO_CONTENT)

    @swagger_auto_schema(
        operation_summary="분석 휴지통 목록 조회",
        operation_description="삭제된(휴지통에 있는) 분석 데이터를 조회합니다.",
        responses={
            200: openapi.Response("분석 휴지통 목록 조회 성공", AnalysisSerializer(many=True)),
            401: "인증 실패",
        },
        tags=["분석 관리"],
    )
    @action(detail=False, methods=["get"], url_path="trash")
    def trash(self, request, *args, **kwargs):
        qs = TrashService.list_deleted(Analysis, request.user.id)
        serializer = AnalysisSerializer(qs, many=True, context={"request": request})
        return Response(serializer.data, status=status.HTTP_200_OK)

    @swagger_auto_schema(
        operation_summary="분석 복구",
        operation_description="삭제된(휴지통에 있는) 분석 데이터를 복구합니다.",
        responses={
            200: openapi.Response("분석 복구 성공", AnalysisSerializer),
            401: "인증 실패",
            404: "분석 데이터를 찾을 수 없음",
        },
        tags=["분석 관리"],
    )
    @action(detail=True, methods=["post"], url_path="restore")
    def restore(self, request, *args, **kwargs):
        instance = TrashService.restore(Analysis, request.user.id, kwargs.get("pk"))
        serializer = AnalysisSerializer(instance, context={"request": request})
        return Response(serializer.data, status=status.HTTP_200_OK)


class AnalysisListView(generics.ListAPIView):
    """
    분석 목록 필터링 조회 API

    사용자와 기간 타입별로 분석 데이터를 필터링하여 조회합니다.

    인증: JWT Bearer 토큰 필요
    """

    serializer_class = AnalysisSerializer

    @swagger_auto_schema(
        operation_summary="분석 목록 필터링 조회",
        operation_description="사용자와 기간 타입별로 분석 데이터를 필터링하여 조회합니다.",
        manual_parameters=[
            openapi.Parameter(
                "type",
                openapi.IN_QUERY,
                description="기간 타입",
                type=openapi.TYPE_STRING,
            ),
        ],
        responses={
            200: openapi.Response("분석 목록 조회 성공", AnalysisSerializer(many=True)),
            401: "인증 실패",
        },
        tags=["분석 관리"],
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    def get_queryset(self):
        queryset = TrashService.list_alive(Analysis, self.request.user.id)
        period_type = self.request.query_params.get("type")
        if period_type:
            queryset = queryset.filter(type=period_type)
        return queryset


class AnalysisRunView(APIView):
    """
    분석 실행 요청 API

    분석 유형과 기간 정보를 받아 비동기 분석 작업을 시작합니다.
    """

    @swagger_auto_schema(
        operation_summary="분석 실행 요청",
        operation_description="분석 유형과 기간 정보를 받아 비동기 분석 작업을 시작합니다.",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=["about", "type", "period_start", "period_end"],
            properties={
                "about": openapi.Schema(type=openapi.TYPE_STRING, description="분석 유형"),
                "type": openapi.Schema(type=openapi.TYPE_STRING, description="기간 타입"),
                "period_start": openapi.Schema(
                    type=openapi.TYPE_STRING, format=openapi.FORMAT_DATE, description="시작 날짜"
                ),
                "period_end": openapi.Schema(
                    type=openapi.TYPE_STRING, format=openapi.FORMAT_DATE, description="종료 날짜"
                ),
            },
        ),
        responses={
            202: openapi.Response(
                "분석 작업 시작됨",
                openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={"task_id": openapi.Schema(type=openapi.TYPE_STRING)},
                ),
            ),
            400: "잘못된 요청",
            401: "인증 실패",
        },
        tags=["분석 관리"],
    )
    def post(self, request):
        analysis_type = request.data.get("about")
        period_type = request.data.get("type")
        period_start = request.data.get("period_start")
        period_end = request.data.get("period_end")

        if not all([analysis_type, period_type, period_start, period_end]):
            return Response(
                {"detail": "about, type, period_start, period_end 값이 필요합니다."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        task = run_user_analysis.delay(
            request.user.id,
            analysis_type,
            period_type,
            period_start,
            period_end,
        )
        return Response({"task_id": task.id}, status=status.HTTP_202_ACCEPTED)


class AnalysisTaskStatusView(APIView):
    """
    분석 작업 상태 조회 API

    Celery task_id 기준으로 작업 상태를 조회합니다.
    """

    @swagger_auto_schema(
        operation_summary="분석 작업 상태 조회",
        operation_description="Celery task_id 기준으로 작업 상태를 조회합니다.",
        responses={
            200: openapi.Response(
                "작업 상태 조회 성공",
                openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        "status": openapi.Schema(type=openapi.TYPE_STRING),
                        "result": openapi.Schema(type=openapi.TYPE_STRING),
                        "date_done": openapi.Schema(
                            type=openapi.TYPE_STRING, format=openapi.FORMAT_DATETIME
                        ),
                    },
                ),
            ),
            401: "인증 실패",
        },
        tags=["분석 관리"],
    )
    def get(self, request, task_id):
        task = TaskResult.objects.filter(task_id=task_id).first()
        if not task:
            return Response({"status": "PENDING"}, status=status.HTTP_200_OK)
        return Response(
            {
                "status": task.status,
                "result": task.result,
                "date_done": task.date_done,
            },
            status=status.HTTP_200_OK,
        )
