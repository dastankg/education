from django.contrib import admin
from django.urls import path, include, re_path

from events.views import (
    ListFavoriteEventsAPIView,
    RemoveFavoriteEventAPIView,
    AddFavoriteEventAPIView,
    UnviewedEventsAPIView,
    EventLinkTrackView,
    EventDetailAPIView,
    UserActionsAPIView,
    EventListView,
)
from users.views import (
    PasswordResetConfirmView,
    PasswordResetRequestView,
    UpdateDeviceTokenView,
)
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularRedocView,
    SpectacularSwaggerView,
)

from users.views import VerificationSuccessView, CustomConfirmEmailView

urlpatterns = [
    # API Documentation
    path("schema/", SpectacularAPIView.as_view(), name="api-schema"),
    path(
        "docs/",
        SpectacularSwaggerView.as_view(url_name="api-schema"),
        name="swagger-ui",
    ),
    path("redoc/", SpectacularRedocView.as_view(url_name="api-schema"), name="redoc"),
    # Admin Site
    path("admin/", admin.site.urls),
    # Authentication URLs
    path("api/v1/auth/", include("dj_rest_auth.urls")),
    path("api/v1/auth/registration/", include("dj_rest_auth.registration.urls")),

    path(
        "api/v1/auth/reset-password-request/",
        PasswordResetRequestView.as_view(),
        name="reset_password_request",
    ),
    path(
        "api/v1/auth/reset-password-confirm/",
        PasswordResetConfirmView.as_view(),
        name="reset_password_confirm",
    ),
    re_path(
        r"auth/registration/account-confirm-email/(?P<key>[-:\w]+)/$",
        CustomConfirmEmailView.as_view(),
        name="account_confirm_email",
    ),
    path(
        "auth/verification-success/",
        VerificationSuccessView.as_view(),
        name="auth-verification-success",
    ),
    # Device Management
    path(
        "api/v1/devices/token/",
        UpdateDeviceTokenView.as_view(),
        name="devices-update-token",
    ),
    # Favorites
    path(
        "api/v1/favorites/",
        ListFavoriteEventsAPIView.as_view(),
        name="favorites-list",
    ),
    path(
        "api/v1/favorites/add/", AddFavoriteEventAPIView.as_view(), name="favorites-add"
    ),
    path(
        "api/v1/favorites/remove/",
        RemoveFavoriteEventAPIView.as_view(),
        name="favorites-remove",
    ),
    # Events
    path("api/v1/events/", EventListView.as_view(), name="events-list"),
    path(
        "api/v1/events/<uuid:event_id>/",
        EventDetailAPIView.as_view(),
        name="events-detail",
    ),
    path(
        "api/v1/events/<uuid:event_id>/link/",
        EventLinkTrackView.as_view(),
        name="events-link-track",
    ),
    path(
        "api/v1/events/unviewed/",
        UnviewedEventsAPIView.as_view(),
        name="events-unviewed",
    ),
    # User Actions
    path(
        "api/v1/user-actions/", UserActionsAPIView.as_view(), name="user-actions-list"
    ),
]
