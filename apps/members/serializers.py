from rest_framework import serializers

from .models import User


# 사용자 회원가입 요청 데이터 스펙 (Request Body)
class UserSignupRequestSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)
    name = serializers.CharField()
    nickname = serializers.CharField()
    phone = serializers.CharField(required=False, allow_blank=True)


# 사용자 회원가입 응답 데이터 스펙 (Response Body)
class UserSignupResponseSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "email", "name", "nickname", "phone"]


# 사용자 로그인 요청 데이터 스펙 (Request Body)
class UserLoginRequestSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)


# 사용자 로그인 응답 데이터 스펙 (Response Body)
class UserLoginResponseSerializer(serializers.Serializer):
    user = UserSignupResponseSerializer()
    token = serializers.CharField()


# 사용자 프로필 응답 데이터 스펙 (Response Body)
class UserProfileResponseSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "email", "name", "nickname", "phone", "date_joined"]


# 사용자 프로필 수정 요청 데이터 스펙 (Request Body)
class UserProfileUpdateRequestSerializer(serializers.Serializer):
    name = serializers.CharField(required=False)
    nickname = serializers.CharField(required=False)
    phone = serializers.CharField(required=False, allow_blank=True)


"""
사용자 관련 API 엔드포인트 스펙 설명

1. 회원가입
POST /api/users/signup/
Request Body: UserSignupRequestSerializer
Response Body: UserSignupResponseSerializer
Status Code: 201 Created (성공), 400 Bad Request (유효성 오류), 409 Conflict (이메일 중복)

2. 로그인
POST /api/users/login/
Request Body: UserLoginRequestSerializer
Response Body: UserLoginResponseSerializer
Status Code: 200 OK (성공), 400 Bad Request (잘못된 자격 증명), 401 Unauthorized

3. 로그아웃
POST /api/users/logout/
Request Body: 없음
Response Body: {"message": "로그아웃 성공"}
Status Code: 200 OK

4. 프로필 조회
GET /api/users/profile/
Request Body: 없음
Response Body: UserProfileResponseSerializer
Status Code: 200 OK, 401 Unauthorized

5. 프로필 수정
PUT /api/users/profile/
Request Body: UserProfileUpdateRequestSerializer
Response Body: UserProfileResponseSerializer
Status Code: 200 OK, 400 Bad Request, 401 Unauthorized
"""
