from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.html import format_html

from .models import User


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    model = User

    list_display = (
        "id",
        "avatar_preview",
        "email",
        "name",
        "surname",
        "phone",
        "is_active",
        "is_staff",
    )

    list_filter = (
        "is_active",
        "is_staff",
    )

    search_fields = (
        "email",
        "name",
        "surname",
        "phone",
    )

    ordering = ("created_at",)

    fieldsets = (
        (
            "Основная информация",
            {
                "fields": (
                    "email",
                    "password",
                    "name",
                    "surname",
                    "avatar",
                    "phone",
                    "github_url",
                    "about",
                )
            },
        ),
        (
            "Права доступа",
            {
                "fields": (
                    "is_active",
                    "is_staff",
                    "is_superuser",
                    "groups",
                    "user_permissions",
                )
            },
        ),
        (
            "Даты",
            {
                "fields": (
                    "last_login",
                )
            },
        ),
    )

    add_fieldsets = (
        (
            "Создание пользователя",
            {
                "classes": ("wide",),
                "fields": (
                    "email",
                    "name",
                    "surname",
                    "password1",
                    "password2",
                    "is_active",
                    "is_staff",
                    "is_superuser",
                ),
            },
        ),
    )

    @admin.display(description="Аватар")
    def avatar_preview(self, obj):
        if obj.avatar:
            return format_html(
                '<img src="{}" width="40" height="40" '
                'style="border-radius: 50%;" />',
                obj.avatar.url,
            )

        return "-"
