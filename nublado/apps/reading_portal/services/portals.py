from telegram import Update
from telegram.ext import ContextTypes
from telegram.error import BadRequest

from django.utils.translation import gettext_lazy as _

from django_telegram.models import TelegramChat

from ..models import ReadingPortal, PortalReading
from ..exceptions import NoDraftPortal, NoOpenPortal, OpenPortalExists, EmptyPortal
from .formatting import format_portal_intro, format_portal_closed


async def list_draft_portals_service(
    update: Update, context: ContextTypes.DEFAULT_TYPE
):
    tg_chat = update.effective_chat

    chat = await TelegramChat.objects.aget_or_create_from_telegram_chat(tg_chat)
    portals = ReadingPortal.objects.draft().from_chat(chat)

    return portals


async def open_portal_service(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
    slug: str = None,
    notify: bool = False,
):
    """
    Open the next draft portal for the given Telegram chat.
    """
    tg_chat = update.effective_chat
    tg_message = update.effective_message
    bot = context.bot

    chat = await TelegramChat.objects.aget_or_create_from_telegram_chat(tg_chat)

    # Check if an open portal already exists in the group.
    existing_open = await ReadingPortal.objects.filter(
        chat=chat, portal_status=ReadingPortal.PortalStatus.OPEN
    ).aexists()

    if existing_open:
        raise OpenPortalExists()

    if slug:
        try:
            portal = await ReadingPortal.objects.draft().from_chat(chat).aget(slug=slug)
        except ReadingPortal.DoesNotExist:
            await context.bot.send_message(
                chat_id=tg_chat.id,
                text=str(_("reading_portal.error.portal_not_found")),
                reply_to_message_id=tg_message.message_id,
            )
            return
    else:
        portal = await ReadingPortal.objects.anext_draft(chat=chat)

    if not portal:
        raise NoDraftPortal()

    if not await portal.ahas_readings():
        raise EmptyPortal()

    intro_text = format_portal_intro(portal)

    intro_message = await bot.send_message(
        chat_id=tg_chat.id,
        text=intro_text,
        parse_mode="HTML",
    )

    readings = PortalReading.objects.for_portal(portal)

    async for reading in readings:

        language_label = reading.language.upper()
        header = f"🌧 <b>Reading: {language_label}</b>"
        reading_text = f"{header}\n\n{reading.message_text}"

        reading_message = await bot.send_message(
            chat_id=tg_chat.id,
            text=reading_text,
            parse_mode="HTML",
        )

        reading.message_id = reading_message.message_id
        await reading.asave(update_fields=["message_id"])

    await bot.pin_chat_message(
        chat_id=tg_chat.id,
        message_id=intro_message.message_id,
        disable_notification=not notify,
    )

    portal.pinned_message_id = intro_message.message_id
    portal.portal_status = ReadingPortal.PortalStatus.OPEN

    await portal.asave(update_fields=["portal_status", "pinned_message_id"])

    return portal


async def close_open_portal_service(
    update: Update, context: ContextTypes.DEFAULT_TYPE, notify: bool = False
):
    tg_chat = update.effective_chat
    bot = context.bot

    chat = await TelegramChat.objects.aget_or_create_from_telegram_chat(tg_chat)

    try:
        portal = await ReadingPortal.objects.aget_open(chat=chat)
    except ReadingPortal.DoesNotExist:
        raise NoOpenPortal()

    # A copy of the old pinned message id.
    old_pin = portal.pinned_message_id

    portal.portal_status = portal.PortalStatus.CLOSED
    portal.pinned_message_id = None
    await portal.asave(update_fields=["portal_status", "pinned_message_id"])

    closed_message = None

    # Unpin intro message if it exists.
    if old_pin:
        try:
            await bot.unpin_chat_message(
                chat_id=tg_chat.id,
                message_id=old_pin,
            )
        except BadRequest:
            pass

        try:
            closed_message = await bot.send_message(
                chat_id=tg_chat.id,
                text=format_portal_closed(),
                reply_to_message_id=old_pin,
            )
        except BadRequest:
            pass

    if not closed_message:
        closed_message = await bot.send_message(
            chat_id=tg_chat.id,
            text=format_portal_closed(),
        )

    await bot.pin_chat_message(
        chat_id=tg_chat.id,
        message_id=closed_message.message_id,
        disable_notification=not notify,
    )
