from django.contrib import admin
from django.db.models import Count, Q
from .models import Event, EventView


class EventViewInline(admin.TabularInline):
    model = EventView
    extra = 0
    readonly_fields = ("user", "is_viewed", "is_liked", "is_linked")
    can_delete = False


@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    readonly_fields = (
        "views_total_display",
        "views_school_display",
        "views_student_display",
        "views_other_display",
        "total_likes_display",
        "likes_school_display",
        "likes_student_display",
        "likes_other_display",
        "links_total_display",
        "links_school_display",
        "links_student_display",
        "links_other_display",
    )

    fieldsets = (
        (
            None,
            {
                "fields": (
                    "title",
                    "description",
                    "image",
                    "deadline",
                    "types_event",
                    "type_url",
                    "company",
                    "click",
                    "views_total_display",
                    "views_school_display",
                    "views_student_display",
                    "views_other_display",
                    "total_likes_display",
                    "likes_school_display",
                    "likes_student_display",
                    "likes_other_display",
                    "links_total_display",
                    "links_school_display",
                    "links_student_display",
                    "links_other_display",
                )
            },
        ),
    )

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.annotate(
            views_total=Count("views", filter=Q(views__is_viewed=True)),
            views_school=Count(
                "views",
                filter=Q(views__is_viewed=True, views__user__type="школьник(ца)"),
            ),
            views_student=Count(
                "views",
                filter=Q(views__is_viewed=True, views__user__type="студент(ка)"),
            ),
            views_other=Count(
                "views", filter=Q(views__is_viewed=True, views__user__type="другое")
            ),
            total_likes=Count("views", filter=Q(views__is_liked=True)),
            likes_school=Count(
                "views",
                filter=Q(views__is_liked=True, views__user__type="школьник(ца)"),
            ),
            likes_student=Count(
                "views", filter=Q(views__is_liked=True, views__user__type="студент(ка)")
            ),
            likes_other=Count(
                "views", filter=Q(views__is_liked=True, views__user__type="другое")
            ),
            links_total=Count("views", filter=Q(views__is_linked=True)),
            links_school=Count(
                "views",
                filter=Q(views__is_linked=True, views__user__type="школьник(ца)"),
            ),
            links_student=Count(
                "views",
                filter=Q(views__is_linked=True, views__user__type="студент(ка)"),
            ),
            links_other=Count(
                "views", filter=Q(views__is_linked=True, views__user__type="другое")
            ),
        )

    def views_total_display(self, obj):
        return getattr(obj, "views_total", 0)

    views_total_display.short_description = "Просмотров всего"

    def views_school_display(self, obj):
        return getattr(obj, "views_school", 0)

    views_school_display.short_description = "Просмотров от школьников"

    def views_student_display(self, obj):
        return getattr(obj, "views_student", 0)

    views_student_display.short_description = "Просмотров от студентов"

    def views_other_display(self, obj):
        return getattr(obj, "views_other", 0)

    views_other_display.short_description = "Просмотров от других пользователей"

    def total_likes_display(self, obj):
        return getattr(obj, "total_likes", 0)

    total_likes_display.short_description = "Всего лайков"

    def likes_school_display(self, obj):
        return getattr(obj, "likes_school", 0)

    likes_school_display.short_description = "Лайков от школьников"

    def likes_student_display(self, obj):
        return getattr(obj, "likes_student", 0)

    likes_student_display.short_description = "Лайков от студентов"

    def likes_other_display(self, obj):
        return getattr(obj, "likes_other", 0)

    likes_other_display.short_description = "Лайков от других пользователей"

    def links_total_display(self, obj):
        return getattr(obj, "links_total", 0)

    links_total_display.short_description = "Переходов всего"

    def links_school_display(self, obj):
        return getattr(obj, "links_school", 0)

    links_school_display.short_description = "Переходов от школьников"

    def links_student_display(self, obj):
        return getattr(obj, "links_student", 0)

    links_student_display.short_description = "Переходов от студентов"

    def links_other_display(self, obj):
        return getattr(obj, "links_other", 0)

    links_other_display.short_description = "Переходов от других пользователей"
