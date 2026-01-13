from django.contrib.auth import authenticate
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import permissions, status
from rest_framework.authentication import SessionAuthentication
from rest_framework.generics import GenericAPIView
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken

from .serializers import (
    RegisterSerializer,
    UserLoginRequestSerializer,
    UserLoginResponseSerializer,
    UserProfileSerializer,
    UserSignupResponseSerializer,
)


# 회원가입 view
class UserSignupView(GenericAPIView):
    serializer_class = RegisterSerializer
    permission_classes = [permissions.AllowAny]

    @swagger_auto_schema(
        operation_summary="회원가입",
        operation_description="새로운 사용자 계정을 생성합니다.",
        request_body=RegisterSerializer,
        responses={
            201: openapi.Response("회원가입 성공", UserSignupResponseSerializer),
            400: "유효성 검증 실패",
        },
        tags=["회원 관리"],
    )
    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)  # 유효성 검증
        user = serializer.save()  # create() 호출 → 비밀번호 암호화 포함

        response_data = UserSignupResponseSerializer(user).data
        return Response(response_data, status=status.HTTP_201_CREATED)


# 로그인 view
class UserLoginView(GenericAPIView):
    serializer_class = UserLoginRequestSerializer
    permission_classes = [permissions.AllowAny]

    @swagger_auto_schema(
        operation_summary="로그인",
        operation_description="사용자 인증 후 JWT 액세스 토큰과 리프레시 토큰을 발급합니다.",
        request_body=UserLoginRequestSerializer,
        responses={
            200: openapi.Response("로그인 성공", UserLoginResponseSerializer),
            401: "이메일 또는 비밀번호 불일치",
        },
        tags=["회원 관리"],
    )
    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        email = serializer.validated_data["email"]
        password = serializer.validated_data["password"]

        user = authenticate(request, email=email, password=password)
        if not user:
            return Response({"detail": "잘못된 자격 증명"}, status=status.HTTP_401_UNAUTHORIZED)

        refresh = RefreshToken.for_user(user)
        access_token = str(refresh.access_token)

        response_data = {"user": UserSignupResponseSerializer(user).data, "token": access_token}

        response = Response(response_data, status=status.HTTP_200_OK)
        response.set_cookie(
            key="refresh_token",
            value=str(refresh),
            httponly=True,
            secure=True,
            samesite="Lax",
            max_age=7 * 24 * 60 * 60,
        )

        return response


# 로그아웃 view
class UserLogoutView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    @swagger_auto_schema(
        operation_summary="로그아웃",
        operation_description="사용자 로그아웃 및 토큰을 블랙리스트에 추가합니다.",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=["refresh"],
            properties={
                "refresh": openapi.Schema(type=openapi.TYPE_STRING, description="리프레시 토큰"),
            },
        ),
        responses={
            200: "로그아웃 성공",
            400: "잘못된 요청",
            401: "인증 실패",
        },
        tags=["회원 관리"],
    )
    def post(self, request):
        refresh_token = request.data.get("refresh")
        if not refresh_token:
            return Response(
                {"detail": "Refresh token required"}, status=status.HTTP_400_BAD_REQUEST
            )

        try:
            token = RefreshToken(refresh_token)
            token.blacklist()
        except Exception:
            return Response({"detail": "Invalid token"}, status=status.HTTP_400_BAD_REQUEST)

        return Response({"detail": "Logout successful"}, status=status.HTTP_200_OK)


class UserProfileView(GenericAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = UserProfileSerializer

    @swagger_auto_schema(
        operation_summary="프로필 조회",
        operation_description="로그인한 사용자의 프로필 정보를 조회합니다.",
        responses={
            200: openapi.Response("프로필 조회 성공", UserProfileSerializer),
            401: "인증 실패",
        },
        tags=["회원 관리"],
    )
    def get(self, request):
        # 본인 프로필 조회
        serializer = self.get_serializer(request.user)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @swagger_auto_schema(
        operation_summary="프로필 수정",
        operation_description="로그인한 사용자의 프로필 정보를 수정합니다.",
        request_body=UserProfileSerializer,
        responses={
            200: openapi.Response("프로필 수정 성공", UserProfileSerializer),
            400: "유효성 검증 실패",
            401: "인증 실패",
        },
        tags=["회원 관리"],
    )
    def patch(self, request):
        # 본인 프로필 일부 수정
        serializer = self.get_serializer(request.user, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)

    @swagger_auto_schema(
        operation_summary="계정 삭제",
        operation_description="로그인한 사용자의 계정을 비활성화합니다.",
        responses={
            200: "계정 삭제 성공",
            401: "인증 실패",
        },
        tags=["회원 관리"],
    )
    def delete(self, request):
        # 본인 계정 삭제
        request.user.is_active = False
        request.user.save(update_fields=["is_active"])
        return Response({"detail": "Deleted successfully"}, status=status.HTTP_200_OK)


class SocialTokenView(APIView):
    """
    소셜 로그인 세션을 JWT 토큰으로 교환하는 API
    """

    authentication_classes = [SessionAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    @swagger_auto_schema(
        operation_summary="소셜 로그인 토큰 발급",
        operation_description="소셜 로그인 세션을 JWT 토큰으로 교환합니다.",
        responses={
            200: openapi.Response("토큰 발급 성공", UserLoginResponseSerializer),
            401: "인증 실패",
        },
        tags=["회원 관리"],
    )
    def get(self, request):
        user = request.user
        refresh = RefreshToken.for_user(user)
        access_token = str(refresh.access_token)

        response_data = {"user": UserSignupResponseSerializer(user).data, "token": access_token}
        response = Response(response_data, status=status.HTTP_200_OK)
        response.set_cookie(
            key="refresh_token",
            value=str(refresh),
            httponly=True,
            secure=True,
            samesite="Lax",
            max_age=7 * 24 * 60 * 60,
        )
        return response


"""
    로그인 API

    사용자 인증 후 JWT 액세스 토큰과 리프레시 토큰을 발급합니다.

    요청 예시 (Request Body):
    {
        "email": "user@example.com",
        "password": "securepassword123"
    }

    응답 예시 (Response):
    {
        "user": {
            "id": 1,
            "email": "user@example.com",
            "username": "홍길동"
        },
        "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
    }

    상태 코드 (Status Codes):
    - 200 OK: 로그인 성공
    - 400 Bad Request: 유효성 검증 실패 (필수 필드 누락)
    - 401 Unauthorized: 이메일 또는 비밀번호 불일치

    참고: 리프레시 토큰은 HttpOnly 쿠키로 설정됩니다.

    인증: 불필요
    """
