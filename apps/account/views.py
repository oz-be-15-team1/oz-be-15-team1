from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import permissions, status, viewsets
from rest_framework.exceptions import MethodNotAllowed
from rest_framework.response import Response

from .models import Account
from .serializers import AccountCreateRequestSerializer, AccountResponseSerializer


class AccountViewSet(viewsets.ModelViewSet):
    """
    계좌 관리 API

    사용자의 계좌를 생성, 조회, 삭제할 수 있습니다.
    계좌 정보는 생성 이후 수정할 수 없습니다.

    엔드포인트:
    - GET /api/accounts/ : 사용자의 모든 계좌 목록 조회
    - POST /api/accounts/ : 새로운 계좌 생성
    - GET /api/accounts/{id}/ : 특정 계좌 상세 조회
    - DELETE /api/accounts/{id}/ : 계좌 삭제

    요청 예시 (POST /api/accounts/):
    {
        "name": "신한은행 입출금",
        "account_number": "110-123-456789",
        "bank_name": "신한은행",
        "balance": 1000000
    }

    응답 예시 (201 Created):
    {
        "id": 1,
        "name": "신한은행 입출금",
        "account_number": "110-123-456789",
        "bank_name": "신한은행",
        "balance": 1000000,
        "created_at": "2026-01-08T10:00:00Z"
    }

    상태 코드:
    - 200 OK: 조회 성공
    - 201 Created: 계좌 생성 성공
    - 204 No Content: 계좌 삭제 성공
    - 400 Bad Request: 유효성 검증 실패
    - 401 Unauthorized: 인증 실패
    - 404 Not Found: 계좌를 찾을 수 없음

    인증: JWT Bearer 토큰 필요
    """

    # 모든 요청에 인증 필요
    permission_classes = [permissions.IsAuthenticated]

    # 계좌 정보는 생성 이후 수정 불가: PUT/PATCH 차단
    http_method_names = ["get", "post", "delete", "head", "options"]

    # 사용자는 본인의 계좌만 조회/생성 가능
    def get_queryset(self):
        # select_related로 user 정보를 한 번에 가져와 N+1 문제 해결
        return Account.objects.select_related("user").filter(user=self.request.user)

    # 생성 동작일 때 특정 시리얼라이저 사용
    def get_serializer_class(self):
        if self.action == "create":
            return AccountCreateRequestSerializer
        return AccountResponseSerializer

    # 계좌 생성 시 현재 사용자와 연동
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    @swagger_auto_schema(
        operation_summary="계좌 생성",
        operation_description="새로운 계좌를 생성합니다. 계좌는 생성 후 수정할 수 없습니다.",
        request_body=AccountCreateRequestSerializer,
        responses={
            201: openapi.Response("계좌 생성 성공", AccountResponseSerializer),
            400: "유효성 검증 실패",
            401: "인증 실패",
        },
        tags=["계좌 관리"],
    )
    def create(self, request, *args, **kwargs):
        # 생성 요청 시리얼라이저로 유효성 검사
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        # 생성 수행
        self.perform_create(serializer)
        # 응답은 AccountResponseSerializer 사용
        instance = serializer.instance
        response_serializer = AccountResponseSerializer(instance)
        return Response(response_serializer.data, status=status.HTTP_201_CREATED)

    @swagger_auto_schema(
        operation_summary="계좌 목록 조회",
        operation_description="사용자의 모든 계좌 목록을 조회합니다.",
        responses={
            200: openapi.Response("계좌 목록 조회 성공", AccountResponseSerializer(many=True)),
            401: "인증 실패",
        },
        tags=["계좌 관리"],
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="계좌 상세 조회",
        operation_description="특정 계좌의 상세 정보를 조회합니다.",
        responses={
            200: openapi.Response("계좌 상세 조회 성공", AccountResponseSerializer),
            401: "인증 실패",
            404: "계좌를 찾을 수 없음",
        },
        tags=["계좌 관리"],
    )
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)

    # update/partial_update 호출 시 명시적 예외 반환(필수X)
    def update(self, request, *args, **kwargs):
        raise MethodNotAllowed("PUT")

    def partial_update(self, request, *args, **kwargs):
        raise MethodNotAllowed("PATCH")

    @swagger_auto_schema(
        operation_summary="계좌 삭제",
        operation_description="계좌를 삭제합니다. 관련된 모든 거래도 함께 삭제됩니다.",
        responses={
            204: "계좌 삭제 성공",
            401: "인증 실패",
            404: "계좌를 찾을 수 없음",
        },
        tags=["계좌 관리"],
    )
    # 계좌 삭제: 소유자만 가능하며 관련 트랜잭션은 DB 제약(on_delete=models.CASCADE)에 따라 삭제
    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
