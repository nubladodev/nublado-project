from import_export.admin import ImportExportModelAdmin

from django.contrib import admin
from django_nublado_telegram.models import (
    TelegramUser,
    TelegramChat,
    TelegramGroupMember,
    TelegramGroupSettings,
)


@admin.register(TelegramUser)
class TelegramUserAdmin(ImportExportModelAdmin):
    pass


@admin.register(TelegramChat)
class TelegramChatAdmin(ImportExportModelAdmin):
    pass


@admin.register(TelegramGroupMember)
class TelegramGroupMemberAdmin(ImportExportModelAdmin):
    pass


@admin.register(TelegramGroupSettings)
class TelegramGroupSettingsAdmin(ImportExportModelAdmin):
    pass