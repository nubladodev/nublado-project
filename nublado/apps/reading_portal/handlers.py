from collections import defaultdict

from telegram import (
    Update,
    ReactionTypeEmoji,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
)
from telegram.error import BadRequest
from telegram.ext import ContextTypes


from django_telegram.utils.helpers import message_link
from django_telegram.utils.telegram import delete_command
from django_telegram.utils.formatting import user_display_name
from django_telegram.jobs import delete_message_job

from .services.portals import (
    open_portal_service,
    close_portal_service,
    list_ready_portals_service,
)
from .services.reading_submissions import (
    submit_reading_voice_message_service,
    review_reading_service,
    get_pending_readings_service,
)
from .bot_messages import BOT_MESSAGES

OPEN_PORTAL_CALLBACK = "open_portal"


async def open_portal(update: Update, context: ContextTypes.DEFAULT_TYPE):
    tg_chat = update.effective_chat
    tg_message = update.effective_message
    slug = None

    if context.args:
        slug = context.args[0]

    await open_portal_service(update, context, slug, True)

    # Delete the lingering command in the chat.
    await delete_command(update)


async def open_portal_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()  # <-- stops the “freezing” spinner
    data = query.data

    if data.startswith(f"{OPEN_PORTAL_CALLBACK}:"):
        slug = data.split(":", 1)[1]

        await open_portal_service(update, context, slug=slug)
        await query.message.delete()


async def close_portal(update: Update, context: ContextTypes.DEFAULT_TYPE):
    tg_chat = update.effective_chat
    tg_message = update.effective_message

    await close_portal_service(update, context)

    # Delete the lingering command in the chat.
    await delete_command(update)


async def list_ready_portals(update: Update, context: ContextTypes.DEFAULT_TYPE):
    tg_chat = update.effective_chat
    tg_message = update.effective_message

    portals = await list_ready_portals_service(update, context)

    if not await portals.aexists():
        await context.bot.send_message(
            chat_id=tg_chat.id,
            text=str(BOT_MESSAGES["error.no_ready_portals"]),
            reply_to_message_id=tg_message.message_id,
        )
        return

    bot_message = BOT_MESSAGES["ready_reading_portals"]
    buttons = []

    async for portal in portals:
        buttons.append(
            [
                InlineKeyboardButton(
                    f"{portal.title}",
                    callback_data=f"{OPEN_PORTAL_CALLBACK}:{portal.slug}",
                )
            ]
        )

    keyboard = InlineKeyboardMarkup(buttons)

    portals_message = await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=str(bot_message).title(),
        reply_markup=keyboard,
    )

    context.job_queue.run_once(
        delete_message_job,
        30,
        data={
            "chat_id": tg_chat.id,
            "message_ids": [tg_message.message_id, portals_message.message_id],
        },
    )


async def submit_reading(update: Update, context: ContextTypes.DEFAULT_TYPE):
    tg_chat = update.effective_chat
    tg_message = update.effective_message

    reading_submission = await submit_reading_voice_message_service(update, context)

    if reading_submission:
        tg_user = update.effective_user
        portal_reading = reading_submission.portal_reading
        bot_message = (
            f"#pending_{portal_reading.language} : {user_display_name(tg_user)}"
        )

        reply_message = await context.bot.send_message(
            chat_id=tg_chat.id,
            text=bot_message,
            reply_to_message_id=tg_message.message_id,
        )

        await context.bot.set_message_reaction(
            chat_id=update.effective_chat.id,
            message_id=reading_submission.message_id,
            reaction=[ReactionTypeEmoji("⚡️")],
        )

        reading_submission.reply_message_id = reply_message.message_id
        await reading_submission.asave(update_fields=["reply_message_id"])


async def pending_readings(update: Update, context: ContextTypes.DEFAULT_TYPE):
    tg_message = update.effective_message
    tg_chat = update.effective_chat

    pending_readings = await get_pending_readings_service(update, context)

    if not await pending_readings.aexists():
        await context.bot.send_message(
            chat_id=tg_chat.id,
            text=str(BOT_MESSAGES["error.no_pending_readings"]),
            reply_to_message_id=tg_message.message_id,
        )
        return

    readings_by_member = defaultdict(list)

    async for pending_reading in pending_readings:
        readings_by_member[pending_reading.member].append(pending_reading)

    readings_list = [f"{str(BOT_MESSAGES["pending_readings"]).title()} \n"]

    for member, readings in readings_by_member.items():
        language_links = []

        for reading in readings:
            link = message_link(tg_chat.id, reading.message_id)
            language = reading.portal_reading.language.upper()
            language_links.append(f'<a href="{link}">{language}</a>')

        readings_list.append(f"{member.mention_html}: {', '.join(language_links)}")

    readings_message = await context.bot.send_message(
        chat_id=tg_chat.id,
        text="\n".join(readings_list),
    )

    context.job_queue.run_once(
        delete_message_job,
        30,
        data={
            "chat_id": tg_chat.id,
            "message_ids": [tg_message.message_id, readings_message.message_id],
        },
    )


async def review_reading(update: Update, context: ContextTypes.DEFAULT_TYPE):
    tg_chat = update.effective_chat
    tg_message = update.effective_message

    reading_submission = await review_reading_service(update, context)

    if reading_submission:
        tg_user = update.effective_user
        tg_chat = update.effective_chat
        portal_reading = reading_submission.portal_reading

        await context.bot.set_message_reaction(
            chat_id=tg_chat.id,
            message_id=reading_submission.message_id,
            reaction=[ReactionTypeEmoji("💯")],
        )

        bot_message = BOT_MESSAGES["reading_reviewed"].format(
            reviewer_name=user_display_name(tg_user)
        )
        await context.bot.send_message(
            chat_id=tg_chat.id,
            text=str(bot_message),
            reply_to_message_id=reading_submission.message_id,
        )

        if reading_submission.reply_message_id:
            try:
                await context.bot.delete_message(
                    chat_id=tg_chat.id, message_id=reading_submission.reply_message_id
                )
            except BadRequest:
                pass

    # Delete the lingering command in the chat.
    await delete_command(update)
