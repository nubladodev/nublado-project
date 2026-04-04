import re

from telegram import Update
from telegram.ext import ContextTypes, filters

from .services import transfer_points
from .utils import extract_points
from .exceptions import BotReceiverError, SelfReceiverError

POINT_FILTER = (
    filters.TEXT
    & filters.ChatType.GROUPS
    & filters.UpdateType.MESSAGE
    & filters.Regex(rf"^{escaped_symbol}+")
)

POINT_SYMBOL = re.escape("+")

# Two symbols for 1 point, three symbols for 2 points...
POINTS_MAP = {
    2: 1,
    3: 2,
    4: 4,
}

POINT_NAME = _("group_points.bot.point_name")
POINTS_NAME = _("group_points.bot.points_name")


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

    # Can't send points to self.
    if tg_sender.id == tg_receiver.id:
        raise SelfReceiverError()

    # Can't send points to bot.
    if tg_receiver.is_bot:
        raise BotReceiverError()

    num_points = extract_points(tg_message.text, POINT_SYMBOL, POINTS_MAP)

    # If symbol count doesn't map to valid value, do nothing.
    if not num_points:
        return

    # Fetch ChatMember objects
    tg_member_sender = await context.bot.get_chat_member(tg_chat.id, tg_sender.id)

    tg_member_receiver = await context.bot.get_chat_member(tg_chat.id, tg_receiver.id)

    # Persist point transferand return sender_member and receiver_member from db.
    sender_member, receiver_member = await transfer_points(
        tg_chat,
        tg_member_sender,
        tg_member_receiver,
        num_points,
    )

    success_message = _(
        "group_points.bot.give_points {sender_name} {sender_points} {num_points} "
        + "{points_name} {receiver_name} {receiver_points}"
    ).format()

    await context.bot.send_message(
        chat_id=tg_chat.id,
        text=str(success_message),
    )


# async def on_success(update: Update, context: ContextTypes.DEFAULT_TYPE, result):
#     tg_chat = update.effective_chat
#     tg_message = update.effective_message
#     tg_sender = result["tg_sender"]
#     sender_member = result["sender_member"]
#     tg_receiver = result["tg_receiver"]
#     receiver_member = result["receiver_member"]
#     num_points = result["num_points"]

#     sender_name = user_display_name(tg_sender)
#     receiver_name = user_display_name(tg_receiver)

#     if num_points > 1:
#         bot_message = BOT_MESSAGES["give_points"].format(
#             sender_name=sender_name,
#             sender_points=sender_member.points,
#             num_points=num_points,
#             points_name=POINTS_NAME,
#             receiver_name=receiver_name,
#             receiver_points=receiver_member.points,
#         )
#         await context.bot.send_message(
#             chat_id=tg_chat.id,
#             text=str(bot_message),
#             reply_to_message_id=tg_message.message_id,
#         )
#     else:
#         bot_message = BOT_MESSAGES["give_point"].format(
#             sender_name=sender_name,
#             sender_points=sender_member.points,
#             points_name=_(POINT_NAME),
#             receiver_name=receiver_name,
#             receiver_points=receiver_member.points,
#         )
#         await context.bot.send_message(
#             chat_id=tg_chat.id,
#             text=str(bot_message),
#             reply_to_message_id=tg_message.message_id,
#         )
