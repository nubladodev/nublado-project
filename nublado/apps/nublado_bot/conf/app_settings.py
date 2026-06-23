from dataclasses import dataclass

from django.conf import settings

from django_nublado_core.conf.base import AppSettings


# The app's settings dict name
SETTINGS_DICT_NAME = "NUBLADO_BOT"

# The app settings default values.
SETTINGS_DEFAULTS = {
    "NAME": "",
    "TOKEN": "",
    "BOT_OWNER_ID": 0,
    "WEBHOOK_URL": "",
    "WEBHOOK_SECRET": "",
    "REPO_ID": "",
}


@dataclass(frozen=True)
class AppData:
    NAME: str
    TOKEN: str
    BOT_OWNER_ID: int
    WEBHOOK_URL: str
    WEBHOOK_SECRET: str
    REPO_ID: int


app_settings = AppSettings(
    defaults=SETTINGS_DEFAULTS,
    settings_dict_name=SETTINGS_DICT_NAME,
    cls=AppData,
)