import uuid

from allauth.account.models import EmailConfirmation, EmailConfirmationHMAC
from allauth.account.views import ConfirmEmailView
from django.shortcuts import render
from django.views.generic import TemplateView
from drf_spectacular.utils import (
    extend_schema,
    OpenApiResponse,
    OpenApiExample,
    OpenApiParameter,
)
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated

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
        print(f"🔍 Получен ключ: {key}")

        confirmation = EmailConfirmationHMAC.from_key(key)
        if confirmation:
            print("✅ Найден через HMAC")
            return confirmation

        try:
            confirmation = EmailConfirmation.objects.get(key=key.lower())
            print("✅ Найден через ORM")
        except EmailConfirmation.DoesNotExist:
            print("❌ Не найден ключ в базе данных")
            confirmation = None

        return confirmation


class VerificationSuccessView(TemplateView):
    template_name = "verification_success.html"


@extend_schema(
    auth=None,
    tags=["auth"],
    summary="Запрос на сброс пароля",
    description="Этот эндпоинт отправляет письмо с кодом для сброса пароля на указанный email.",
    request=PasswordResetRequestSerializer,
    responses={
        200: OpenApiResponse(
            description="Письмо для сброса пароля отправлено",
            examples=[
                OpenApiExample(
                    "Успешный ответ",
                    value={"message": "Код для сброса пароля отправлен на ваш email."},
                )
            ],
        ),
        400: OpenApiResponse(
            description="Ошибка запроса",
            examples=[
                OpenApiExample(
                    "Email не найден",
                    value={"error": "Пользователь с указанным email не найден."},
                ),
            ],
        ),
    },
)
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
                password_reset = PasswordReset.objects.get(user=user, used=False)
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


@extend_schema(
    auth=None,
    tags=["auth"],
    summary="Подтверждение сброса пароля",
    description="Этот эндпоинт устанавливает новый пароль после проверки кода сброса.",
    request=PasswordResetConfirmSerializer,
    responses={
        200: OpenApiResponse(
            description="Пароль успешно изменен",
            examples=[
                OpenApiExample(
                    "Успешный ответ",
                    value={"message": "Пароль успешно изменен."},
                )
            ],
        ),
        400: OpenApiResponse(
            description="Ошибка запроса",
            examples=[
                OpenApiExample(
                    "Ошибка валидации",
                    value={
                        "password": ["Пароль должен содержать не менее 8 символов."],
                        "password2": ["Пароли не совпадают."],
                        "code": ["Неверный код подтверждения."],
                        "email": ["Этот email не найден."],
                    },
                ),
                OpenApiExample(
                    "Недействительный код",
                    value={"error": "Недействительный код сброса пароля."},
                ),
            ],
        ),
    },
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


@extend_schema(
    tags=["User"],
    summary="Обновление токена устройства",
    description="Этот эндпоинт позволяет обновить FCM токен устройства пользователя для получения push-уведомлений.",
    parameters=[
        OpenApiParameter(
            name="user_id",
            description="ID пользователя",
            required=True,
            type=str,
            location=OpenApiParameter.QUERY,
        ),
    ],
    request={
        "application/json": {
            "type": "object",
            "properties": {
                "device_token": {
                    "type": "string",
                    "description": "FCM токен устройства",
                }
            },
            "required": ["device_token"],
        }
    },
    responses={
        200: {"description": "Токен устройства успешно обновлен"},
        400: {"description": "Неверные данные запроса"},
        404: {"description": "Пользователь не найден"},
    },
)
class UpdateDeviceTokenView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            user_id = request.query_params.get("user_id")
            device_token = request.data.get("device_token")

            if not user_id:
                return Response(
                    {"error": "Необходимо указать user_id"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            if not device_token:
                return Response(
                    {"error": "Необходимо указать device_token"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            try:
                user = User.objects.get(id=user_id, is_active=True)
            except User.DoesNotExist:
                return Response(
                    {"error": "Пользователь не найден"},
                    status=status.HTTP_404_NOT_FOUND,
                )

            user.device_token = device_token
            user.save(update_fields=["device_token"])

            return Response(
                {"success": "Токен устройства успешно обновлен"},
                status=status.HTTP_200_OK,
            )
        except Exception as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
