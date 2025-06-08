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
