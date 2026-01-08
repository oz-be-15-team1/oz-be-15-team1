from django.shortcuts import get_object_or_404
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import generics, status, viewsets
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Notification
from .serializers import NotificationSerializer


class NotificationViewSet(viewsets.ModelViewSet):
    """
    알림 관리 API

    사용자의 알림을 조회, 생성, 수정, 삭제할 수 있습니다.

    인증: JWT Bearer 토큰 필요
    """
    queryset = Notification.objects.all()
    serializer_class = NotificationSerializer

    @swagger_auto_schema(
        operation_summary="알림 목록 조회",
        operation_description="모든 알림을 조회합니다.",
        responses={
            200: openapi.Response("알림 목록 조회 성공", NotificationSerializer(many=True)),
            401: "인증 실패",
        },
        tags=["알림 관리"],
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="알림 조회",
        operation_description="특정 알림의 상세 정보를 조회합니다.",
        responses={
            200: openapi.Response("알림 조회 성공", NotificationSerializer),
            401: "인증 실패",
            404: "알림을 찾을 수 없음",
        },
        tags=["알림 관리"],
    )
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)


class UnreadNotificationListView(generics.ListAPIView):
    """
    읽지 않은 알림 목록 조회 API

    사용자의 읽지 않은 알림만 조회합니다.

    인증: JWT Bearer 토큰 필요
    """
    serializer_class = NotificationSerializer

    def get_queryset(self):
        return Notification.objects.filter(user=self.request.user, is_read=False)

    @swagger_auto_schema(
        operation_summary="읽지 않은 알림 목록 조회",
        operation_description="사용자의 읽지 않은 알림만 조회합니다.",
        responses={
            200: openapi.Response("읽지 않은 알림 목록 조회 성공", NotificationSerializer(many=True)),
            401: "인증 실패",
        },
        tags=["알림 관리"],
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)


class NotificationMarkReadView(APIView):
    """
    알림 읽음 처리 API

    특정 알림을 읽음 상태로 변경합니다.

    인증: JWT Bearer 토큰 필요
    """

    @swagger_auto_schema(
        operation_summary="알림 읽음 처리",
        operation_description="특정 알림을 읽음 상태로 표시합니다.",
        responses={
            200: openapi.Response("알림 읽음 처리 성공", NotificationSerializer),
            401: "인증 실패",
            404: "알림을 찾을 수 없음",
        },
        tags=["알림 관리"],
    )
    def patch(self, request, pk):
        notification = get_object_or_404(Notification, pk=pk, user=request.user)
        notification.is_read = True
        notification.save(update_fields=["is_read"])
        serializer = NotificationSerializer(notification)
        return Response(serializer.data, status=status.HTTP_200_OK)
