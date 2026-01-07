
from rest_framework import permissions, status, viewsets
from rest_framework.exceptions import MethodNotAllowed
from rest_framework.response import Response

from .models import Account
from .serializers import AccountCreateRequestSerializer, AccountResponseSerializer


class AccountViewSet(viewsets.ModelViewSet):
    # 모든 요청에 인증 필요
    permission_classes = [permissions.IsAuthenticated]
    
    # 계좌 정보는 생성 이후 수정 불가: PUT/PATCH 차단
    http_method_names = ["get", "post", "delete", "head", "options"]

    # 사용자는 본인의 계좌만 조회/생성 가능
    def get_queryset(self):
        # select_related로 user 정보를 한 번에 가져와 N+1 문제 해결
        return Account.objects.select_related('user').filter(user=self.request.user)

    # 생성 동작일 때 특정 시리얼라이저 사용
    def get_serializer_class(self):
        if self.action == "create":
            return AccountCreateRequestSerializer
        return AccountResponseSerializer

    # 계좌 생성 시 현재 사용자와 연동
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

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

    # update/partial_update 호출 시 명시적 예외 반환(필수X)
    def update(self, request, *args, **kwargs):
        raise MethodNotAllowed("PUT")

    def partial_update(self, request, *args, **kwargs):
        raise MethodNotAllowed("PATCH")

    # 계좌 삭제: 소유자만 가능하며 관련 트랜잭션은 DB 제약(on_delete=models.CASCADE)에 따라 삭제
    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

