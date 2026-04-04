import logging

from telegram import Update
from telegram.ext import ContextTypes

from reading_portal.exceptions import ReadingPortalError
from group_points.exceptions import GroupPointsError

logger = logging.getLogger("django")


async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    error = context.error
    tg_chat = update.effective_chat if update else None
    tg_message = update.effective_message if update else None

    if isinstance(error, (ReadingPortalError, GroupPointsError)):
        if tg_chat:
            await context.bot.send_message(
                chat_id=tg_chat.id,
                text=str(error),
                reply_to_message_id=(
                    update.effective_message.message_id if tg_message else None
                ),
            )
        return

    logger.exception("Unhandled error", exc_info=error)

    if tg_chat:
        await context.bot.send_message(
            chat_id=tg_chat.id,
            text="Something went wrong. Try again later.",
        )
