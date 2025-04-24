from django.contrib.auth.base_user import BaseUserManager, AbstractBaseUser
from django.contrib.auth.models import PermissionsMixin
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models
from django.utils import timezone
from django.conf import settings
from datetime import timedelta


class UserManager(BaseUserManager):

    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('User must have an email address')

        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)

        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        return self.create_user(email, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
    TYPE_CHOICES = [
        ("школьник(ца)", "Школьник(ца)"),
        ("студент(ка)", "Студент(ка)"),
        ("другое", "Другое"),
    ]
    age = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(120)])
    type = models.CharField(max_length=20, choices=TYPE_CHOICES, blank=True, null=True)
    email = models.EmailField('email address', unique=True)
    full_name = models.CharField('full name', max_length=255)
    device_token = models.CharField(max_length=255, blank=True, null=True)
    is_verified = models.BooleanField('verified', default=False)
    is_active = models.BooleanField('active', default=True)
    is_staff = models.BooleanField('staff status', default=False)
    created_at = models.DateTimeField('created at', auto_now_add=True)

    objects = UserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    class Meta:
        verbose_name = 'user'
        verbose_name_plural = 'users'

    def __str__(self):
        return self.email


class PasswordReset(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    reset_token = models.CharField(max_length=6)
    created_at = models.DateTimeField(auto_now_add=True)
    used = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.user.email} - {self.reset_token}"

    @property
    def is_expired(self):
        # Срок действия токена - 24 часа
        return self.created_at < timezone.now() - timedelta(hours=24)
