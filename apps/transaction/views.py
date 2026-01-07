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
    # 모든 요청에 대해 인증 요구
    permission_classes = [permissions.IsAuthenticated]

    # 허용할 HTTP 메소드 목록을 제한 (부분 수정 허용)
    http_method_names = ["get", "post", "patch", "delete", "head", "options"]

    # 현재 요청 사용자의 계좌에 속한 거래만 조회되도록 제한
    def get_queryset(self):
        qs = Transaction.objects.filter(account__user=self.request.user)

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

    # 거래 생성 엔드포인트
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
        )

        # 생성된 거래를 응답용 시리얼라이저로 직렬화하여 반환
        out = TransactionResponseSerializer(tx, context={"request": request})
        return Response(out.data, status=status.HTTP_201_CREATED)

    # PUT(전체 업데이트)은 허용하지 않음
    def update(self, request, *args, **kwargs):
        raise MethodNotAllowed("PUT")

    # PATCH(부분 업데이트)을 허용
    def partial_update(self, request, *args, **kwargs):
        instance = self.get_object()

        serializer = TransactionUpdateRequestSerializer(data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        validated = serializer.validated_data

        # 허용된 필드들만 업데이트
        for attr, val in validated.items():
            setattr(instance, attr, val)
        instance.save()

        out = TransactionResponseSerializer(instance, context={"request": request})
        return Response(out.data, status=status.HTTP_200_OK)

    # 거래 삭제 엔드포인트
    def destroy(self, request, *args, **kwargs):
        # 객체를 조회하여 삭제하고 간단 메시지를 반환
        instance = self.get_object()
        instance.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

