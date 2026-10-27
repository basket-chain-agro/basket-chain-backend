from django.contrib.auth import logout
from rest_framework import generics, permissions, serializers, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenRefreshView as SimpleJWTRefreshView

from .models import User
from .serializers import LoginSerializer, RegisterSerializer, UserSerializer


class LogoutResponseSerializer(serializers.Serializer):
    detail = serializers.CharField(read_only=True)


class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    permission_classes = [permissions.AllowAny]
    serializer_class = RegisterSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        refresh = RefreshToken.for_user(user)
        response = {
            "success": True,
            "message": "Registration successful.",
            "data": {
                "user": UserSerializer(user).data,
                "tokens": {
                    "access": str(refresh.access_token),
                    "refresh": str(refresh),
                },
            },
        }
        return Response(response, status=status.HTTP_201_CREATED)


class LoginView(APIView):
    permission_classes = [permissions.AllowAny]
    serializer_class = LoginSerializer

    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data["user"]
        refresh = RefreshToken.for_user(user)
        response = {
            "success": True,
            "message": "Login successful.",
            "data": {
                "user": UserSerializer(user).data,
                "tokens": {
                    "access": str(refresh.access_token),
                    "refresh": str(refresh),
                },
            },
        }
        return Response(response, status=status.HTTP_200_OK)


class LogoutView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = LogoutResponseSerializer

    def post(self, request):
        refresh_token = request.data.get("refresh")
        if not refresh_token:
            return Response(
                {"success": False, "message": "Validation failed.",
                    "errors": {"refresh": ["This field is required."]}},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            token = RefreshToken(refresh_token)
            token.blacklist()
        except Exception:
            return Response(
                {"success": False, "message": "Invalid or expired refresh token.",
                    "errors": {"refresh": ["Token is invalid or expired."]}},
                status=status.HTTP_401_UNAUTHORIZED,
            )

        logout(request)
        return Response({"success": True, "message": "Logout successful.", "data": None}, status=status.HTTP_200_OK)


class RefreshTokenView(SimpleJWTRefreshView):
    def post(self, request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)
        payload = {
            "success": True,
            "message": "Token refreshed successfully.",
            "data": {
                "access": response.data.get("access"),
                "refresh": response.data.get("refresh"),
            },
        }
        return Response(payload, status=response.status_code)


class CurrentUserView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = UserSerializer

    def get(self, request):
        serializer = UserSerializer(request.user)
        return Response(
            {"success": True, "message": "User retrieved successfully.",
                "data": serializer.data},
            status=status.HTTP_200_OK,
        )
