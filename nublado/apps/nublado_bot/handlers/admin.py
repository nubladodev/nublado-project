from telegram import Update
from telegram.ext import ContextTypes
from telegram.error import BadRequest

from django_telegram.models import TelegramChat


async def list_groups(update:Update, context: ContextTypes.DEFAULT_TYPE):
    """
    List the groups the bot is active in.
    """
    tg_chat = update.effective_chat

    group_list = ["Groups: \n"]

    groups = TelegramChat.objects.filter(
        chat_type=TelegramChat.ChatType.SUPERGROUP,
    )

    async for chat in groups:
        group_list.append(chat.title)

    await context.bot.send_message(
        chat_id=tg_chat.id,
        text="\n".join(group_list),
    )


async def broadcast_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Send a message to all the groups the bot is active in.
    """

    groups = TelegramChat.objects.filter(
        chat_type=TelegramChat.ChatType.SUPERGROUP,
    )

    async for chat in groups:
        try:
            await context.bot.send_message(
                chat_id=chat.id,
                text="This is a broadcast message."
            )
        except BadRequest:
            pass