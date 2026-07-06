import time

from telegram import Update
from telegram.ext import ContextTypes

from ..bot_messages import (
    START,
    HELLO,
)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    tg_chat = update.effective_chat
    tg_message = update.effective_message

    await context.bot.send_message(
        chat_id=tg_chat.id,
        text=str(START),
        reply_to_message_id=tg_message.message_id,
    )


async def hello(update: Update, context: ContextTypes.DEFAULT_TYPE):
    tg_chat = update.effective_chat

    await context.bot.send_message(
        chat_id=tg_chat.id,
        text=str(HELLO),
    )


async def unix_timestamp(update: Update, context: ContextTypes.DEFAULT_TYPE):
    tg_chat = update.effective_chat
    tg_message = update.effective_message
    epoch_seconds = int(time.time())
    bot_message = f"<code>{epoch_seconds}</code>"

    await context.bot.send_message(
        chat_id=tg_chat.id,
        text=bot_message,
        reply_to_message_id=tg_message.message_id,
    )

