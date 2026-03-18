import logging

from telegram.ext import (
    Application,
    CommandHandler,
    Defaults,
    MessageHandler,
    CallbackQueryHandler,
    filters
)
from telegram.constants import ParseMode

from django.apps import AppConfig
from django.conf import settings

from django_telegram.bot import create_app
from django_telegram.bot_registry import registry
from django_telegram.policies import (
    GroupOnly,
    PrivateOnly,
    AdminOnly,
    GroupOwnerOnly,
    with_policies,
)

logger = logging.getLogger("django")

BOT_NAME = settings.NUBLADO_BOT
BOT_TOKEN = settings.NUBLADO_BOT_TOKEN


async def post_init(application: Application):
    logger.info(f"Bot {BOT_NAME} is running.")


class NubladoBotConfig(AppConfig):
    name = "nublado_bot"

    def ready(self):
        from django_telegram.services.language import resolve_chat_language
        from django_telegram.handlers import LanguageHandler
        from django_telegram.constants import MIDDLEWARE_GROUP, HANDLER_GROUP
        from reading_portal.handlers import (
            open_portal,
            open_portal_callback,
            close_portal,
            list_draft_portals,
            handle_voice_submission,
            pending_readings,
            review_reading,
        )
        from .handlers.group_points import give_points, POINT_FILTER
        from .handlers.misc import start, hello
        from .handlers.group_settings import set_bot_language

        defaults = Defaults(
            parse_mode=ParseMode.HTML,
        )

        app = create_app(BOT_TOKEN, post_init=post_init, defaults=defaults)
        app.bot_data["language_resolver"] = resolve_chat_language
        registry.register(BOT_NAME, app)

        # Middleware
        app.add_handler(LanguageHandler(), group=MIDDLEWARE_GROUP)

        # Command handlers.
        app.add_handler(
            CommandHandler(
                "start",
                with_policies(PrivateOnly)(start),
            ),
            group=HANDLER_GROUP,
        )
        app.add_handler(
            CommandHandler(
                "hello",
                with_policies(GroupOnly)(hello),
            ),
            group=HANDLER_GROUP,
        )
        app.add_handler(
            CommandHandler(
                "set_bot_language",
                with_policies(GroupOnly, AdminOnly)(set_bot_language),
            ),
            group=HANDLER_GROUP,
        )
        app.add_handler(
            CommandHandler(
                "show_portals",
                with_policies(GroupOnly)(list_draft_portals),
            ),
            group=HANDLER_GROUP,
        )
        app.add_handler(
            CallbackQueryHandler(
                open_portal_callback,
                pattern="^open_portal:",
            ),
            group=HANDLER_GROUP
        )
        app.add_handler(
            CommandHandler(
                "open_portal",
                with_policies(GroupOnly)(open_portal),
            ),
            group=HANDLER_GROUP,
        )
        app.add_handler(
            CommandHandler(
                "close_portal",
                with_policies(GroupOnly, GroupOwnerOnly)(close_portal),
            ),
            group=HANDLER_GROUP,
        )
        app.add_handler(
            CommandHandler(
                "reviewed",
                with_policies(GroupOnly)(review_reading),
            ),
            group=HANDLER_GROUP,
        )
        app.add_handler(
            CommandHandler(
                "pending_readings",
                with_policies(GroupOnly)(pending_readings),
            ),
            group=HANDLER_GROUP,
        )
        app.add_handler(
            MessageHandler(
                filters.VOICE & filters.REPLY,
                handle_voice_submission  
            ),
            group=HANDLER_GROUP,
        )

        # Message handlers.
        app.add_handler(
            MessageHandler(
                POINT_FILTER,
                with_policies(GroupOnly)(give_points),
            ),
            group=HANDLER_GROUP,
        )
