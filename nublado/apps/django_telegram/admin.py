from django.contrib import admin

from .models import (
    TelegramUser,
    TelegramChat,
    TelegramGroupMember,
    TelegramGroupSettings,
)


@admin.register(TelegramChat)
class TelegramChatAdmin(admin.ModelAdmin):

    list_display = (
        "id",
        "title",
        "username",
        "chat_type",
        "date_created",
    )

    search_fields = (
        "id",
        "title",
        "username",
    )

    readonly_fields = (
        "id",
        "chat_type",
        "date_created",
        "title",
        "username",
    )

    ordering = ("-date_created",)


@admin.register(TelegramUser)
class TelegramUserAdmin(admin.ModelAdmin):
    list_display = [
        "id",
        "username",
        "first_name",
        "last_name",
        "is_bot",
        "date_created",
        "date_updated",
    ]

    search_fields = (
        "id",
        "username",
        "first_name",
        "last_name",
    )

    readonly_fields = (
        "id",
        "is_bot",
        "date_created",
        "date_updated",
    )

    list_filter = ("is_bot",)


@admin.register(TelegramGroupSettings)
class TelegramGroupSettingsAdmin(admin.ModelAdmin):
    list_display = (
        "chat",
        "language",
    )

    list_editable = ("language",)

    search_fields = (
        "chat__id",
        "chat__title",
    )


@admin.register(TelegramGroupMember)
class TelegramGroupMemberAdmin(admin.ModelAdmin):
    list_display = (
        "chat",
        "user",
        "points",
        "date_created",
    )

    list_filter = ("chat",)

    search_fields = (
        "chat__title",
        "user__username",
        "user__id",
    )

    ordering = ("-points",)
