from telegram.ext import ContextTypes
from telegram.error import BadRequest


async def delete_message_job(context: ContextTypes.DEFAULT_TYPE):
    job = context.job
    chat_id = job.data.get("chat_id")
    message_ids = job.data.get("message_ids", [])

    if not chat_id:
        return

    for message_id in message_ids:
        try:
            await context.bot.delete_message(chat_id, message_id)
        except BadRequest:
            pass