"""
Authentication views: register, login (JWT), refresh, profile.
"""
from django.contrib.auth import get_user_model
from rest_framework import generics, status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenRefreshView

from .serializers import (
    EmailTokenObtainPairSerializer,
    RegisterSerializer,
    UserSerializer,
)

User = get_user_model()


def _tokens_for_user(user):
    """Issue access + refresh pair for a user."""
    refresh = RefreshToken.for_user(user)
    return {
        "refresh": str(refresh),
        "access": str(refresh.access_token),
    }


class RegisterView(generics.CreateAPIView):
    """
    POST /api/auth/register/
    Public — creates user and returns JWT tokens.
    """

    serializer_class = RegisterSerializer
    permission_classes = (AllowAny,)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        return Response(
            {
                "success": True,
                "message": "Registration successful.",
                "user": UserSerializer(user).data,
                "tokens": _tokens_for_user(user),
            },
            status=status.HTTP_201_CREATED,
        )


class LoginView(APIView):
    """
    POST /api/auth/login/
    Public — accepts email + password, returns JWT.
    """

    permission_classes = (AllowAny,)

    def post(self, request):
        serializer = EmailTokenObtainPairSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data["user"]
        return Response(
            {
                "success": True,
                "message": "Login successful.",
                "user": UserSerializer(user).data,
                "tokens": {
                    "access": serializer.validated_data["access"],
                    "refresh": serializer.validated_data["refresh"],
                },
            }
        )


class RefreshTokenView(TokenRefreshView):
    """POST /api/auth/refresh/ — exchange refresh token for new access token."""

    permission_classes = (AllowAny,)


class ProfileView(APIView):
    """GET /api/auth/me/ — current authenticated user."""

    permission_classes = (IsAuthenticated,)

    def get(self, request):
        return Response(
            {
                "success": True,
                "user": UserSerializer(request.user).data,
            }
        )


class LogoutView(APIView):
    """
    POST /api/auth/logout/
    Blacklists refresh token (requires token_blacklist app).
    """

    permission_classes = (IsAuthenticated,)

    def post(self, request):
        try:
            refresh = request.data.get("refresh")
            if refresh:
                token = RefreshToken(refresh)
                token.blacklist()
        except Exception:
            return Response(
                {"success": False, "message": "Invalid refresh token."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        return Response({"success": True, "message": "Logged out successfully."})
