from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import generics, viewsets

from .models import Analysis
from .serializers import AnalysisSerializer


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

    @swagger_auto_schema(
        operation_summary="분석 목록 필터링 조회",
        operation_description="사용자와 기간 타입별로 분석 데이터를 필터링하여 조회합니다.",
        manual_parameters=[
            openapi.Parameter('type', openapi.IN_QUERY, description="기간 타입 (예: monthly, weekly)", type=openapi.TYPE_STRING),
        ],
        responses={
            200: openapi.Response("분석 목록 조회 성공", AnalysisSerializer(many=True)),
            401: "인증 실패",
        },
        tags=["분석 관리"],
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)
