from django.utils.translation import gettext_lazy as _

# Translators: Message when giving exactly 1 point to a group member.
# {sender_name}, {receiver_name} = usernames.
# {sender_points}, {receiver_points} = updated point totals for sender and receiver.
# {points_name} = singular form of the points name (e.g., point, karma point, raindrop).
# Example: @foo (10) has given a karma point to @fee (5).
GIVE_POINT = _("group_points.bot.give_point {sender_name} {sender_points} "
    "{points_name} {receiver_name} {receiver_points}")

# Translators: Message when giving more than 1 point to a group member.
# {sender_name}, {receiver_name} = usernames.
# {sender_points}, {receiver_points} = updated point totals for sender and receiver.
# {num_points} = number of points given.
# {points_name} = plural form of the points name (e.g., points, karma points, raindrops).
# Example: @foo (10) has given 3 karma points to @fee (5).
GIVE_POINTS = _("group_points.bot.give_points {sender_name} {sender_points} {num_points} "
    "{points_name} {receiver_name} {receiver_points}")

# Translators: Message when taking exactly 1 point from a group member.
# {sender_name}, {receiver_name} = usernames.
# {sender_points}, {receiver_points} = updated point totals for sender and receiver.
# {points_name} = singular form of the points name (e.g., point, karma point, raindrop).
# Example: @foo (10) has taken a karma point from @fee (5).
TAKE_POINT = _("group_points.bot.take_point {sender_name} {sender_points} "
    "{points_name} {receiver_name} {receiver_points}")

# Translators: Message when taking more than 1 point from a group member.
# {sender_name}, {receiver_name} = usernames.
# {sender_points}, {receiver_points} = updated point totals for sender and receiver.
# {num_points} = number of points taken.
# {points_name} = singular form of the points name (e.g., point, karma point, raindrop).
# Example: @foo (10) has taken a karma point from @fee (5).
TAKE_POINTS = _("group_points.bot.take_points {sender_name} {sender_points} {num_points} "
    "{points_name} {receiver_name} {receiver_points}")

# Translators: Message when attempting to give points to a bot.
# {points_name} = plural form of the points name (e.g., points, karma points, raindrops).
# Example: You can't give karma points to a bot.
ERROR_NO_GIVE_POINTS_BOT = _("group_points.bot.error.no_give_points_bot {points_name}")

# Translators: Message when attempting to take points from a bot.
# {points_name} = plural form of the points name (e.g., points, karma points, raindrops).
# Example: You can't take karma points from a bot.
ERROR_NO_TAKE_POINTS_BOT = _("group_points.bot.error.no_take_points_bot {points_name}")

# Translators: Message when attempting to give points to self.
# {points_name} = plural form of the points name (e.g., points, karma points, raindrops).
# Example: You can't give karma points to yourself.
ERROR_NO_GIVE_POINTS_SELF = _("group_points.bot.error.no_give_points_self {points_name}")

# Translators: Message when attempting to take points from self.
# {points_name} = plural form of the points name (e.g., points, karma points, raindrops).
# Example: You can't take karma points from yourself.
ERROR_NO_TAKE_POINTS_SELF = _("group_points.bot.error.no_take_points_self {points_name}")

BOT_MESSAGES = {
    "error.no_give_points_bot": ERROR_NO_GIVE_POINTS_BOT,
    "error.no_take_points_bot": ERROR_NO_TAKE_POINTS_BOT,
    "error.no_give_points_self": ERROR_NO_GIVE_POINTS_SELF,
    "error.no_take_points_self": ERROR_NO_TAKE_POINTS_SELF,
    "give_point": GIVE_POINT,
    "give_points": GIVE_POINTS,
    "take_point": TAKE_POINT,
    "take_points": TAKE_POINTS,
}
