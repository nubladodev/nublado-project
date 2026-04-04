from django.utils.translation import gettext_lazy as _

BOT_MESSAGES = {
    "start": _("nublado.bot.start"),
    "hello": _("nublado.bot.hello"),
    # Group settings
    "language_set": _("nublado.bot.language_set {language}"),
    "error.language_active": _("nublado.bot.error.language_active {language}"),
    "error.invalid_language": _("nublado.bot.error.invalid_language: {language_keys}"),
}
