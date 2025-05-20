from django.views.decorators.cache import cache_page
from django.utils.decorators import method_decorator

from django.contrib.auth import get_user_model
from drf_spectacular.utils import (
    OpenApiExample,
    OpenApiParameter,
    extend_schema,
    OpenApiResponse,
)
from rest_framework.pagination import LimitOffsetPagination

from events.models import Event, EventView
from rest_framework.response import Response
from events.serializers import (
    EventsLikesSerializer,
    EventsUnviewedSerializer,
    EventSerializer,
)
from rest_framework.permissions import IsAuthenticated
from rest_framework import generics, status
from rest_framework.views import APIView

User = get_user_model()


@extend_schema(
    tags=["User"],
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
            "-views__created_at"
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
    tags=["User"],
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
    tags=["User"],
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


@extend_schema(
    auth=None,
    tags=["User"],
    summary="Список непросмотренных событий",
    description="Возвращает события, которые пользователь ещё не просмотрел.",
    parameters=[
        OpenApiParameter(
            name="user_id",
            description="ID пользователя",
            required=True,
            type=int,
            location=OpenApiParameter.QUERY,
        ),
    ],
    responses={
        200: OpenApiResponse(
            description="Список непросмотренных событий",
            response=EventsUnviewedSerializer(many=True),
        ),
        400: OpenApiResponse(
            description="Ошибка запроса",
            examples=[
                OpenApiExample("Ошибка", value={"error": "Необходимо указать user_id"})
            ],
        ),
        404: OpenApiResponse(
            description="Пользователь не найден",
            examples=[
                OpenApiExample("Ошибка", value={"error": "Пользователь не найден"})
            ],
        ),
    },
)
class UnviewedEventsAPIView(generics.ListAPIView):
    serializer_class = EventsUnviewedSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user_id = self.request.query_params.get("user_id")

        if not user_id:
            return Event.objects.none()

        try:
            user = User.objects.get(id=user_id, is_active=True)
        except (User.DoesNotExist, ValueError):
            return Event.objects.none()

        viewed_events = EventView.objects.filter(user=user, is_viewed=True).values_list(
            "event__event_id", flat=True
        )
        return Event.objects.exclude(event_id__in=viewed_events)

    def list(self, request, *args, **kwargs):
        try:
            user_id = request.query_params.get("user_id")

            if not user_id:
                return Response(
                    {"error": "Необходимо указать user_id"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            try:
                User.objects.get(id=int(user_id), is_active=True)
            except (User.DoesNotExist, ValueError):
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
    tags=["Events"],
    summary="Фиксация перехода по ссылке события",
    description="Этот эндпоинт устанавливает флаг `is_linked=True` для связки пользователь-событие, "
    "что означает, что пользователь действительно перешёл по ссылке (`type_url`).",
    parameters=[
        OpenApiParameter(
            name="event_id",
            description="UUID события",
            required=True,
            type={"type": "string", "format": "uuid"},
            location=OpenApiParameter.PATH,
        ),
        OpenApiParameter(
            name="user_id",
            description="ID пользователя",
            required=True,
            type=str,
            location=OpenApiParameter.QUERY,
        ),
    ],
    responses={
        200: OpenApiResponse(
            description="Переход успешно зафиксирован",
            examples=[
                OpenApiExample(
                    "Успешный переход",
                    value={"message": "Переход по ссылке зафиксирован."},
                )
            ],
        ),
        404: OpenApiResponse(
            description="Событие не найдено",
            examples=[
                OpenApiExample(
                    "Событие не существует",
                    value={"error": "Событие не найдено."},
                )
            ],
        ),
    },
)
class EventLinkTrackView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, event_id):
        try:
            user_id = request.query_params.get("user_id")

            if not user_id:
                return Response(
                    {"error": "Необходимо указать user_id"},
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
                    {"error": "Событие не найдено."},
                    status=status.HTTP_404_NOT_FOUND,
                )

            event_view, _ = EventView.objects.get_or_create(user=user, event=event)
            if not event_view.is_linked:
                event_view.is_linked = True
                event_view.save(update_fields=["is_linked"])

            return Response(
                {"message": "Переход по ссылке зафиксирован."},
                status=status.HTTP_200_OK,
            )
        except Exception as e:
            return Response(
                {"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


@extend_schema(
    tags=["Events"],
    summary="Получение детальной информации о Event",
    description="Этот эндпоинт возвращает подробную информацию о конкретном Event по его ID. Передайте `user_id` как query параметр, чтобы зафиксировать просмотр.",
    parameters=[
        OpenApiParameter(
            name="user_id",
            description="UUID пользователя для фиксации просмотра и определения is_like/is_viewed",
            required=False,
            type=int,
            location=OpenApiParameter.QUERY,
        ),
    ],
    responses={200: EventSerializer, 404: {"description": "Event не найден"}},
    examples=[
        OpenApiExample(
            "Детальная информация о Event",
            value={
                "event_id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
                "title": "Summer Internship Program",
                "description": "3-month internship opportunity for students",
                "image": "/media/images/3fa85f64-5717-4562-b3fc-2c963f66afa6.jpg",
                "deadline": "2025-06-30",
                "types_event": "internship",
                "type_url": "https://example.com/internships",
                "company": "apple",
                "created_at": "2025-03-15T10:30:00Z",
                "updated_at": "2025-03-15T10:30:00Z",
            },
        )
    ],
)
class EventDetailAPIView(generics.RetrieveAPIView):
    permission_classes = [IsAuthenticated]
    queryset = Event.objects.all()
    serializer_class = EventSerializer
    lookup_field = "event_id"

    def get(self, request, *args, **kwargs):
        try:
            user_id = request.query_params.get("user_id")
            event = self.get_object()
            event.click += 1
            event.save()
            if user_id:
                try:
                    user = User.objects.get(id=user_id)

                    try:
                        event_view = EventView.objects.get(user=user, event=event)
                        event_view.is_viewed = True
                        event_view.save()
                    except EventView.DoesNotExist:
                        EventView.objects.create(user=user, event=event, is_viewed=True)

                except User.DoesNotExist:
                    pass

            serializer = self.get_serializer(
                event, context={"request": request, "user_id": user_id}
            )
            return Response(serializer.data)
        except Exception as e:
            return Response(
                {"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


@extend_schema(
    auth=None,
    tags=["Events"],
    summary="Список событий с фильтрацией",
    description="Возвращает список событий с возможностью поиска по названию и фильтрации по типу события.",
    parameters=[
        OpenApiParameter(
            name="query",
            description="Поиск по названию события",
            required=False,
            type=str,
            location=OpenApiParameter.QUERY,
        ),
        OpenApiParameter(
            name="types_event",
            description="Тип события для фильтрации (опционально): grant, internship, event, olympiad, course.",
            required=False,
            type=str,
            enum=["grant", "internship", "event", "olympiad", "course"],
            location=OpenApiParameter.QUERY,
        ),
        OpenApiParameter(
            name="ordering",
            description="Сортировка результатов (по умолчанию -created_at)",
            required=False,
            type=str,
            location=OpenApiParameter.QUERY,
        ),
    ],
    responses={
        200: OpenApiResponse(
            description="Список событий", response=EventSerializer(many=True)
        ),
    },
)
class EventListView(generics.ListAPIView):
    queryset = Event.objects.all()
    serializer_class = EventSerializer

    @method_decorator(cache_page(180))
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)

    def get_queryset(self):
        queryset = Event.objects.all()

        query = self.request.query_params.get("query", None)
        if query:
            queryset = queryset.filter(title__icontains=query)

        types_event = self.request.query_params.get("types_event", None)
        if types_event:
            queryset = queryset.filter(types_event=types_event)

        ordering = self.request.query_params.get("ordering", "-created_at")
        return queryset.order_by(ordering)


@extend_schema(
    tags=["User"],
    summary="Список активности пользователя",
    parameters=[
        OpenApiParameter(
            name="user_id",
            description="UUID пользователя, для которого запрашиваются действия.",
            required=True,
            type=str,
            location=OpenApiParameter.QUERY,
        ),
        OpenApiParameter(
            name="event_type",
            description="Тип события для фильтрации (опционально): grant, internship, event, olympiad, course.",
            required=False,
            type=str,
            enum=["grant", "internship", "event", "olympiad", "course"],
            location=OpenApiParameter.QUERY,
        ),
        OpenApiParameter(
            name="limit",
            description="Количество элементов на странице (по умолчанию 8).",
            required=False,
            type=int,
            location=OpenApiParameter.QUERY,
        ),
        OpenApiParameter(
            name="offset",
            description="Смещение от начала списка результатов.",
            required=False,
            type=int,
            location=OpenApiParameter.QUERY,
        ),
    ],
    responses={
        200: {
            "type": "object",
            "properties": {
                "count": {"type": "integer", "description": "Общее количество записей"},
                "next": {
                    "type": ["string", "null"],
                    "description": "URL следующей страницы",
                },
                "previous": {
                    "type": ["string", "null"],
                    "description": "URL предыдущей страницы",
                },
                "results": {
                    "type": "object",
                    "properties": {
                        "liked_events": {
                            "type": "array",
                            "items": {"type": "string", "format": "uuid"},
                            "description": "Список UUID событий, которые пользователь лайкнул.",
                        },
                        "viewed_events": {
                            "type": "array",
                            "items": {"type": "string", "format": "uuid"},
                            "description": "Список UUID событий, которые пользователь просмотрел.",
                        },
                        "unviewed_count": {
                            "type": "integer",
                            "description": "Количество непросмотренных событий.",
                        },
                    },
                },
            },
        },
        400: {"description": "Bad Request (Parameter user_id is required)"},
    },
)
class UserActionsAPIView(APIView):
    permission_classes = [IsAuthenticated]
    pagination_class = LimitOffsetPagination

    def get(self, request):
        user_id = request.query_params.get("user_id")
        event_type = request.query_params.get("event_type")

        if not user_id:
            return Response(
                {"detail": "Параметр user_id обязателен"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        user_actions_query = EventView.objects.filter(user_id=user_id)

        if event_type:
            user_actions_query = user_actions_query.filter(
                event__types_event=event_type
            )

        user_actions_query = user_actions_query.order_by("-created_at")

        events_query = Event.objects.all()
        if event_type:
            events_query = events_query.filter(types_event=event_type)

        viewed_events_ids = EventView.objects.filter(user_id=user_id, is_viewed=True)
        if event_type:
            viewed_events_ids = viewed_events_ids.filter(event__types_event=event_type)
        viewed_events_ids = viewed_events_ids.values_list("event_id", flat=True)

        unviewed_events = events_query.exclude(event_id__in=viewed_events_ids)
        unviewed_count = unviewed_events.count()

        paginator = self.pagination_class()
        paginated_actions = paginator.paginate_queryset(user_actions_query, request)

        liked_events = []
        viewed_events = []

        for action in paginated_actions:
            event_uuid = str(action.event.event_id)
            if action.is_liked:
                liked_events.append(event_uuid)
            if action.is_viewed:
                viewed_events.append(event_uuid)

        results = {
            "liked_events": liked_events,
            "viewed_events": viewed_events,
            "unviewed_count": unviewed_count,
        }

        return paginator.get_paginated_response(results)
