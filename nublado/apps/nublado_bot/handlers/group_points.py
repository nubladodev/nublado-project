from telegram import Update
from telegram.ext import ContextTypes

from django.utils.translation import gettext_lazy as _

from django_telegram.utils.formatting import user_display_name
from group_points.handlers import make_give_points_handler
from group_points.constants import PointTransferError

from ..bot_messages import BOT_MESSAGES

# Bot-specific configuration
POINT_SYMBOL = "+"

# Read: 2 symbols for 1 point, 3 symbols for 2 points, 4 symbols for 4 points.
POINTS_MAP = {
    2: 1,
    3: 2,
    4: 4,
}

# Translation keys or message templates
POINT_NAME = "bot.nublado.point_name"
POINTS_NAME = "bot.nublado.points_name"


async def on_success(update: Update, context: ContextTypes.DEFAULT_TYPE, result):
    tg_chat = update.effective_chat
    tg_message = update.effective_message
    tg_sender = result["tg_sender"]
    sender_member = result["sender_member"]
    tg_receiver = result["tg_receiver"]
    receiver_member = result["receiver_member"]
    num_points = result["num_points"]

    sender_name = user_display_name(tg_sender)
    receiver_name = user_display_name(tg_receiver)

    if num_points > 1:
        bot_message = BOT_MESSAGES["give_points"].format(
            sender_name=sender_name,
            sender_points=sender_member.points,
            num_points=num_points,
            points_name=_(POINTS_NAME),
            receiver_name=receiver_name,
            receiver_points=receiver_member.points_map,
        )
        await context.bot.send_message(
            chat_id=tg_chat.id,
            text=str(bot_message),
            reply_to_message_id=tg_message.message_id,
        )
    else:
        bot_message = BOT_MESSAGES["give_point"].format(
            sender_name=sender_name,
            sender_points=sender_member.points,
            points_name=_(POINT_NAME),
            receiver_name=receiver_name,
            receiver_points=receiver_member.points,
        )
        await context.bot.send_message(
            chat_id=tg_chat.id,
            text=str(bot_message),
            reply_to_message_id=tg_message.message_id,
        )


async def on_error(update, context, error):
    tg_chat = update.effective_chat
    tg_message = update.effective_message

    if error == PointTransferError.SELF:
        bot_message = BOT_MESSAGES["no_give_self"].format(points_name=_(POINTS_NAME))
        await context.bot.send_message(
            chat_id=tg_chat.id,
            text=str(bot_message),
            reply_to_message_id=tg_message.message_id,
        )
    elif error == PointTransferError.BOT:
        bot_message = BOT_MESSAGES["no_give_bot"].format(points_name=_(POINTS_NAME))
        await context.bot.send_message(
            chat_id=tg_chat.id,
            text=str(bot_message),
            reply_to_message_id=tg_message.message_id,
        )


POINT_FILTER, give_points = make_give_points_handler(
    point_symbol=POINT_SYMBOL,
    points_map=POINTS_MAP,
    on_success=on_success,
    on_error=on_error,
)
