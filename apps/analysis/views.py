from django_celery_results.models import TaskResult
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import generics, status, viewsets
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Analysis
from .serializers import AnalysisSerializer
from .tasks import run_user_analysis


class AnalysisViewSet(viewsets.ModelViewSet):
    """
    분석 관리 API

    사용자의 거래 분석 데이터를 조회, 생성, 수정, 삭제할 수 있습니다.

    인증: JWT Bearer 토큰 필요
    """
    queryset = Analysis.objects.all()
    serializer_class = AnalysisSerializer

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


class AnalysisListView(generics.ListAPIView):
    """
    분석 목록 필터링 조회 API

    사용자와 기간 타입별로 분석 데이터를 필터링하여 조회합니다.

    인증: JWT Bearer 토큰 필요
    """
    serializer_class = AnalysisSerializer

    def get_queryset(self):
        queryset = Analysis.objects.all()
        if self.request.user and self.request.user.is_authenticated:
            queryset = queryset.filter(user=self.request.user)
        period_type = self.request.query_params.get("type")
        if period_type:
            queryset = queryset.filter(type=period_type)
        return queryset


class AnalysisRunView(APIView):
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
