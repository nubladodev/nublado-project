import re

from telegram import Update
from telegram.ext import ContextTypes, filters

from .services import transfer_points
from .utils import extract_points
from .validators import validate_point_transfer


def make_give_points_handler(
    *,
    point_symbol: str,
    points_map: dict,
    on_success=None,  # async callback(update, context, result)
    on_error=None,  # async callback(update, context, error)
):
    """
    Factory that returns: (POINT_FILTER, give_points_handler)
    This is an attempt to keep behavior and presentation decoupled.
    """

    # Escape symbol in case it's regex-special (e.g. "+", "*").
    escaped_symbol = re.escape(point_symbol)

    # Filter: message must
    #  - be text
    #  - be in a group
    #  - be a normal message
    #  - start with one or more of the point symbol
    POINT_FILTER = (
        filters.TEXT
        & filters.ChatType.GROUPS
        & filters.UpdateType.MESSAGE
        & filters.Regex(rf"^{escaped_symbol}+")
    )

    async def give_points(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """
        Handler triggered when a valid point-giving message is detected.
        """
        tg_message = update.effective_message
        tg_chat = update.effective_chat
        tg_sender = update.effective_user

        # Do nothing if the message isn't a reply.
        if not tg_message or not tg_message.reply_to_message:
            return

        # The telegram user reeiving the points.
        tg_receiver = tg_message.reply_to_message.from_user

        # Validate point transfer.
        error = validate_point_transfer(tg_sender, tg_receiver)

        if error:
            # Core does NOT decide what to say.
            if on_error:
                await on_error(update, context, error)
            return

        num_points = extract_points(tg_message.text, point_symbol, points_map)

        # If symbol count doesn't map to valid value, do nothing.
        if not num_points:
            return

        # Fetch ChatMember objects
        tg_member_sender = await context.bot.get_chat_member(tg_chat.id, tg_sender.id)

        tg_member_receiver = await context.bot.get_chat_member(
            tg_chat.id, tg_receiver.id
        )

        # Persist point transferand return sender_member and receiver_member from db.
        sender_member, receiver_member = await transfer_points(
            tg_chat,
            tg_member_sender,
            tg_member_receiver,
            num_points,
        )

        if on_success:
            await on_success(
                update,
                context,
                {
                    "tg_sender": tg_sender,
                    "tg_receiver": tg_receiver,
                    "sender_member": sender_member,
                    "receiver_member": receiver_member,
                    "num_points": num_points,
                },
            )

    return POINT_FILTER, give_points
