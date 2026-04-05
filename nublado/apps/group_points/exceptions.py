from django.utils.translation import gettext_lazy as _

from .bot_messages import BOT_MESSAGES


class GroupPointsError(Exception):
    """Base exception for Group Points domain."""

    default_message = _("group_points.bot.error.default")

    def __init__(self, message=None, **kwargs):
        self.message = message or self.default_message
        self.kwargs = kwargs
        super().__init__(self.message)

    def __str__(self):
        return str(self.message).format(**self.kwargs)


class BotReceiverError(GroupPointsError):
    default_message = BOT_MESSAGES["error.no_give_points_bot"]


class SelfReceiverError(GroupPointsError):
    default_message = default_message = BOT_MESSAGES["error.no_give_points_self"]
