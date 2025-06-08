import uuid

from allauth.account.models import EmailConfirmation, EmailConfirmationHMAC
from allauth.account.views import ConfirmEmailView
from django.shortcuts import render
from django.views.generic import TemplateView
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from .permissions import IsAuthenticated

from users.models import PasswordReset
from users.serializers import (
    PasswordResetRequestSerializer,
    PasswordResetConfirmSerializer,
)
from django.contrib.auth import get_user_model
from rest_framework import status

User = get_user_model()


class CustomConfirmEmailView(ConfirmEmailView):
    def get(self, *args, **kwargs):
        self.object = self.get_object()

        if self.object:
            self.object.confirm(self.request)
            return render(self.request, "verification_success.html")
        else:
            return render(self.request, "verification_failed.html")

    def get_object(self, queryset=None):
        key = self.kwargs.get("key")
        print(f"Получен ключ: {key}")

        confirmation = EmailConfirmationHMAC.from_key(key)
        if confirmation:
            print("Найден через HMAC")
            return confirmation

        try:
            confirmation = EmailConfirmation.objects.get(key=key.lower())
            print("Найден через ORM")
        except EmailConfirmation.DoesNotExist:
            print("Не найден ключ в базе данных")
            confirmation = None

        return confirmation


class VerificationSuccessView(TemplateView):
    template_name = "verification_success.html"


class PasswordResetRequestView(APIView):
    permission_classes = (AllowAny,)
    serializer_class = PasswordResetRequestSerializer

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        email = serializer.validated_data["email"]

        try:
            user = User.objects.get(email=email)

            try:
                password_reset = PasswordReset.objects.get(
                    user=user, used=False)
                password_reset.reset_token = uuid.uuid4().hex[:6].upper()
                password_reset.save()
            except PasswordReset.DoesNotExist:
                password_reset = PasswordReset.objects.create(
                    user=user, reset_token=uuid.uuid4().hex[:6].upper()
                )

            serializer.send_reset_email(user, password_reset)

            return Response(
                {"message": "Код для сброса пароля отправлен на ваш email."},
                status=status.HTTP_200_OK,
            )

        except User.DoesNotExist:
            return Response(
                {"error": "Пользователь с указанным email не найден."},
                status=status.HTTP_400_BAD_REQUEST,
            )


class PasswordResetConfirmView(APIView):
    permission_classes = (AllowAny,)
    serializer_class = PasswordResetConfirmSerializer

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)

        email = serializer.validated_data["email"]
        code = serializer.validated_data["code"]

        try:
            user = User.objects.get(email=email)

            try:
                password_reset = PasswordReset.objects.get(
                    user=user, reset_token=code, used=False
                )

                if password_reset.is_expired:
                    return Response(
                        {"error": "Код сброса пароля истёк. Запросите новый код."},
                        status=status.HTTP_400_BAD_REQUEST,
                    )

                serializer.save(user=user)

                password_reset.used = True
                password_reset.save()

                return Response(
                    {"message": "Пароль успешно изменен."},
                    status=status.HTTP_200_OK,
                )

            except PasswordReset.DoesNotExist:
                return Response(
                    {"error": "Недействительный код сброса пароля."},
                    status=status.HTTP_400_BAD_REQUEST,
                )

        except User.DoesNotExist:
            return Response(
                {"error": "Пользователь с указанным email не найден."},
                status=status.HTTP_400_BAD_REQUEST,
            )


class UpdateDeviceTokenView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        user = request.user
        device_token = request.data.get("device_token")

        if not device_token:
            return Response(
                {"error": "Необходимо указать device_token"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        user.device_token = device_token
        user.save(update_fields=["device_token"])

        return Response(
            {"success": "Токен устройства успешно обновлен"},
            status=status.HTTP_200_OK,
        )
