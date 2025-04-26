from events.models import Event
from django.utils import timezone

for _ in range(30):
    Event.objects.create(
        title="Грант на обучение в Европе",
        description="Грант покрывает полную стоимость обучения и проживания.",
        image="media/images/84b88a02-ad22-4e53-89c0-c968d3bd5af6.png",  # Можно поставить любой файл, если тестово
        deadline=timezone.now().date(),
        types_event="grant",
        type_url="https://example.com",
        company="European Grants Foundation",
    )
