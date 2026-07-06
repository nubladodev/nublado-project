from dataclasses import dataclass

from django.utils.translation import gettext_lazy as _

from django_nublado_core.conf.base import AppSettings


# The app's settings dict name
SETTINGS_DICT_NAME = "GROUP_POINTS"

# The app settings default values.
SETTINGS_DEFAULTS = {
    "POINT_NAME": _("point"),
    "POINTS_NAME": _("points"),
    "POINT_SYMBOL": "+",
    "SYMBOL_COUNT_TO_POINTS": {
        2: 1,
        3: 2,
        4: 4,
    },
}


@dataclass(frozen=True)
class AppData:
    POINT_NAME: str
    POINTS_NAME: str
    POINT_SYMBOL: str
    SYMBOL_COUNT_TO_POINTS: dict


app_settings = AppSettings(
    defaults=SETTINGS_DEFAULTS,
    settings_dict_name=SETTINGS_DICT_NAME,
    cls=AppData,
)