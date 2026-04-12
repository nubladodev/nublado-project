from html import escape
from telegram.constants import ChatType, ChatMemberStatus

from django.db import models
from django.utils.translation import gettext_lazy as _

from django_nublado_core.models import TimestampModel, LanguageModel
from .managers import (
    TelegramUserManager,
    TelegramChatManager,
    TelegramGroupMemberManager,
)


class TelegramUser(TimestampModel):
    """
    Model for a Telegram user.
    """
    # Telegram id
    id = models.BigIntegerField(primary_key=True)
    username = models.CharField(max_length=255, null=True, blank=True)
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255, null=True, blank=True)
    is_bot = models.BooleanField(default=False)

    objects = TelegramUserManager()

    def __str__(self):
        return f"{self.display_name} : {str(self.id)}"

    @property
    def display_name(self):
        if self.username:
            name = f"@{self.username}"
        else:
            if self.last_name:
                name = f"{self.first_name} {self.last_name}"
            else:
                name = self.first_name
        return name


class TelegramChat(TimestampModel):
    """
    Model for a Telegram chat
    """

    class ChatType(models.TextChoices):
        PRIVATE = ChatType.PRIVATE, _("private")
        GROUP = ChatType.GROUP, _("group")
        SUPERGROUP = ChatType.SUPERGROUP, _("supergroup")
        CHANNEL = ChatType.CHANNEL, _("channel")

    # Telegram id
    id = models.BigIntegerField(primary_key=True)

    # These fields are "snapshots" of their respective values derived from Telegram.
    chat_type = models.CharField(max_length=20, choices=ChatType)
    title = models.CharField(max_length=255, null=True, blank=True)
    username = models.CharField(max_length=255, null=True, blank=True)

    objects = TelegramChatManager()

    def __str__(self):
        return f"{self.id}: {self.title}"


class TelegramGroupSettings(LanguageModel, TimestampModel):
    chat = models.OneToOneField(
        TelegramChat,
        on_delete=models.CASCADE,
        related_name="settings",
    )

    def __str__(self):
        return f"Settings: {self.chat} (language={self.language})"


class TelegramGroupMember(TimestampModel):
    """
    Model for a member of a Telegram group.
    """

    class GroupRole(models.TextChoices):
        MEMBER = ChatMemberStatus.MEMBER, _("member")
        ADMIN = ChatMemberStatus.ADMINISTRATOR, _("admin")
        OWNER = ChatMemberStatus.OWNER, _("owner")

    user = models.ForeignKey(
        TelegramUser,
        on_delete=models.CASCADE,
        related_name="memberships",
    )
    chat = models.ForeignKey(
        TelegramChat,
        on_delete=models.CASCADE,
        related_name="members",
    )

    # This is just a "snapshot" of the group member's role. Don't
    # use it for permissions. Rather, use the role data from Telegram
    # that this field is derived from.
    role = models.CharField(max_length=20, choices=GroupRole)

    is_active = models.BooleanField(default=True)
    joined_at = models.DateTimeField(auto_now_add=True)
    left_at = models.DateTimeField(null=True, blank=True)

    # Optional for group "karma points." This can be extracted to its own
    # table if more elaborate point features are needed.
    points = models.IntegerField(default=0)

    objects = TelegramGroupMemberManager()

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["user", "chat"], name="unique_group_membership"
            )
        ]
        indexes = [
            models.Index(fields=["chat", "-points"]),
        ]

    def __str__(self):
        return f"{self.user} in {self.chat} ({self.role})"

    @property
    def mention_html(self):
        display_name = escape(self.user.display_name)
        return f'<a href="tg://user?id={self.user.id}">{display_name}</a>'
