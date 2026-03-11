from django.conf import settings
from rest_framework import generics, status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken

from .models import User
from .serializers import RegisterSerializer, UserSerializer, TelegramCheckSerializer, TelegramBindSerializer, TelegramLoginSerializer

import os
from dotenv import load_dotenv
load_dotenv()

BOT_SECRET = os.getenv('BOT_SECRET')

class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = RegisterSerializer
    permission_classes = [AllowAny]


class MeView(generics.RetrieveAPIView):
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return self.request.user


class TelegramCheckView(APIView):
    permission_classes = []

    def post(self, request):
        if request.headers.get("X-BOT-SECRET") != BOT_SECRET:
            return Response({"detail": "Unauthorized"}, status=403)

        serializer = TelegramCheckSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        return Response(
            {
                "registered": serializer.validated_data["registered"],
                "needs_phone": serializer.validated_data["needs_phone"],
            },
            status=status.HTTP_200_OK,
        )


class TelegramBindView(APIView):
    permission_classes = []

    def post(self, request):
        if request.headers.get("X-BOT-SECRET") != BOT_SECRET:
            return Response({"detail": "Unauthorized"}, status=403)

        serializer = TelegramBindSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = serializer.validated_data["user"]
        refresh = RefreshToken.for_user(user)

        return Response(
            {
                "access_token": str(refresh.access_token),
                "refresh_token": str(refresh),
            },
            status=status.HTTP_200_OK,
        )


class TelegramLoginView(APIView):
    permission_classes = []

    def post(self, request):
        if request.headers.get("X-BOT-SECRET") != BOT_SECRET:
            return Response({"detail": "Unauthorized"}, status=403)

        serializer = TelegramLoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = serializer.validated_data["user"]
        refresh = RefreshToken.for_user(user)

        return Response(
            {
                "access_token": str(refresh.access_token),
                "refresh_token": str(refresh),
            },
            status=status.HTTP_200_OK,
        )
