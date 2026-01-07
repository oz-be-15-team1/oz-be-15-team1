from django.contrib.auth import authenticate
from rest_framework import status
from rest_framework.generics import GenericAPIView
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken

from .serializers import (
    RegisterSerializer,
    UserLoginRequestSerializer,
    UserSignupResponseSerializer,
)


# 회원가입 view
class UserSignupView(GenericAPIView):
    serializer_class = RegisterSerializer

    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)  # 유효성 검증
        user = serializer.save()  # create() 호출 → 비밀번호 암호화 포함

        response_data = UserSignupResponseSerializer(user).data
        return Response(response_data, status=status.HTTP_201_CREATED)

# 로그인 view
class UserLoginView(GenericAPIView):
    serializer_class = UserLoginRequestSerializer

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

        response_data = {
            "user": UserSignupResponseSerializer(user).data,
            "token": access_token
        }

        response = Response(response_data, status=status.HTTP_200_OK)
        response.set_cookie(
            key="refresh_token",
            value=str(refresh),
            httponly=True,
            secure=True,
            samesite="Lax",
            max_age=7*24*60*60
        )

        return response
