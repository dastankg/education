from pathlib import Path
import os

from dotenv import load_dotenv

load_dotenv()
BASE_DIR = Path(__file__).resolve().parent.parent


SECRET_KEY = os.getenv("SECRET_KEY")

DEBUG = True

ALLOWED_HOSTS = ["109.73.194.192", "127.0.0.1", "localhost", "google.com"]



INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django.contrib.sites",
    "events.apps.EventsConfig",
    "users.apps.UsersConfig",
    "drf_spectacular",
    "drf_spectacular_sidecar",
    "rest_framework",
    "rest_framework.authtoken",
    "allauth",
    "allauth.account",
    "allauth.socialaccount",
    "dj_rest_auth.registration",
]
SITE_ID = 1

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "allauth.account.middleware.AccountMiddleware",
]

ROOT_URLCONF = "config.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "config.wsgi.application"


DATABASES = {
    "default": {
        "ENGINE": os.getenv("DB_ENGINE"),
        "NAME": os.getenv("DB_NAME"),
        "USER": os.getenv("DB_USER"),
        "PASSWORD": os.getenv("DB_PASSWORD"),
        "HOST": os.getenv("DB_HOST"),
        "PORT": os.getenv("DB_PORT"),
    }
}
CACHES = {
    "default": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": os.environ.get("REDIS_URL", "redis://localhost:6379/0"),
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
        },
    }
}
AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]

LANGUAGE_CODE = "en-us"

TIME_ZONE = "UTC"

USE_I18N = True

USE_TZ = True

STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"
STATIC_URL = "/static/"
STATIC_ROOT = os.path.join(BASE_DIR, "staticfiles")
STATICFILES_DIRS = [
    os.path.join(BASE_DIR, "static"),
]

AWS_S3_ENDPOINT_URL = os.getenv("S3_ENDPOINT_URL")
AWS_STORAGE_BUCKET_NAME = os.getenv("S3_BUCKET_NAME")
AWS_ACCESS_KEY_ID = os.getenv("S3_ACCESS_KEY_ID")
AWS_SECRET_ACCESS_KEY = os.getenv("S3_SECRET_ACCESS_KEY")
AWS_S3_REGION_NAME = "ru-1"
AWS_S3_CUSTOM_DOMAIN = f"{AWS_STORAGE_BUCKET_NAME}.s3.timeweb.cloud"

AWS_S3_OBJECT_PARAMETERS = {
    "CacheControl": "max-age=86400",
}

AWS_DEFAULT_ACL = "public-read"
AWS_QUERYSTRING_AUTH = False
AWS_S3_FILE_OVERWRITE = False

STORAGES = {
    "default": {
        "BACKEND": "storages.backends.s3boto3.S3Boto3Storage",
    },
    "staticfiles": {
        "BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage",
    },
}

AWS_S3_SIGNATURE_VERSION = "s3"
AWS_S3_ADDRESSING_STYLE = "virtual"
MEDIA_URL = f"https://{AWS_S3_CUSTOM_DOMAIN}/media/"
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"



AUTH_USER_MODEL = "users.User"

REST_FRAMEWORK = {
    "DEFAULT_PAGINATION_CLASS": "rest_framework.pagination.LimitOffsetPagination",
    "PAGE_SIZE": 8,
    "DEFAULT_SCHEMA_CLASS": "drf_spectacular.openapi.AutoSchema",
    "DEFAULT_AUTHENTICATION_CLASSES": (
        "dj_rest_auth.jwt_auth.JWTCookieAuthentication",
    ),
}

SPECTACULAR_SETTINGS = {
    "TITLE": "API",
    "DESCRIPTION": "RetMind Test assignment",
    "VERSION": "1.0.0",
    "SERVE_INCLUDE_SCHEMA": False,
    "SERVE_AUTHENTICATION": None,
    "SWAGGER_UI_DIST": "SIDECAR",
    "SWAGGER_UI_FAVICON_HREF": "SIDECAR",
    "REDOC_DIST": "SIDECAR",
}

EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
EMAIL_HOST = os.getenv("SMTP_HOST")
EMAIL_PORT = os.getenv("SMTP_PORT")
EMAIL_USE_TLS = True
EMAIL_HOST_USER = os.getenv("SMTP_EMAIL")
EMAIL_HOST_PASSWORD = os.getenv("SMTP_PASSWORD")

from datetime import timedelta

SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(hours=1),
    "REFRESH_TOKEN_LIFETIME": timedelta(days=1),
}

REST_AUTH = {
    "USE_JWT": True,
    "JWT_AUTH_COOKIE": "_auth",
    "JWT_AUTH_REFRESH_COOKIE": "_refresh",
    "JWT_AUTH_HTTPONLY": False,
    "REGISTER_SERIALIZER": "users.serializers.CustomRegisterSerializer",
    "LOGIN_SERIALIZER": "users.serializers.CustomLoginSerializer",
    "USER_DETAILS_SERIALIZER": "users.serializers.CustomUserDetailsSerializer",
}
ACCOUNT_USER_MODEL_USERNAME_FIELD = None
ACCOUNT_EMAIL_CONFIRMATION_EXPIRE_DAYS = 1
ACCOUNT_AUTHENTICATION_METHOD = "email"
ACCOUNT_USERNAME_REQUIRED = False
ACCOUNT_EMAIL_REQUIRED = True
ACCOUNT_EMAIL_VERIFICATION = "mandatory"
ACCOUNT_CONFIRM_EMAIL_ON_GET = True
ACCOUNT_EMAIL_CONFIRMATION_ANONYMOUS_REDIRECT_URL = "/auth/verification-success/"
ACCOUNT_EMAIL_CONFIRMATION_AUTHENTICATED_REDIRECT_URL = "/auth/verification-success/"


FIREBASE_CREDENTIALS_PATH = os.path.join(BASE_DIR, "firebase-credentials.json")