from email import utils

from django.contrib.auth import get_user_model
from drf_spectacular.utils import (
    OpenApiExample,
    OpenApiParameter,
    extend_schema,
    OpenApiResponse,
)
from events.models import Event, EventView
from rest_framework.response import Response
from events.serializers import EventsLikesSerializer
from rest_framework.permissions import IsAuthenticated
from rest_framework import generics, status
from rest_framework.views import APIView

User = get_user_model()

@extend_schema(
    tags=["UserProfile"],
    summary="Получение списка избранных Event",
    description="Этот эндпоинт возвращает список всех избранных Event пользователя.",
    parameters=[
        OpenApiParameter(
            name="user_id",
            description="ID пользователя",
            required=True,
            type=str,
            location=OpenApiParameter.QUERY,
        ),
    ],
    responses={
        200: {"description": "Список избранных Event"},
        404: {"description": "Пользователь не найден"},
    },
)
class ListFavoriteEventsAPIView(generics.ListAPIView):
    serializer_class = EventsLikesSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user_id = self.request.query_params.get("user_id")

        if not user_id:
            return Event.objects.none()

        try:
            user = User.objects.get(id=user_id, is_active=True)
        except User.DoesNotExist:
            return Event.objects.none()

        return Event.objects.filter(views__user=user, views__is_liked=True).order_by(
            "-created_at"
        )

    def list(self, request, *args, **kwargs):
        try:
            user_id = request.query_params.get("user_id")

            if not user_id:
                return Response(
                    {"error": "Необходимо указать user_id"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            try:
                User.objects.get(id=user_id, is_active=True)
            except User.DoesNotExist:
                return Response(
                    {"error": "Пользователь не найден"},
                    status=status.HTTP_404_NOT_FOUND,
                )

            return super().list(request, *args, **kwargs)
        except Exception as e:
            return Response(
                {"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


@extend_schema(
    tags=["UserProfile"],
    summary="Добавление Event в избранное",
    description="Этот эндпоинт позволяет пользователю добавить Event в список избранного.",
    parameters=[
        OpenApiParameter(
            name="user_id",
            description="ID пользователя",
            required=True,
            type=str,
            location=OpenApiParameter.QUERY,
        ),
        OpenApiParameter(
            name="event_id",
            description="ID события, которое нужно добавить в избранное",
            required=True,
            type=str,
            location=OpenApiParameter.QUERY,
        ),
    ],
    responses={
        200: {"description": "Event успешно добавлен в избранное"},
        404: {"description": "Пользователь или Event не найден"},
        400: {"description": "Event уже в избранном"},
    },
)
class AddFavoriteEventAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            user_id = request.query_params.get("user_id")
            event_id = request.query_params.get("event_id")

            if not user_id or not event_id:
                return Response(
                    {"error": "Необходимо указать user_id и event_id"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            try:
                user = User.objects.get(id=user_id, is_active=True)
            except User.DoesNotExist:
                return Response(
                    {"error": "Пользователь не найден"},
                    status=status.HTTP_404_NOT_FOUND,
                )

            try:
                event = Event.objects.get(event_id=event_id)
            except Event.DoesNotExist:
                return Response(
                    {"error": "Event не найден"}, status=status.HTTP_404_NOT_FOUND
                )

            if EventView.objects.filter(user=user, event=event, is_liked=True).exists():
                return Response(
                    {"error": "Event уже в избранном"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            EventView.objects.update_or_create(
                user=user, event=event, defaults={"is_liked": True}
            )

            return Response(
                {"success": "Event успешно добавлен в избранное"},
                status=status.HTTP_200_OK,
            )
        except Exception as e:
            return Response(
                {"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


@extend_schema(
    tags=["UserProfile"],
    summary="Удаление Event из избранного",
    description="Этот эндпоинт позволяет пользователю удалить Event из списка избранного.",
    parameters=[
        OpenApiParameter(
            name="user_id",
            description="ID пользователя",
            required=True,
            type=str,
            location=OpenApiParameter.QUERY,
        ),
        OpenApiParameter(
            name="event_id",
            description="ID события, которое нужно удалить из избранного",
            required=True,
            type=str,
            location=OpenApiParameter.QUERY,
        ),
    ],
    responses={
        200: {"description": "Event успешно удален из избранного"},
        404: {"description": "Пользователь или Event не найден"},
        400: {"description": "Event не был в избранном"},
    },
)
class RemoveFavoriteEventAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def delete(self, request):
        try:
            user_id = request.query_params.get("user_id")
            event_id = request.query_params.get("event_id")

            if not user_id or not event_id:
                return Response(
                    {"error": "Необходимо указать user_id и event_id"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            try:
                user = User.objects.get(id=user_id, is_active=True)
            except User.DoesNotExist:
                return Response(
                    {"error": "Пользователь не найден"},
                    status=status.HTTP_404_NOT_FOUND,
                )

            try:
                event = Event.objects.get(event_id=event_id)
            except Event.DoesNotExist:
                return Response(
                    {"error": "Event не найден"}, status=status.HTTP_404_NOT_FOUND
                )

            try:
                event_view = EventView.objects.get(user=user, event=event)
            except EventView.DoesNotExist:
                return Response(
                    {"error": "Event не был в избранном"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            if not event_view.is_liked:
                return Response(
                    {"error": "Event не был в избранном"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            event_view.is_liked = False
            event_view.save()

            return Response(
                {"success": "Event успешно удален из избранного"},
                status=status.HTTP_200_OK,
            )
        except Exception as e:
            return Response(
                {"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
