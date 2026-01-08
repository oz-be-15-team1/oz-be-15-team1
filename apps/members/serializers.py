from rest_framework import serializers

from .models import User


# 사용자 회원가입 요청 데이터 스펙 (Request Body)
class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ["email", "password", "name", 'phone']

    def create(self, validated_data):
        password = validated_data.pop("password")
        user = User(**validated_data)
        user.set_password(password)  # 비밀번호 암호화
        user.save()
        return user


# 사용자 회원가입 응답 데이터 스펙 (Response Body)
class UserSignupResponseSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "email", "name", 'phone']


# 사용자 로그인 요청 데이터 스펙 (Request Body)
class UserLoginRequestSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)


# 사용자 로그인 응답 데이터 스펙 (Response Body)
class UserLoginResponseSerializer(serializers.Serializer):
    user = UserSignupResponseSerializer()
    token = serializers.CharField()


# 회원정보 조회, 수정
class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'email', 'name', 'phone']
        read_only_fields = ['id', 'email']


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
