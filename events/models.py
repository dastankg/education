import os
import uuid

from django.contrib.auth import get_user_model
from django.contrib.postgres.indexes import HashIndex
from django.db import models
from django_ckeditor_5.fields import CKEditor5Field

User = get_user_model()


def get_image_path(instance, filename):
    ext = filename.split(".")[-1]
    filename = f"{uuid.uuid4()}.{ext}"
    return os.path.join("media/images", filename)


class Event(models.Model):
    TYPE_CHOICES = [
        ("grant", "Grant"),
        ("internship", "Internship"),
        ("event", "Event"),
        ("olympiad", "Olympiad"),
        ("course", "Course"),
    ]

    event_id = models.UUIDField(
        primary_key=True, default=uuid.uuid4, editable=False, db_index=True
    )
    title = models.CharField(max_length=200)
    description = CKEditor5Field(config_name='extends')
    image = models.ImageField(upload_to=get_image_path)
    deadline = models.DateField()
    types_event = models.CharField(max_length=100, choices=TYPE_CHOICES)
    type_url = models.URLField()
    company = models.CharField(max_length=100, blank=True, null=True)
    click = models.IntegerField(blank=True, null=True, default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = "Event"
        verbose_name_plural = "Events"
        indexes = (HashIndex(fields=("event_id",), name="uuid_hash_index"),)


class EventView(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="event_views")
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name="views")
    is_viewed = models.BooleanField(default=False)
    is_liked = models.BooleanField(default=False)
    is_linked = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    liked_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        unique_together = ("user", "event")