from drf_spectacular.utils import extend_schema_field
from rest_framework import serializers

from events.models import Event, EventView


class EventsLikesSerializer(serializers.ModelSerializer):
    is_like = serializers.SerializerMethodField()

    class Meta:
        model = Event
        fields = [
            "event_id",
            "title",
            "image",
            "deadline",
            "types_event",
            "company",
            "is_like",
        ]

    @extend_schema_field(serializers.BooleanField())
    def get_is_like(self, obj):
        request = self.context.get("request")
        user_id = request.query_params.get("user_id") if request else None

        if not user_id:
            return False

        return EventView.objects.filter(
            user__id=user_id, event=obj, is_liked=True
        ).exists()