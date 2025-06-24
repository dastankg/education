from django.contrib import admin
from django.urls import path, include, re_path

from events.views import (
    ListFavoriteEventsAPIView,
    RemoveFavoriteEventAPIView,
    AddFavoriteEventAPIView,
    UnviewedEventsAPIView,
    EventLinkTrackView,
    EventDetailAPIView,
    UnviewedEventsCountAPIView,
    EventListView,
)
from users.views import (
    PasswordResetConfirmView,
    PasswordResetRequestView,
    UpdateDeviceTokenView,
)

from users.views import VerificationSuccessView, CustomConfirmEmailView

urlpatterns = [
    # Admin Site
    path("admin/", admin.site.urls),
    path('ckeditor5/', include('django_ckeditor_5.urls')),
    # Authentication URLs
    path("api/v1/auth/", include("dj_rest_auth.urls")),
    path("api/v1/auth/registration/", include("dj_rest_auth.registration.urls")),
    path(
        "api/v2/auth/password/reset/",
        PasswordResetRequestView.as_view(),
        name="reset_password_request",
    ),
    path(
        "api/v2/auth/password/reset/confirm/",
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
    path(
        "api/v1/devices/token/",
        UpdateDeviceTokenView.as_view(),
        name="devices-update-token",
    ),
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
        "api/v1/events/unviewed/",
        UnviewedEventsAPIView.as_view(),
        name="events-unviewed",
    ),
    path(
        "api/v1/events/track/<uuid:event_id>/",
        EventLinkTrackView.as_view(),
        name="event-link-track",
    ),
    path("api/v1/events/unviewed_count/", UnviewedEventsCountAPIView.as_view()),
    path(
        "api/v1/events/<uuid:event_id>/",
        EventDetailAPIView.as_view(),
        name="event-detail",
    ),
]
