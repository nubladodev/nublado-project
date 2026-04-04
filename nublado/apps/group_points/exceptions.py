from django.utils.translation import gettext_lazy as _


class GroupPointsError(Exception):
    """Base exception for Group Points domain."""

    default_message = _("group_points.bot.error.default")

    def __init__(self, message=None):
        self.message = message or self.default_message
        super().__init__(self.message)

    def __str__(self):
        return str(self.message)


class BotReceiverError(GroupPointsError):
    default_message = _("group_points.bot.error.no_send_points_to_bot")


class SelfReceiverError(GroupPointsError):
    default_message = _("group_points.bot.error.no_send_points_to_self")
