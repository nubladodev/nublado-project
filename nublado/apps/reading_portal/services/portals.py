import logging

from telegram import Update
from telegram.ext import ContextTypes
from telegram.error import BadRequest

from django_telegram.models import TelegramChat
from django_telegram.utils.telegram import safe_delete_message
from django_telegram.utils.async_utils import async_call

from ..models import ReadingPortal, PortalReading
from ..exceptions import (
    NoReadyPortal,
    NoOpenPortal,
    OpenPortalExists,
    NoReadingMessageId,
    ReadingPortalError,
)
from ..utils.formatting import format_portal_intro, format_portal_closed, format_reading
from ..bot_messages import BOT_MESSAGES

logger = logging.getLogger("django")


# async def current_portal(update: Update, context: ContextTypes.DEFAULT_TYPE):
#     tg_chat = update.effective_chat
#     chat, created = await async_call(TelegramChat.objects.get_or_create_from_chat, tg_chat)

#     # Get open portal.
#     try:
#         portal = await async_call(ReadingPortal.objects.get_open, chat=chat)
#     except ReadingPortal.DoesNotExist:
#         raise NoOpenPortal()

#     return portal


async def ready_portals(update: Update):
    """
    Return a list of ready Reading Portals.
    """
    tg_chat = update.effective_chat

    chat, created = await async_call(TelegramChat.objects.get_or_create_from_chat, tg_chat)
    portals_qs = (
        ReadingPortal.objects.ready()
        .for_chat(chat)
    )
    portals = [portal async for portal in portals_qs]

    return portals


async def open_portal(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
    slug: str = None,
    notify: bool = False,
):
    """
    Open a ready Reading Portal by slug if provided,
    or open the first ready Reading Portal in the queue.
    """
    tg_chat = update.effective_chat
    tg_message = update.effective_message
    bot = context.bot

    chat, created = await async_call(TelegramChat.objects.get_or_create_from_chat, tg_chat)

    # Make sure an open portal doesn't already exist.
    if await (
        ReadingPortal.objects.open()
        .for_chat(chat)
        .aexists()
    ):
        raise OpenPortalExists()

    # If a slug is provided, attempt to open a Reading Portal with the coresponding slug.
    if slug:
        try:
            portal = await (
                ReadingPortal.objects.ready()
                .for_chat(chat)
                .aget(slug=slug)
            )
        except ReadingPortal.DoesNotExist:
            await context.bot.send_message(
                chat_id=tg_chat.id,
                text=str(BOT_MESSAGES["error.portal_not_found"]),
                reply_to_message_id=tg_message.message_id,
            )
            return
    else:
        # If no slug is provided, ger the next ready Reading Portal in the queue.
        portal = await (
            ReadingPortal.objects.ready()
            .for_chat(chat)
            .order_by("created_at")
            .afirst()
        )

    if not portal:
        # There are no portals ready to be posted.
        raise NoReadyPortal()

    # intro message to be pinned
    intro_text = format_portal_intro(portal)
    intro_message = await bot.send_message(
        chat_id=tg_chat.id,
        text=intro_text,
        parse_mode="HTML",
    )

    # Attempt to open portal or rollback. 
    try:
        await portal.aopen(pinned_message_id=intro_message.message_id)
    except ReadingPortalError:
        await safe_delete_message(intro_message)
        raise

    # Post the portal readings.
    readings = PortalReading.objects.for_portal(portal)

    async for reading in readings:
        reading_text = format_reading(reading)
        reading_message = await bot.send_message(
            chat_id=tg_chat.id,
            text=reading_text,
            parse_mode="HTML",
        )

        # Update the PortalReading message_id for reference in the chat.
        reading.message_id = reading_message.message_id
        await reading.asave(update_fields=["message_id"])

    # Pin the intro message.
    # Non-critical: pin failure should not break portal flow.
    try:
        await bot.pin_chat_message(
            chat_id=tg_chat.id,
            message_id=intro_message.message_id,
            disable_notification=not notify,
        )
    except Exception:
        # log only, don't rollback portal
        logger.warning("Failed to pin intro message for portal %s", portal.slug)

    return portal


async def close_portal(
    update: Update, context: ContextTypes.DEFAULT_TYPE, notify: bool = False
):
    tg_chat = update.effective_chat
    bot = context.bot

    chat, created = await async_call(TelegramChat.objects.get_or_create_from_chat, tg_chat)

    try:
        portal = await async_call(ReadingPortal.objects.get_open, chat=chat)
    except ReadingPortal.DoesNotExist:
        raise NoOpenPortal()

    pinned_message_id = portal.pinned_message_id

    await portal.aclose()

    # Unpin portal intro and pin closing message.
    if pinned_message_id:
        try:
            await bot.unpin_chat_message(
                chat_id=tg_chat.id,
                message_id=pinned_message_id,
            )
        except BadRequest as e:
            logger.warning(f"Failed to unpin portal intro: {e}")

    closed_message = None

    try:
        closed_message = await bot.send_message(
            chat_id=tg_chat.id,
            text=format_portal_closed(),
            reply_to_message_id=pinned_message_id
        )
    except BadRequest as e:
        logger.warning(f"Failed to reply to portal intro with closed message: {e}")

    if not closed_message:
        closed_message = await bot.send_message(
            chat_id=tg_chat.id,
            text=format_portal_closed(),
        )

    try:
        await bot.pin_chat_message(
            chat_id=tg_chat.id,
            message_id=closed_message.message_id,
            disable_notification=not notify,
        )
    except BadRequest as e:
        logger.warning(f"Failed to pin closed message: {e}")


async def edit_reading(
    update: Update,
    *,
    language: str,
    text: str
):
    tg_chat = update.effective_chat

    chat, created = await async_call(TelegramChat.objects.get_or_create_from_chat, tg_chat)

    # Get open portal in chat.
    try:
        portal = await async_call(ReadingPortal.objects.get_open, chat=chat)
    except ReadingPortal.DoesNotExist:
        raise NoOpenPortal()

    # Get existing reading.
    try:
        reading = await PortalReading.objects.aget(
            reading_portal=portal,
            language=language,
        )
    except PortalReading.DoesNotExist:
        return None

    if not reading.message_id:
        raise NoReadingMessageId()

    reading.message_text = text.strip()
    await reading.asave(update_fields=["message_text"])

    return reading



