from django.utils.translation import gettext_lazy as _


class ReadingPortalError(Exception):
    """Base exception for Reading Portal domain."""

    default_message = _("Reading Portal error")

    def __init__(self, message=None):
        self.message = message or self.default_message
        super().__init__(self.message)

    def __str__(self):
        return str(self.message)

class PortalNotReady(ReadingPortalError):
    """
    Exception raised when a portal is required to be ready, and it isn't.
    """
    default_message = _("reading_portal.bot.error.portal_not_ready")


class PortalAlreadyOpen(ReadingPortalError):
    default_message = _("reading_portal.bot.error.portal_already_open")

class NoReplyToAudio(ReadingPortalError):
    default_message = _("reading_portal.bot.error.no_reply_to_audio")


class NoReplyToReading(ReadingPortalError):
    default_message = _("reading_portal.bot.error.no_reply_to_reading")


class NoAudioReplyToText(ReadingPortalError):
    default_message = _("reading_portal.bot.error.no_reply_to_text")


class NoDraftPortal(ReadingPortalError):
    default_message = _("reading_portal.bot.error.no_draft_portal")


class NoReadyPortal(ReadingPortalError):
    """
    Exception raised when there is no ready portal.
    """
    default_message = _("reading_portal.bot.error.no_ready_portal")


class NoOpenPortal(ReadingPortalError):
    default_message = _("reading_portal.bot.error.no_open_portal")


class OpenPortalExists(ReadingPortalError):
    default_message = _("reading_portal.bot.error.open_portal_exists")


class EmptyPortal(ReadingPortalError):
    default_message = _("reading_portal.bot.error.empty_portal")


class NoPendingReading(ReadingPortalError):
    default_message = _("reading_portal.bot.error.no_pending_reading")


class NoExistingReading(ReadingPortalError):
    default_message = _("reading_portal.bot.error.no_existing_reading")


class NoReadingMessageId(ReadingPortalError):
    default_message = _("reading_portal.bot.error.no_reading_message_id")
