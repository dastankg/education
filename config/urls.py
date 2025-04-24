from django.contrib import admin
from django.urls import path, include, re_path
from users.views import PasswordResetConfirmView, PasswordResetRequestView, UpdateDeviceTokenView
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularRedocView,
    SpectacularSwaggerView,
)

from users.views import VerificationSuccessView, CustomConfirmEmailView

urlpatterns = [

    path("schema/", SpectacularAPIView.as_view(), name="schema"),
    path("docs/", SpectacularSwaggerView.as_view(url_name="schema"), name="swagger-ui"),
    path("redoc/", SpectacularRedocView.as_view(url_name="schema"), name="redoc"),

    path(
        "api/v1/auth/password/reset/",
        PasswordResetRequestView.as_view(),
        name="rest_password_reset",
    ),
    path(
        "api/v1/auth/password/reset/confirm/",
        PasswordResetConfirmView.as_view(),
        name="rest_password_reset_confirm",
    ),

    path('admin/', admin.site.urls),
    path("api/v1/auth/", include("dj_rest_auth.urls")),
    path('api/v1/auth/registration/', include('dj_rest_auth.registration.urls')),



    re_path(
        r"auth/registration/account-confirm-email/(?P<key>[-:\w]+)/$",
        CustomConfirmEmailView.as_view(),
        name="account_confirm_email",
    ),

    path(
        "auth/verification-success/",
        VerificationSuccessView.as_view(),
        name="verification_success",
    ),

    path(
        "update-device-token/",
        UpdateDeviceTokenView.as_view(),
        name="update-device-token",
    ),

]
