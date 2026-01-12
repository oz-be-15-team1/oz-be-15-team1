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
