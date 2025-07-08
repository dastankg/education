import firebase_admin
from django.contrib.auth import get_user_model
from firebase_admin import credentials, messaging
from django.conf import settings
import logging

logger = logging.getLogger(__name__)

User = get_user_model()


class FirebaseNotificationService:
    _instance = None
    _initialized = False

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(FirebaseNotificationService, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        if not self._initialized:
            try:
                cred_path = getattr(settings, "FIREBASE_CREDENTIALS_PATH", None)
                if not cred_path:
                    logger.error("FIREBASE_CREDENTIALS_PATH not set in settings")
                    return

                cred = credentials.Certificate(cred_path)
                firebase_admin.initialize_app(cred)
                self._initialized = True
                logger.info("Firebase notification service initialized")
            except Exception as e:
                logger.error(f"Failed to initialize Firebase: {str(e)}")

    def send_notification(self, title, body, tokens, data=None):
        if not self._initialized:
            logger.error("Firebase not initialized, cannot send notification")
            return {"success": 0, "failure": len(tokens)}

        if not tokens:
            logger.warning("No tokens provided for notification")
            return {"success": 0, "failure": 0}

        notification = messaging.Notification(title=title, body=body)

        results = {"success": 0, "failure": 0, "responses": []}

        for token in tokens:
            message = messaging.Message(
                notification=notification, token=token, data=data
            )

            try:
                response = messaging.send(message)
                results["success"] += 1
                results["responses"].append({"success": True, "message_id": response})
                logger.info(f"Notification sent to token {token[:10]}...")
            except Exception as e:
                results["failure"] += 1
                results["responses"].append({"success": False, "error": str(e)})
                logger.error(
                    f"Failed to send notification to token {token[:10]}...: {str(e)}"
                )

        logger.info(
            f"Total notifications: {results['success']} successful, {results['failure']} failed"
        )
        return results

    def send_event_notification(self, event, tokens=None):
        title = "Новое событие"
        body = event.title

        data = {
            "event_id": str(event.event_id),
            "type": event.types_event,
            "title": event.title,
            "click_action": "OPEN_EVENT_DETAILS",
        }

        if tokens is None:
            tokens = list(
                User.objects.filter(is_active=True, device_token__isnull=False)
                .exclude(device_token="")
                .values_list("device_token", flat=True)
            )

        return self.send_notification(title, body, tokens, data)
