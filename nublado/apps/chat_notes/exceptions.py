from django.utils.translation import gettext_lazy as _

#from .bot_messages import BOT_MESSAGES


class ChatNotesError(Exception):
    """Base exception for Group Points domain."""

    default_message = _("chat_notes.bot.error.default")

    def __init__(self, message=None, **kwargs):
        self.message = message or self.default_message
        self.kwargs = kwargs
        super().__init__(self.message)

    def __str__(self):
        # For lazy translations with placeholders.
        return str(self.message).format(**self.kwargs)


class RepoNotConfigured(ChatNotesError):
    pass

class RepoNotFound(ChatNotesError):
    pass