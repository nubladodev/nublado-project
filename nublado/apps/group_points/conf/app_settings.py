import re
from dataclasses import dataclass


from django_nublado_core.conf.base import AppSettings


# The app's settings dict name
SETTINGS_DICT_NAME = "GROUP_POINTS"


# The app settings default values.
SETTINGS_DEFAULTS = {
    "POINT_SYMBOL": re.escape("+"),
    "POINTS_MAP": {
        2: 1,
        3: 2,
        4: 4,
    },
}


@dataclass(frozen=True)
class AppData:
    POINT_SYMBOL: str
    POINTS_MAP: dict


app_settings = AppSettings(
    defaults=SETTINGS_DEFAULTS,
    settings_dict_name=SETTINGS_DICT_NAME,
    cls=AppData,
)