from django.db.models.signals import post_save
from django.dispatch import receiver
import logging

from .models import Event
from events.utils import FirebaseNotificationService

logger = logging.getLogger(__name__)


@receiver(post_save, sender=Event)
def send_event_notification(sender, instance, created, **kwargs):
    if created:
        try:
            logger.info(
                f"New event created: {instance.title} (ID: {instance.event_id}), sending notification"
            )
            notification_service = FirebaseNotificationService()
            result = notification_service.send_event_notification(instance)
            logger.info(f"Notification sending result: {result}")
        except Exception as e:
            logger.error(
                f"Failed to send notification for event {instance.event_id}: {str(e)}"
            )
