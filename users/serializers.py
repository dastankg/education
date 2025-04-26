from dj_rest_auth.registration.serializers import RegisterSerializer
from dj_rest_auth.serializers import LoginSerializer, UserDetailsSerializer
from django.contrib.auth.hashers import make_password
from django.contrib.auth.password_validation import validate_password
from django.core.mail import send_mail

from rest_framework import serializers

from django.contrib.auth import get_user_model

from django.conf import settings

User = get_user_model()


class CustomRegisterSerializer(RegisterSerializer):
    username = None

    full_name = serializers.CharField(required=False)
    age = serializers.IntegerField(required=False)
    type = serializers.CharField(required=False, max_length=50)
    def validate_email(self, email):
        email = super().validate_email(email)
        if User.objects.filter(email=email).exists():
            raise serializers.ValidationError(
                "Пользователь с таким email уже существует."
            )
        return email

    def get_cleaned_data(self):
        return {
            "email": self.validated_data.get("email", ""),
            "password1": self.validated_data.get("password1", ""),
            "password2": self.validated_data.get("password2", ""),
            "full_name": self.validated_data.get("full_name", ""),
            "age": self.validated_data.get("age", None),
            "type": self.validated_data.get("type", ""),
        }

    def save(self, request):
        user = super().save(request)
        user.full_name = self.cleaned_data.get('full_name', '')
        user.age = self.cleaned_data.get('age')
        user.type = self.cleaned_data.get('type', '')
        user.save()
        return user

class CustomLoginSerializer(LoginSerializer):
    username = None
    email = serializers.EmailField(required=True)
    password = serializers.CharField(required=True, style={"input_type": "password"})


class PasswordResetRequestSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)

    def send_reset_email(self, user, password_reset):
        subject = "Сброс пароля"
        reset_code = password_reset.reset_token
        message = f"""
        Здравствуйте, {user.full_name or "пользователь"}!

        Вы запросили сброс пароля. Используйте следующий код для установки нового пароля:

        {reset_code}

        Код действителен в течение 24 часов.

        Если вы не запрашивали сброс пароля, просто проигнорируйте это сообщение.

        С уважением,
        Команда поддержки
        """
        email_from = settings.EMAIL_HOST_USER
        recipient_list = [user.email]

        try:
            send_mail(subject, message, email_from, recipient_list, fail_silently=False)
        except Exception as e:
            print(f"Ошибка отправки email: {str(e)}")


class PasswordResetConfirmSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)
    code = serializers.CharField(required=True, min_length=6, max_length=6)
    password = serializers.CharField(
        write_only=True, required=True, validators=[validate_password]
    )
    password2 = serializers.CharField(write_only=True, required=True)

    def validate(self, attrs):
        if attrs["password"] != attrs["password2"]:
            raise serializers.ValidationError({"password2": "Пароли не совпадают."})
        return attrs

    def save(self, **kwargs):
        user = kwargs.get("user")
        user.password = make_password(self.validated_data["password"])
        user.save()
        return user


class CustomUserDetailsSerializer(UserDetailsSerializer):
    age = serializers.IntegerField(required=False)
    user_type = serializers.CharField(required=False)
    device_token = serializers.CharField(required=False)

    class Meta(UserDetailsSerializer.Meta):
        model = User
        fields = (
            "pk",
            "email",
            "full_name",
            "age",
            "type",
            "user_type",
        )
