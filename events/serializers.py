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

    # @extend_schema_field(serializers.BooleanField())
    # def get_is_like(self, obj):
    #     request = self.context.get("request")
    #     user_id = request.query_params.get("user_id") if request else None

    #     if not user_id:
    #         return False

    #     return EventView.objects.filter(
    #         user__id=user_id, event=obj, is_liked=True
    #     ).exists()


class EventsUnviewedSerializer(serializers.ModelSerializer):
    is_viewed = serializers.SerializerMethodField()

    class Meta:
        model = Event
        fields = [
            "event_id",
            "title",
            "image",
            "deadline",
            "types_event",
            "company",
            "is_viewed",
        ]

    # @extend_schema_field(serializers.BooleanField())
    # def get_is_viewed(self, obj):
    #     request = self.context.get("request")
    #     user_id = request.query_params.get("user_id") if request else None

    #     if not user_id:
    #         return False

    #     return EventView.objects.filter(
    #         user__id=user_id, event=obj, is_viewed=True
    #     ).exists()


class EventSerializer(serializers.ModelSerializer):
    class Meta:
        model = Event
        fields = [
            "event_id",
            "title",
            "description",
            "image",
            "deadline",
            "types_event",
            "type_url",
            "company",
            "created_at",
            "updated_at",
        ]
