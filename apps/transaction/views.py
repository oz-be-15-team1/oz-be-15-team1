from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import permissions, status, viewsets
from rest_framework.exceptions import MethodNotAllowed
from rest_framework.response import Response

from .models import Transaction

# 요청/응답에 사용할 시리얼라이저들을 가져오기
from .serializers import (
    TransactionCreateRequestSerializer,
    TransactionResponseSerializer,
    TransactionUpdateRequestSerializer,
)

# 서비스 레이어의 create_transaction 함수를 가져오기
from .services import create_transaction


# 거래 관련 REST API 뷰셋 정의
class TransactionViewSet(viewsets.ModelViewSet):
    """
    거래(Transaction) 관리 API

    사용자의 수입/지출 거래를 생성, 조회, 수정, 삭제할 수 있습니다.

    엔드포인트:
    - GET /api/transactions/ : 거래 목록 조회 (필터링 가능)
    - POST /api/transactions/ : 새로운 거래 생성
    - GET /api/transactions/{id}/ : 특정 거래 상세 조회
    - PATCH /api/transactions/{id}/ : 거래 부분 수정
    - DELETE /api/transactions/{id}/ : 거래 삭제

    요청 예시 (POST /api/transactions/):
    {
        "account": 1,
        "amount": 50000,
        "direction": "expense",
        "method": "card",
        "description": "점심 식사",
        "occurred_at": "2026-01-08T12:30:00Z"
    }

    응답 예시 (201 Created):
    {
        "id": 1,
        "account": 1,
        "amount": 50000,
        "direction": "expense",
        "method": "card",
        "description": "점심 식사",
        "occurred_at": "2026-01-08T12:30:00Z",
        "created_at": "2026-01-08T12:30:00Z"
    }

    필터링 파라미터 (GET /api/transactions/):
    - account: 계좌 ID (예: ?account=1)
    - direction: 거래 방향 (예: ?direction=expense)
    - min_amount: 최소 금액 (예: ?min_amount=10000)
    - max_amount: 최대 금액 (예: ?max_amount=100000)
    - start_date: 시작 날짜 (예: ?start_date=2026-01-01)
    - end_date: 종료 날짜 (예: ?end_date=2026-01-31)

    상태 코드:
    - 200 OK: 조회 성공
    - 201 Created: 거래 생성 성공
    - 204 No Content: 거래 삭제 성공
    - 400 Bad Request: 유효성 검증 실패
    - 401 Unauthorized: 인증 실패
    - 404 Not Found: 거래를 찾을 수 없음

    인증: JWT Bearer 토큰 필요
    """

    # 모든 요청에 대해 인증 요구
    permission_classes = [permissions.IsAuthenticated]

    # 허용할 HTTP 메소드 목록을 제한 (부분 수정 허용)
    http_method_names = ["get", "post", "patch", "delete", "head", "options"]

    # 현재 요청 사용자의 계좌에 속한 거래만 조회되도록 제한
    def get_queryset(self):
        # select_related로 account와 user 정보를 한 번에 가져와 N+1 문제 해결
        qs = Transaction.objects.select_related("account", "account__user").filter(
            account__user=self.request.user
        )

        # 필터링: account, direction, 금액 범위, 날짜 범위
        params = self.request.query_params
        account = params.get("account")
        direction = params.get("direction")
        min_amount = params.get("min_amount")
        max_amount = params.get("max_amount")
        start_date = params.get("start_date")
        end_date = params.get("end_date")

        if account:
            qs = qs.filter(account_id=account)
        if direction:
            qs = qs.filter(direction=direction)
        if min_amount:
            qs = qs.filter(amount__gte=min_amount)
        if max_amount:
            qs = qs.filter(amount__lte=max_amount)
        if start_date:
            qs = qs.filter(occurred_at__gte=start_date)
        if end_date:
            qs = qs.filter(occurred_at__lte=end_date)

        return qs

    # 액션에 따라 사용할 시리얼라이저를 결정
    def get_serializer_class(self):
        if self.action == "create":
            # 생성 요청시에는 입력용 시리얼라이저 사용
            return TransactionCreateRequestSerializer
        if self.action in ("partial_update", "update"):
            return TransactionUpdateRequestSerializer
        # 그 외 응답은 응답용 시리얼라이저 사용
        return TransactionResponseSerializer

    @swagger_auto_schema(
        operation_summary="거래 목록 조회",
        operation_description="사용자의 모든 거래를 조회합니다. 계좌, 방향, 금액, 날짜 등으로 필터링할 수 있습니다.",
        manual_parameters=[
            openapi.Parameter('account', openapi.IN_QUERY, description="계좌 ID", type=openapi.TYPE_INTEGER),
            openapi.Parameter('direction', openapi.IN_QUERY, description="거래 방향 (income/expense)", type=openapi.TYPE_STRING),
            openapi.Parameter('min_amount', openapi.IN_QUERY, description="최소 금액", type=openapi.TYPE_NUMBER),
            openapi.Parameter('max_amount', openapi.IN_QUERY, description="최대 금액", type=openapi.TYPE_NUMBER),
            openapi.Parameter('start_date', openapi.IN_QUERY, description="시작 날짜 (YYYY-MM-DD)", type=openapi.TYPE_STRING),
            openapi.Parameter('end_date', openapi.IN_QUERY, description="종료 날짜 (YYYY-MM-DD)", type=openapi.TYPE_STRING),
        ],
        responses={
            200: openapi.Response("거래 목록 조회 성공", TransactionResponseSerializer(many=True)),
            401: "인증 실패",
        },
        tags=["거래 관리"],
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="거래 상세 조회",
        operation_description="특정 거래의 상세 정보를 조회합니다.",
        responses={
            200: openapi.Response("거래 조회 성공", TransactionResponseSerializer),
            401: "인증 실패",
            404: "거래를 찾을 수 없음",
        },
        tags=["거래 관리"],
    )
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)

    # 거래 생성 엔드포인트
    @swagger_auto_schema(
        operation_summary="거래 생성",
        operation_description="새로운 수입/지출 거래를 생성합니다.",
        request_body=TransactionCreateRequestSerializer,
        responses={
            201: openapi.Response("거래 생성 성공", TransactionResponseSerializer),
            400: "유효성 검증 실패",
            401: "인증 실패",
        },
        tags=["거래 관리"],
    )
    def create(self, request, *args, **kwargs):
        # 요청 데이터를 시리얼라이즈/검증
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        # 검증된 데이터 추출
        validated = serializer.validated_data

        # 서비스 레이어를 통해 거래 생성 수행
        tx = create_transaction(
            request.user,
            account_id=validated["account"],
            amount=validated["amount"],
            direction=validated["direction"],
            method=validated["method"],
            description=validated.get("description"),
            occurred_at=validated["occurred_at"],
            tags=validated.get("tags"),
        )

        # 생성된 거래를 응답용 시리얼라이저로 직렬화하여 반환
        out = TransactionResponseSerializer(tx, context={"request": request})
        return Response(out.data, status=status.HTTP_201_CREATED)

    # PUT(전체 업데이트)은 허용하지 않음
    def update(self, request, *args, **kwargs):
        raise MethodNotAllowed("PUT")

    # PATCH(부분 업데이트)을 허용
    @swagger_auto_schema(
        operation_summary="거래 수정",
        operation_description="거래 정보를 부분적으로 수정합니다.",
        request_body=TransactionUpdateRequestSerializer,
        responses={
            200: openapi.Response("거래 수정 성공", TransactionResponseSerializer),
            400: "유효성 검증 실패",
            401: "인증 실패",
            404: "거래를 찾을 수 없음",
        },
        tags=["거래 관리"],
    )
    def partial_update(self, request, *args, **kwargs):
        instance = self.get_object()

        serializer = TransactionUpdateRequestSerializer(data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        validated = serializer.validated_data

        # 허용된 필드들만 업데이트
        for attr, val in validated.items():
            if attr == "tags":
                instance.tags.set(val)
                continue
            setattr(instance, attr, val)
        instance.save()

        out = TransactionResponseSerializer(instance, context={"request": request})
        return Response(out.data, status=status.HTTP_200_OK)

    # 거래 삭제 엔드포인트
    @swagger_auto_schema(
        operation_summary="거래 삭제",
        operation_description="거래를 삭제합니다.",
        responses={
            204: "거래 삭제 성공",
            401: "인증 실패",
            404: "거래를 찾을 수 없음",
        },
        tags=["거래 관리"],
    )
    def destroy(self, request, *args, **kwargs):
        # 객체를 조회하여 삭제하고 간단 메시지를 반환
        instance = self.get_object()
        instance.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
