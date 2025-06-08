from django.utils import timezone

from django.contrib.auth import get_user_model
from rest_framework.pagination import LimitOffsetPagination

from events.models import Event, EventView
from rest_framework.response import Response
from events.serializers import (
    EventSerializer,
)
from rest_framework import generics, status
from rest_framework.views import APIView
from users.permissions import IsAuthenticated

User = get_user_model()


class ListFavoriteEventsAPIView(generics.ListAPIView):
    serializer_class = EventSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user

        return Event.objects.filter(views__user=user, views__is_liked=True).order_by(
            "-views__liked_at"
        )

    # def list(self, request, *args, **kwargs):
    #     try:
    #         return super().list(request, *args, **kwargs)
    #     except Exception as e:
    #         return Response(
    #             {"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
    #         )


class AddFavoriteEventAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        user = request.user
        event_id = request.query_params.get("event_id")

        if not event_id:
            return Response(
                {"error": "Необходимо указать user_id и event_id"},
                status=status.HTTP_400_BAD_REQUEST,
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
            user=user, event=event, defaults={"is_liked": True, "liked_at": timezone.now()}
        )

        return Response(
            {"success": "Event успешно добавлен в избранное"},
            status=status.HTTP_200_OK,
        )

class RemoveFavoriteEventAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def delete(self, request):
        user = request.user
        event_id = request.query_params.get("event_id")

        if not event_id:
            return Response(
                {"error": "Необходимо указать event_id"},
                status=status.HTTP_400_BAD_REQUEST,
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
        
class UnviewedEventsAPIView(generics.ListAPIView):
    serializer_class = EventSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user

        viewed_events = EventView.objects.filter(user=user, is_viewed=True).values_list(
            "event__event_id", flat=True
        )
        return Event.objects.exclude(event_id__in=viewed_events)

    # def list(self, request, *args, **kwargs):
    #     try:
    #         return super().list(request, *args, **kwargs)
    #     except Exception as e:
    #         return Response(
    #             {"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
    #         )

class EventLinkTrackView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, event_id):
        user = request.user

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

class EventDetailAPIView(generics.RetrieveAPIView):
    permission_classes = [IsAuthenticated]
    queryset = Event.objects.all()
    serializer_class = EventSerializer
    lookup_field = "event_id"

    def get(self, request, *args, **kwargs):
        user = request.user
        event = self.get_object()
        event.click += 1
        event.save()

        try:
            event_view = EventView.objects.get(user=user, event=event)
            event_view.is_viewed = True
            event_view.save()
        except EventView.DoesNotExist:
            EventView.objects.create(user=user, event=event, is_viewed=True)


        serializer = self.get_serializer(
            event, context={"request": request, "user_id": user.id}
        )
        return Response(serializer.data)

class EventListView(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    queryset = Event.objects.all()
    serializer_class = EventSerializer

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
    
    def get_serializer_context(self):
        context = super().get_serializer_context()
        context["request"] = self.request
        return context


class UserActionsAPIView(APIView):
    permission_classes = [IsAuthenticated]
    pagination_class = LimitOffsetPagination

    def get(self, request):
        user = request.user
        event_type = request.query_params.get("event_type")

        user_actions_query = EventView.objects.filter(user=user)

        if event_type:
            user_actions_query = user_actions_query.filter(
                event__types_event=event_type
            )

        user_actions_query = user_actions_query.order_by("-created_at")

        events_query = Event.objects.all()
        if event_type:
            events_query = events_query.filter(types_event=event_type)

        viewed_events_ids = EventView.objects.filter(user=user, is_viewed=True)
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
