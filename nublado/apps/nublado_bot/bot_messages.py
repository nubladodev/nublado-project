from django.utils.translation import gettext_lazy as _

# Translators: Message when the bot has started.
# Example: Nublado bot has started.
START = _("nublado.bot.start")

# Translators: Message to greet the group.
# Example: Hello, everybody.
HELLO = _("nublado.bot.hello")

# Translators: Message when the bot language has been changed.
# {language} = native name of the language (e.g., español, English, Deutsch).
# Example: The bot's language has been set to English.
LANGUAGE_SET = _("nublado.bot.language_set {language}")

# Translators: Message when attempting to change the bot's language to one that's already active.
# {language} = native name of the language (e.g., español, English, Deutsch).
# Example: The bot's language is already set to English.
ERROR_LANGUAGE_ACTIVE = _("nublado.bot.error.language_active {language}")

# Translators: Message when attempting to change the bot's language to an invalid or unsupported language.
# {language_keys} = a list of the supported language keys (e.g., en, es, de).
# Example: Invalid language key. Valid language keys are [en, es, de].
ERROR_INVALID_LANGUAGE = _("nublado.bot.error.invalid_language: {language_keys}")

BOT_MESSAGES = {
    "start": START,
    "hello": HELLO,
    # Group settings
    "language_set": LANGUAGE_SET,
    "error.language_active": ERROR_LANGUAGE_ACTIVE,
    "error.invalid_language": ERROR_INVALID_LANGUAGE,
}
