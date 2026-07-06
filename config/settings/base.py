import os
import sys
from pathlib import Path

from django.utils.translation import gettext_noop as _


# Get key env values from the virtual environment.
def get_env_variable(var_name):
    try:
        return os.environ[var_name]
    except KeyError:
        error_msg = "Set the {} environment variable.".format(var_name)
        raise Exception(error_msg)


# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent.parent

# Custom directory for apps
APP_DIR = "nublado/apps"
sys.path.append(os.path.join(BASE_DIR, APP_DIR))

APPS_ROOT = BASE_DIR / APP_DIR

PROJECT_NAME = "Nublado Project"

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = get_env_variable("DJANGO_SECRET_KEY")

ALLOWED_HOSTS = []

# Installed apps
INSTALLED_APPS = [
    "jazzmin",
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django_nublado_core",
    "users.apps.UserConfig",
    "django_nublado_telegram",
    "reading_portal.apps.ReadingPortalConfig",
    "group_points.apps.GroupPointsConfig",
    "chat_notes.apps.ChatNotesConfig",
    "nublado_bot.apps.NubladoBotConfig",
    "project_app.apps.ProjectAppConfig",
    "import_export",
]

AUTH_USER_MODEL = "users.User"

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "django.middleware.locale.LocaleMiddleware",
]

ROOT_URLCONF = "config.urls"

WSGI_APPLICATION = "config.wsgi.application"
ASGI_APPLICATION = "config.asgi.application"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
                "project_app.context_processors.global_settings",
            ],
        },
    },
]

# Password validation
AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]

# Internationalization and localization
EN = "en"
ES = "es"
LANGUAGE_CODE = EN
LANGUAGES = [
    (EN, _("common.language.en")),
    (ES, _("common.language.es")),
]

# Variations of LANGUAGES in different data types.
LANGUAGES_DICT = dict(LANGUAGES)

LOCALE_PATHS = (APPS_ROOT / "project_app" / "locale",)

TIME_ZONE = "UTC"
USE_I18N = True
USE_L10N = True
USE_TZ = True

STATIC_URL = "/static/"
STATIC_ROOT = BASE_DIR / APP_DIR / "staticfiles"

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# Logging
LOGGING = {
    "version": 1,
    # Version of logging
    "disable_existing_loggers": False,
    "formatters": {
        "verbose": {
            "format": "{levelname} {asctime} {module} {process:d} {thread:d} {message}",
            "style": "{",
        },
        "simple": {
            "format": "{levelname} {message}",
            "style": "{",
        },
    },
    "filters": {
        "require_debug_true": {
            "()": "django.utils.log.RequireDebugTrue",
        },
    },
    # Handlers
    "handlers": {
        "file": {
            "level": "DEBUG",
            "class": "logging.FileHandler",
            "filename": "nublado-debug.log",
        },
        "console": {
            "level": "INFO",
            "class": "logging.StreamHandler",
            "formatter": "simple",
        },
    },
    # Loggers
    "loggers": {
        "django": {
            "level": "INFO",
            "handlers": ["console"],
            "propagate": True,
        },
    },
}

# django-nublado-telegram settings
DJANGO_NUBLADO_TELEGRAM_BOT = {
    "BOT_MODE": "polling",
}

NUBLADO_BOT = {
    "NAME": "nublado",
    "TOKEN": get_env_variable("NUBLADO_BOT_TOKEN"),
    "BOT_OWNER_ID": 8009983006,
    "WEBHOOK_URL": "https://nublado-project.onrender.com/bot/nublado/webhook/",
    "WEBHOOK_SECRET": "supersecretnubladowebhooktoken",
    "REPO_ID": get_env_variable("NUBLADO_REPO_ID")
}

GROUP_POINTS = {
    "POINTS_NAME": _("group_points.bot.points_name"),
    "POINT_SYMBOL": "+",
    "SYMBOL_COUNT_TO_POINTS": {
        2: 1,
        3: 2,
        4: 4,
    },
}

# Third-party settings
JAZZMIN_SETTINGS = {
    "site_title": "Nublado Admin",
    "site_header": "Nublado",
    "site_brand": "Nublado",
    "site_logo": "images/nublado-logo.png",
    "site_logo_classes": "img-circle",
    "site_icon": None,
    "welcome_sign": "Welcome to Nublado",
    "copyright": "Nublado",
    "usermenu_links": [
        {"model": "auth.user"},
    ],
    "custom_css": "css/jazmin_admin_override.css",
}
