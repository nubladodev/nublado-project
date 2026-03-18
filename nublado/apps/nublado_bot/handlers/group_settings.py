from telegram import Update
from telegram.ext import ContextTypes

from django.utils.translation import override, gettext_lazy as _
from django.conf import settings

from django_telegram.utils.language import (
    get_context_language,
    normalize_language_code,
)
from django_telegram.services.language import set_chat_language
from django_telegram.decorators import with_language

from ..bot_messages import BOT_MESSAGES


@with_language
async def set_bot_language(update: Update, context: ContextTypes.DEFAULT_TYPE):
    tg_chat = update.effective_chat
    tg_message = update.effective_message

    # The bot command language-code argument.
    if len(context.args) != 1:
        await tg_message.reply_text(_("Usage: /set_bot_language <language_code>"))
        return

    language_code = normalize_language_code(context.args[0])

    # Check if language_code is in acceptable language codes.
    if not language_code:
        keys = list(settings.LANGUAGES_DICT.keys())
        bot_message = BOT_MESSAGES["error_invalid_language_code"].format(
            language_keys=keys
        )
        await context.bot.send_message(
            chat_id=tg_chat.id,
            text=str(bot_message),
            reply_to_message_id=tg_message.message_id,
        )
        return

    current_language = get_context_language(context)

    if language_code == current_language:
        bot_message = BOT_MESSAGES["bot_language_already_active"].format(
            language=_(settings.LANGUAGES_DICT[language_code])
        )
        await context.bot.send_message(
            chat_id=tg_chat.id,
            text=str(bot_message),
            reply_to_message_id=tg_message.message_id,
        )
        return

    # If the language_code isn't the current language, update the group settings language and
    # context data bot language, then activate the new language.
    await set_chat_language(update, context, language_code)

    with override(language_code):
        bot_message = BOT_MESSAGES["bot_language_set"].format(
            language=_(settings.LANGUAGES_DICT[language_code])
        )
        await context.bot.send_message(
            chat_id=tg_chat.id,
            text=str(bot_message),
            reply_to_message_id=tg_message.message_id,
        )
