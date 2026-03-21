import logging

from telegram.ext import (
    Application,
    Defaults,
)
from telegram.constants import ParseMode

from django.apps import AppConfig
from django.conf import settings

from django_telegram.bot import create_app, TelegramBot
from django_telegram.bot_registry import registry

logger = logging.getLogger("django")

BOT_NAME = settings.NUBLADO_BOT
BOT_TOKEN = settings.NUBLADO_BOT_TOKEN


async def post_init(application: Application):
    logger.info(f"Bot {BOT_NAME} is running.")


class NubladoBotConfig(AppConfig):
    name = "nublado_bot"

    def ready(self):
        from django_telegram.services.language import resolve_chat_language

        from .handlers.register_handlers import register_handlers

        defaults = Defaults(
            parse_mode=ParseMode.HTML,
        )

        app = create_app(BOT_TOKEN, post_init=post_init, defaults=defaults)
        app.bot_data["language_resolver"] = resolve_chat_language

        register_handlers(app)

        bot = TelegramBot(
            name=BOT_NAME,
            application=app,
            webhook_url=settings.NUBLADO_BOT_WEBHOOK_URL,
            webhook_token=settings.NUBLADO_BOT_WEBHOOK_SECRET,
        )
        registry.register(BOT_NAME, bot)
