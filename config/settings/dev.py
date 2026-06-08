from .base import *

DEBUG = True

INSTALLED_APPS += [
    "debug_toolbar",
]

MIDDLEWARE += [
    "debug_toolbar.middleware.DebugToolbarMiddleware",
]

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql_psycopg2",
        "NAME": os.environ["DATABASE_NAME"],
        "USER": os.environ["DATABASE_USER"],
        "PASSWORD": os.environ["DATABASE_PWD"],
        "HOST": "localhost",
        "PORT": "",
    }
}

EMAIL_HOST = "localhost"
EMAIL_PORT = 1025
EMAIL_HOST_USER = None
EMAIL_HOST_PASSWORD = None
EMAIL_BACKEND = "django.core.mail.backends.filebased.EmailBackend"
EMAIL_FILE_PATH = "~/tmp/email-messages/"

DJANGO_NUBLADO_TELEGRAM_BOT["BOT_MODE"] = "polling"
