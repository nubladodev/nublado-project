from django.utils.translation import gettext_lazy as _

BOT_MESSAGES = {
    "error.no_give_points_bot": _(
        "group_points.bot.error.no_give_points_bot {points_name}"
    ),
    "error.no_take_points_bot": _(
        "group_points.bot.error.no_take_points_bot {points_name}"
    ),
    "error.no_give_points_self": _(
        "group_points.bot.error.no_give_points_self {points_name}"
    ),
    "error.no_take_points_self": _(
        "group_points.bot.error.no_take_points_self {points_name}"
    ),
    "give_point": _(
        "group_points.bot.give_point {sender_name} {sender_points} "
        + "{points_name} {receiver_name} {receiver_points}"
    ),
    "give_points": _(
        "group_points.bot.give_points {sender_name} {sender_points} {num_points} "
        + "{points_name} {receiver_name} {receiver_points}"
    ),
    "take_point": _(
        "group_points.bot.take_point {sender_name} {sender_points} "
        + "{points_name} {receiver_name} {receiver_points}"
    ),
    "take_points": _(
        "group_points.bot.take_points {sender_name} {sender_points} {num_points} "
        + "{points_name} {receiver_name} {receiver_points}"
    ),
}
