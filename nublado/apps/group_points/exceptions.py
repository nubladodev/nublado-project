from django.utils.translation import gettext_lazy as _

from .bot_messages import (
    ERROR_NO_GIVE_POINTS_BOT,
    ERROR_NO_GIVE_POINTS_SELF,
)


class GroupPointsError(Exception):
    """Base exception for Group Points domain."""

    default_message = _("group_points.bot.error.default")

    def __init__(self, message=None, **kwargs):
        self.message = message or self.default_message
        self.kwargs = kwargs
        super().__init__(self.message)

    def __str__(self):
        # For lazy translations with placeholders.
        return str(self.message).format(**self.kwargs)


class BotReceiverError(GroupPointsError):
    # placeholder: points_name
    default_message = ERROR_NO_GIVE_POINTS_BOT


class SelfReceiverError(GroupPointsError):
    # placeholder: points_name
    default_message = default_message = ERROR_NO_GIVE_POINTS_SELF
