from django.utils.translation import gettext_lazy as _

from .bot_messages import BOT_MESSAGES
from .constants import POINTS_NAME


class GroupPointsError(Exception):
    """Base exception for Group Points domain."""

    default_message = _("group_points.bot.error.default")

    def __init__(self, message=None):
        self.message = message or self.default_message
        super().__init__(self.message)

    def __str__(self):
        return str(self.message)


class BotReceiverError(GroupPointsError):
    default_message = BOT_MESSAGES["error.no_give_points_bot"].format(
        points_name=_(POINTS_NAME)
    )


class SelfReceiverError(GroupPointsError):
    default_message = default_message = BOT_MESSAGES["error.no_give_points_self"]
