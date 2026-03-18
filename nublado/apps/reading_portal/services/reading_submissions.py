from telegram import Update
from telegram.ext import ContextTypes
from telegram.error import BadRequest

from django_telegram.models import TelegramChat, TelegramGroupMember

from ..models import ReadingPortal, PortalReading, ReadingSubmission
from ..exceptions import (
    NoOpenPortal,
    NoReplyToReading,
    NoPendingReading,
)


async def submit_reading_service(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Submit a reading to the Reading Portal.

    Returns: A ReadingSubmission object, or None.
    """
    tg_chat = update.effective_chat
    tg_message = update.effective_message
    tg_user = update.effective_user
    bot = context.bot

    # Must be a voice message
    if not tg_message or not tg_message.voice:
        return None

    # Must reply to a reading
    text_message = tg_message.reply_to_message
    if not text_message or not text_message.text:
        return None

    if text_message.from_user.id != context.bot.id:
        return None

    chat = await TelegramChat.objects.aget_or_create_from_telegram_chat(tg_chat)

    try:
        portal = await ReadingPortal.objects.aget_open(chat=chat)
    except ReadingPortal.DoesNotExist:
        raise NoOpenPortal()

    try:
        reading = await PortalReading.objects.with_portal().aget(
            reading_portal=portal, 
            message_id=text_message.message_id,
        )
    except PortalReading.DoesNotExist:
        raise NoReplyToReading()

    tg_member = await bot.get_chat_member(tg_chat.id, tg_user.id)
    member = await TelegramGroupMember.objects.aget_or_create_from_chat_member(
        tg_member, tg_chat
    )

    # Delete old reading submission if this is a resubmission.
    old_submission = await (
        ReadingSubmission.objects
        .pending()
        .filter(
            portal_reading=reading,
            member=member,
        )
        .afirst()
    )

    if old_submission:
        # Delete the old voice message
        try:
            await bot.delete_message(
                chat_id=tg_chat.id,
                message_id=old_submission.message_id
            )
        except BadRequest:
            # Message may already be deleted.
            pass

        # Delete the old reading submissions bot reply if it exists.
        if old_submission.reply_message_id:
            try:
                await bot.delete_message(
                    chat_id=tg_chat.id,
                    message_id=old_submission.reply_message_id
                )
            except BadRequest:
                pass

        # Hard delete the old submission from the db.
        await old_submission.adelete()

    # Create a new reading submission.
    reading_submission = await ReadingSubmission.objects.acreate(
        portal_reading=reading,
        member=member,
        message_id=tg_message.message_id,
        reading_status=ReadingSubmission.ReadingStatus.PENDING,
    )

    return reading_submission


async def review_reading_service(update: Update, context: ContextTypes.DEFAULT_TYPE):
    tg_chat = update.effective_chat
    tg_message = update.effective_message

    chat = await TelegramChat.objects.aget_or_create_from_telegram_chat(tg_chat)

    # Check if there is an open Reading Portal in the group.
    try:
        portal = await ReadingPortal.objects.aget_open(chat=chat)
    except ReadingPortal.DoesNotExist:
        raise NoOpenPortal()

    if not tg_message or not tg_message.reply_to_message:
        return None

    voice_message = tg_message.reply_to_message

    if not voice_message.voice:
        return None

    # Check if voice message is a pending reading submission. 
    try:
        reading_submission = await (
            ReadingSubmission.objects
            .with_user()
            .pending()
            .for_portal(portal)
            .aget(
                message_id=voice_message.message_id,
            )
        )
    except ReadingSubmission.DoesNotExist:
        raise NoPendingReading()

    reading_submission.reading_status = ReadingSubmission.ReadingStatus.REVIEWED
    await reading_submission.asave(update_fields=["reading_status"])

    return reading_submission


async def get_pending_readings_service(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Return pending reading submissions for the currently open
    Reading Portal.
    """
    tg_chat = update.effective_chat

    chat = await TelegramChat.objects.aget_or_create_from_telegram_chat(tg_chat)

    # Get reading submissions from currently upen Reading Portal.
    try:
        portal = await ReadingPortal.objects.aget_open(chat=chat)
    except ReadingPortal.DoesNotExist:
        raise NoOpenPortal()

    pending_readings = ( 
        ReadingSubmission.objects
        .with_portal()
        .with_user()
        .pending()
        .filter(
            portal_reading__reading_portal_id=portal.id
        )
    )

    return pending_readings
