from rest_framework import serializers

from apps.tag.models import Tag
from apps.tag.serializers import TagReadSerializer

from .models import Transaction


# 거래 생성 요청 데이터 스펙 (Request Body)
class TransactionCreateRequestSerializer(serializers.ModelSerializer):
    tags = serializers.PrimaryKeyRelatedField(queryset=Tag.objects.all(), many=True, required=False)

    class Meta:
        model = Transaction
        fields = ["account", "amount", "direction", "method", "description", "occurred_at", "tags"]


# 거래 응답 데이터 스펙 (Response Body)
class TransactionResponseSerializer(serializers.ModelSerializer):
    account_name = serializers.CharField(source="account.name", read_only=True)
    tags = TagReadSerializer(many=True, read_only=True)

    class Meta:
        model = Transaction
        fields = [
            "id",
            "account",
            "account_name",
            "amount",
            "balance_after",
            "direction",
            "method",
            "description",
            "tags",
            "occurred_at",
            "created_at",
            "updated_at",
        ]


# 거래 수정 요청 데이터 스펙 (Request Body)
class TransactionUpdateRequestSerializer(serializers.Serializer):
    amount = serializers.DecimalField(max_digits=14, decimal_places=2, required=False)
    direction = serializers.ChoiceField(choices=Transaction.DIRECTION_CHOICES, required=False)
    method = serializers.CharField(required=False)
    description = serializers.CharField(required=False, allow_blank=True)
    occurred_at = serializers.DateTimeField(required=False)
    tags = serializers.PrimaryKeyRelatedField(queryset=Tag.objects.all(), many=True, required=False)


"""
거래 관련 API 엔드포인트 스펙 설명

1. 거래 목록 조회
GET /api/transactions/
Query Params: account (선택), direction (선택), start_date (선택), end_date (선택)
Response Body: TransactionResponseSerializer (리스트)
Status Code: 200 OK, 401 Unauthorized

2. 거래 생성
POST /api/transactions/
Request Body: TransactionCreateRequestSerializer
Response Body: TransactionResponseSerializer
Status Code: 201 Created, 400 Bad Request, 401 Unauthorized

3. 거래 상세 조회
GET /api/transactions/{id}/
Response Body: TransactionResponseSerializer
Status Code: 200 OK, 404 Not Found, 401 Unauthorized

4. 거래 수정
PUT /api/transactions/{id}/
Request Body: TransactionUpdateRequestSerializer
Response Body: TransactionResponseSerializer
Status Code: 200 OK, 400 Bad Request, 404 Not Found, 401 Unauthorized

5. 거래 삭제
DELETE /api/transactions/{id}/
Response Body: {"message": "거래 삭제 성공"}
Status Code: 204 No Content, 404 Not Found, 401 Unauthorized
"""
