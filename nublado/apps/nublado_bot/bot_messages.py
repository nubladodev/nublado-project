from django.utils.translation import gettext_lazy as _

BOT_MESSAGES = {
    "start": _("nublado.bot.start"),
    "hello": _("nublado.bot.hello"),
    # Group settings
    "language_set": _("nublado.bot.language_set {language}"),
    "error.language_active": _("nublado.bot.error.language_active {language}"),
    "error.invalid_language": _("nublado.bot.error.invalid_language: {language_keys}"),
    # Group points
    "error.no_give_points_bot": _("nublado.bot.error.no_give_points_bot {points_name}"),
    "error.no_take_points_bot": _("nublado.bot.error.no_take_points_bot {points_name}"),
    "error.no_give_points_self": _(
        "nublado.bot.error.no_give_points_self {points_name}"
    ),
    "error.no_take_points_self": _(
        "nublado.bot.error.no_take_points_self {points_name}"
    ),
    "give_point": _(
        "nublado.bot.give_point {sender_name} {sender_points} "
        + "{points_name} {receiver_name} {receiver_points}"
    ),
    "give_points": _(
        "nublado.bot.give_points {sender_name} {sender_points} {num_points} "
        + "{points_name} {receiver_name} {receiver_points}"
    ),
    "take_point": _(
        "nublado.bot.take_point {sender_name} {sender_points} "
        + "{points_name} {receiver_name} {receiver_points}"
    ),
    "take_points": _(
        "nublado.bot.take_points {sender_name} {sender_points} {num_points} "
        + "{points_name} {receiver_name} {receiver_points}"
    ),
}
