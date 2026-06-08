from telegram import Update, ReactionTypeEmoji
from telegram.ext import ContextTypes, filters

from django_nublado_telegram.jobs import delete_message_job
from .utils import normalize_key
from .services import save_repo_item_service, get_repo_item_service, list_repo_items_service
from .bot_messages import BOT_MESSAGES


HASHTAG_FILTER = filters.TEXT & filters.Regex(r"^#\w+$")


async def save_repo_item(update: Update, context: ContextTypes.DEFAULT_TYPE):
    tg_chat = update.effective_chat
    tg_message = update.effective_message

    if not tg_message or not tg_message.reply_to_message:
        return

    if not context.args:
        await tg_message.reply_text("Usage: /save <key>")
        return

    key = normalize_key(" ".join(context.args))

    replied_to = tg_message.reply_to_message

    repo_item = await save_repo_item_service(update, context, key, replied_to.message_id)

    bot_message = BOT_MESSAGES["note_saved"].format(key=key)

    await context.bot.send_message(
        chat_id=tg_chat.id,
        text=str(bot_message),
        reply_to_message_id=tg_message.message_id,
    )


async def get_repo_item(update: Update, context: ContextTypes.DEFAULT_TYPE):
    tg_message = update.effective_message

    if not tg_message or not tg_message.text:
        return

    text = tg_message.text.strip()

    if not text.startswith("#") or " " in text:
        return

    key = normalize_key(text[1:])

    repo_item = await get_repo_item_service(update, context, key)

    if not repo_item:
        return

    await context.bot.copy_message(
        chat_id=tg_message.chat_id,
        from_chat_id=repo_item.repo.repo_chat_id,
        message_id=repo_item.message_id,
        reply_to_message_id=tg_message.message_id,
    )
    await context.bot.set_message_reaction(
        chat_id=tg_message.chat_id,
        message_id=tg_message.message_id,
        reaction=[ReactionTypeEmoji("✍️")],
    )


async def list_repo_items(update: Update, context: ContextTypes.DEFAULT_TYPE):
    tg_chat = update.effective_chat
    tg_message = update.effective_message
    search_key = normalize_key(" ".join(context.args)) if context.args else None

    repo_items = await list_repo_items_service(update, context, search_key)

    if repo_items:
        header = (
            f"Notes with '<b>{search_key}</b>':\n\n"
            if search_key else "Notes:\n\n"
        )
        body = "\n".join(f"#{item.key}" for item in repo_items)

        notes_message = await context.bot.send_message(
            chat_id=tg_chat.id,
            text=f"{header}{body}"
        )
    else:
       notes_message = await context.bot.send_message(
            chat_id=tg_chat.id,
            text="No notes found."
        )

    # Make the message and command disappear after 30 seconds.
    context.job_queue.run_once(
        delete_message_job,
        30,
        data={
            "chat_id": tg_chat.id,
            "message_ids": [tg_message.message_id, notes_message.message_id],
        },
    )