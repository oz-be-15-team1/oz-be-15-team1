from rest_framework import serializers

from .models import Account


# 계정 생성 요청 데이터 스펙 (Request Body)
class AccountCreateRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = Account
        fields = [
            "name",
            "source_type",
            "balance",
            "account_number",
            "bank_code",
            "account_type",
            "card_company",
            "card_number",
            "billing_day",
        ]


# 계정 응답 데이터 스펙 (Response Body)
class AccountResponseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Account
        fields = [
            "id",
            "name",
            "source_type",
            "balance",
            "is_active",
            "account_number",
            "bank_code",
            "account_type",
            "card_company",
            "card_number",
            "billing_day",
            "created_at",
            "updated_at",
        ]


# 계정 수정 요청 데이터 스펙 (Request Body)
class AccountUpdateRequestSerializer(serializers.Serializer):
    name = serializers.CharField(required=False)
    balance = serializers.DecimalField(max_digits=14, decimal_places=2, required=False)
    is_active = serializers.BooleanField(required=False)
    account_number = serializers.CharField(required=False, allow_blank=True)
    bank_code = serializers.CharField(required=False, allow_blank=True)
    account_type = serializers.CharField(required=False, allow_blank=True)
    card_company = serializers.CharField(required=False, allow_blank=True)
    card_number = serializers.CharField(required=False, allow_blank=True)
    billing_day = serializers.IntegerField(required=False, allow_null=True)


"""
계정 관련 API 엔드포인트 스펙 설명

1. 계정 목록 조회
GET /api/accounts/
Query Params: source_type (선택), is_active (선택)
Response Body: AccountResponseSerializer (리스트)
Status Code: 200 OK, 401 Unauthorized

2. 계정 생성
POST /api/accounts/
Request Body: AccountCreateRequestSerializer
Response Body: AccountResponseSerializer
Status Code: 201 Created, 400 Bad Request, 401 Unauthorized

3. 계정 상세 조회
GET /api/accounts/{id}/
Response Body: AccountResponseSerializer
Status Code: 200 OK, 404 Not Found, 401 Unauthorized

4. 계정 수정
PUT /api/accounts/{id}/
Request Body: AccountUpdateRequestSerializer
Response Body: AccountResponseSerializer
Status Code: 200 OK, 400 Bad Request, 404 Not Found, 401 Unauthorized

5. 계정 삭제
DELETE /api/accounts/{id}/
Response Body: {"message": "계정 삭제 성공"}
Status Code: 204 No Content, 404 Not Found, 401 Unauthorized
"""
