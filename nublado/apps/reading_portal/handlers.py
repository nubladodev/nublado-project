from html import escape

from telegram import (
    Update,
    ReactionTypeEmoji,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
)
from telegram.error import BadRequest
from telegram.ext import ContextTypes

from django_telegram.utils.telegram import delete_command
from django_telegram.utils.formatting import user_display_name
from django_telegram.jobs import schedule_message_cleanup

from .services.portals import (
    # current_portal,
    ready_portals,
    open_portal,
    close_portal,
    ready_portals,
    edit_reading,
)
from .services.reading_submissions import (
    submit_reading,
    review_reading,
    portal_reading_submissions,
)
from .utils.formatting import (
    format_edited_reading,
    format_reading_submission_list,
)
from .bot_messages import BOT_MESSAGES

OPEN_PORTAL_CALLBACK = "open_portal"


# async def show_current_portal(update: Update, context: ContextTypes.DEFAULT_TYPE):
#     tg_chat = update.effective_chat

#     portal = await current_portal(update, context)


async def show_ready_portals(update: Update, context: ContextTypes.DEFAULT_TYPE):
    tg_chat = update.effective_chat
    tg_message = update.effective_message

    portals = await ready_portals(update)

    if not portals:
        await context.bot.send_message(
            chat_id=tg_chat.id,
            text=str(BOT_MESSAGES["no_ready_portals"]),
            reply_to_message_id=tg_message.message_id,
        )
        return

    message_header = BOT_MESSAGES["ready_reading_portals"]
    buttons = [
        [
            InlineKeyboardButton(
                f"{portal.title}",
                callback_data=f"{OPEN_PORTAL_CALLBACK}:{portal.slug}",
            )
        ]
        for portal in portals
    ]

    keyboard = InlineKeyboardMarkup(buttons)

    bot_message = await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=str(message_header).title(),
        reply_markup=keyboard,
    )

    # Chat cleanup.
    schedule_message_cleanup(
        update,
        context,
        bot_message_ids=[bot_message.message_id],
    )


async def handle_open_portal(update: Update, context: ContextTypes.DEFAULT_TYPE):
    tg_chat = update.effective_chat
    tg_message = update.effective_message
    slug = None

    if context.args:
        slug = context.args[0]

    await open_portal(update, context, slug, True)
    # Delete the lingering command in the chat.
    await delete_command(update)


async def open_portal_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()  # <-- stops the “freezing” spinner
    data = query.data

    if data.startswith(f"{OPEN_PORTAL_CALLBACK}:"):
        slug = data.split(":", 1)[1]

        await open_portal(update, context, slug=slug)
        await query.message.delete()


async def handle_close_portal(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await close_portal(update, context)

    # Delete the lingering command in the chat.
    await delete_command(update)


async def handle_submit_reading(update: Update, context: ContextTypes.DEFAULT_TYPE):
    reading_submission = await submit_reading(update, context)

    if not reading_submission:
        return

    tg_chat = update.effective_chat
    tg_message = update.effective_message
    tg_user = update.effective_user
    portal_reading = reading_submission.portal_reading

    reply_message = (
        f"#pending_{portal_reading.language} : {user_display_name(tg_user)}"
    )

    bot_message = await context.bot.send_message(
        chat_id=tg_chat.id,
        text=reply_message,
        reply_to_message_id=tg_message.message_id,
    )

    await context.bot.set_message_reaction(
        chat_id=update.effective_chat.id,
        message_id=reading_submission.message_id,
        reaction=[ReactionTypeEmoji("⚡️")],
    )

    reading_submission.reply_message_id = bot_message.message_id
    await reading_submission.asave(update_fields=["reply_message_id"])


async def handle_review_reading(update: Update, context: ContextTypes.DEFAULT_TYPE):
    reading_submission = await review_reading(update, context)

    if not reading_submission:
        await delete_command(update)
        return

    tg_user = update.effective_user
    tg_chat = update.effective_chat

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

    await delete_command(update)


async def show_reading_submissions(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Display the reading submissions for the
    currently open Reading Portal.
    """
    tg_chat = update.effective_chat
    tg_message = update.effective_message

    portal, submissions = await portal_reading_submissions(
        update,
        context,
        pending_only=False,
    )

    if not submissions:
        await context.bot.send_message(
            chat_id=tg_chat.id,
            text=str(BOT_MESSAGES["no_readings"]),
            reply_to_message_id=tg_message.message_id,
        )
        return

    submissions_list = format_reading_submission_list(
        portal,
        submissions,
        list_header=str(BOT_MESSAGES["readings"]).title(),
    )

    bot_message = await context.bot.send_message(
        chat_id=tg_chat.id,
        text="\n".join(submissions_list),
    )
  
    # Chat cleanup.
    schedule_message_cleanup(
        update,
        context,
        bot_message_ids=[bot_message.message_id],
    )


async def show_pending_readings(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Display the pending reading submissions for the
    currently open Reading Portal.
    """
    tg_chat = update.effective_chat
    tg_message = update.effective_message

    portal, submissions = await portal_reading_submissions(
        update,
        context,
        pending_only=True,
    )

    if not submissions:
        await context.bot.send_message(
            chat_id=tg_chat.id,
            text=str(BOT_MESSAGES["no_pending_readings"]),
            reply_to_message_id=tg_message.message_id,
        )
        return

    submissions_list = format_reading_submission_list(
        portal,
        submissions,
        list_header=str(BOT_MESSAGES["pending_readings"]).title(),
    )

    bot_message = await context.bot.send_message(
        chat_id=tg_chat.id,
        text="\n".join(submissions_list),
    )
  
    # Chat cleanup.
    schedule_message_cleanup(
        update,
        context,
        bot_message_ids=[bot_message.message_id],
    )


async def handle_edit_reading(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Edit an open Reading Portal's reading by language from text in the chat.
    """
    tg_chat = update.effective_chat
    tg_message = update.effective_message

    # Parse args
    if not context.args:
        await tg_message.reply_text(escape("Usage: /edit_reading <language>"))
        return

    language = context.args[0].lower()

    # Must be reply
    source_message = tg_message.reply_to_message
    if not source_message or not source_message.text:
        await tg_message.reply_text(
            "Error: must be a reply to a text message."
        )
        return

    reading = await edit_reading(
        update,
        language=language,
        text=source_message.text,
    )

    if not reading:
        return

    reading_text = format_edited_reading(reading)

    try:
        await context.bot.edit_message_text(
            chat_id=tg_chat.id,
            message_id=reading.message_id,
            text=reading_text,
            parse_mode="HTML",
        )
    except BadRequest as e:
        await tg_message.reply_text(
            f"Updated DB, but failed to edit message: {e}"
        )
        return

    await tg_message.reply_text(
        f"Updated reading ({language.upper()})."
    )


