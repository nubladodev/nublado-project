import logging

from telegram import Update
from telegram.ext import ContextTypes
from telegram.error import BadRequest

from django_telegram.models import TelegramChat, TelegramGroupMember
from django_telegram.utils.async_utils import async_call

from ..models import ReadingPortal, PortalReading, ReadingSubmission
from ..exceptions import (
    NoPortal,
    NoOpenPortal,
    NoReplyToReading,
    NoPendingReading,
)

logger = logging.getLogger("django")


async def submit_reading_voice_message_service(
    update: Update, context: ContextTypes.DEFAULT_TYPE
):
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

    # Voice message must be a reply to a text message.
    tg_reply_to_message = tg_message.reply_to_message
    if not tg_reply_to_message or not tg_reply_to_message.text:
        return None

    # Readings are posted by the bot, so ignore text messages from other sources.
    if tg_reply_to_message.from_user.id != context.bot.id:
        return None

    chat, created = await async_call(TelegramChat.objects.get_or_create_from_chat, tg_chat)

    try:
        portal = await async_call(ReadingPortal.objects.get_open, chat=chat)
    except ReadingPortal.DoesNotExist:
        return None

    try:
        reading = await PortalReading.objects.with_portal().aget(
            reading_portal=portal,
            message_id=tg_reply_to_message.message_id,
        )
    except PortalReading.DoesNotExist:
        return None

    tg_member = await bot.get_chat_member(tg_chat.id, tg_user.id)
    member, created = await async_call(
        TelegramGroupMember.objects.get_or_create_from_chat_member,
        tg_member,
        tg_chat
    )

    # Delete old reading submission if this is a resubmission.
    old_submission = await (
        ReadingSubmission.objects.pending()
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
                chat_id=tg_chat.id, message_id=old_submission.message_id
            )
        except BadRequest as e:
            # Message may already be deleted.
            logger.warning("BadRequest: %s", e)

        # Delete the old reading submissions bot reply if it exists.
        if old_submission.reply_message_id:
            try:
                await bot.delete_message(
                    chat_id=tg_chat.id, message_id=old_submission.reply_message_id
                )
            except BadRequest as e:
                logger.warning("BadRequest: %s", e)

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

    chat, created = await async_call(TelegramChat.objects.get_or_create_from_chat, tg_chat)

    # Current reading portal (open or last closed)
    portal = await async_call(ReadingPortal.objects.current, chat=chat)
    if not portal:
        raise NoPortal()

    if not tg_message or not tg_message.reply_to_message:
        return None

    tg_reply_to_message = tg_message.reply_to_message

    if not tg_reply_to_message.voice:
        return None

    # Check if voice message is a pending reading submission.
    try:
        reading_submission = await (
            ReadingSubmission.objects.with_user()
            .for_portal(portal)
            .aget(
                message_id=tg_reply_to_message.message_id,
            )
        )
    except ReadingSubmission.DoesNotExist:
        raise NoPendingReading()

    # Allow multiple reviews, but change the status of the reading submission from pending to reviewed
    # with the first review to exclude it from the pending list.
    if reading_submission.reading_status != ReadingSubmission.ReadingStatus.REVIEWED:
        reading_submission.reading_status = ReadingSubmission.ReadingStatus.REVIEWED
        await reading_submission.asave(update_fields=["reading_status"])

    return reading_submission

async def get_portal_pending_readings_service(
    update: Update, context: ContextTypes.DEFAULT_TYPE
):
    """
    Return current portal (currently open or last closed) and its 
    pending readings submissions.
    """
    tg_chat = update.effective_chat

    chat, created = await async_call(TelegramChat.objects.get_or_create_from_chat, tg_chat)

    # Get pending reading submissions from currently open
    # or the last closed Reading Portal if none is open.
    portal = await async_call(ReadingPortal.objects.current, chat=chat)
    if not portal:
        raise NoPortal()

    pending_readings = (
        ReadingSubmission.objects.with_portal()
        .with_user()
        .pending()
        .filter(portal_reading__reading_portal_id=portal.id)
    )

    return portal, pending_readings

