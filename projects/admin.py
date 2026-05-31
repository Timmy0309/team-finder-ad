from django.contrib import admin

from .models import Project


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "name",
        "owner",
        "status",
        "participants_count",
        "created_at",
    )

    list_editable = (
        "status",
    )

    list_filter = (
        "status",
        "created_at",
    )

    search_fields = (
        "name",
        "description",
        "owner__email",
        "owner__name",
        "owner__surname",
    )

    filter_horizontal = (
        "participants",
    )

    @admin.display(description="Количество участников")
    def participants_count(self, obj):
        return obj.participants.count()
