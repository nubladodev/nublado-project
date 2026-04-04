import re

from django.utils.translation import gettext_lazy as _

POINT_SYMBOL = re.escape("+")

POINT_NAME = _("group_points.bot.point_name")
POINTS_NAME = _("group_points.bot.points_name")

POINTS_MAP = {
    2: 1,
    3: 2,
    4: 4,
}
