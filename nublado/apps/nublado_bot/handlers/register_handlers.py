from telegram.ext import CommandHandler, MessageHandler, CallbackQueryHandler, filters

from django_telegram.policies import (
    GroupOnly,
    PrivateOnly,
    AdminOnly,
    GroupOwnerOnly,
    with_policies,
)
from django_telegram.decorators import with_language
from django_telegram.constants import HANDLER_GROUP, MIDDLEWARE_GROUP


def register_handlers(app):
    from django_telegram.handlers import LanguageHandler
    from reading_portal.handlers import (
        pending_readings,
        list_draft_portals,
        open_portal,
        close_portal,
        submit_reading,
        review_reading,
        open_portal_callback,
    )
    from .group_settings import set_bot_language
    from .group_points import give_points, POINT_FILTER
    from .misc import start, hello

    # middleware
    app.add_handler(LanguageHandler(), group=MIDDLEWARE_GROUP)

    # commands
    app.add_handler(
        CommandHandler(
            "start", 
            with_policies(PrivateOnly())(with_language(start)),
        ),
        group=HANDLER_GROUP
    )

    app.add_handler(
        CommandHandler(
            "hello", 
            with_policies(GroupOnly())(with_language(hello)),
        ),
        group=HANDLER_GROUP
    )

    app.add_handler(
        CommandHandler(
            "set_bot_language", 
            with_policies(GroupOnly())(with_language(set_bot_language)),
        ),
        group=HANDLER_GROUP
    )

    app.add_handler(
        CommandHandler(
            "open_portal", 
            with_policies(GroupOnly())(with_language(open_portal)),
        ),
        group=HANDLER_GROUP
    )

    app.add_handler(
        CommandHandler(
            "close_portal", 
            with_policies(GroupOnly())(with_language(close_portal)),
        ),
        group=HANDLER_GROUP
    )

    app.add_handler(
        CommandHandler(
            "pending_readings", 
            with_policies(GroupOnly())(with_language(pending_readings)),
        ),
        group=HANDLER_GROUP
    )

    app.add_handler(
        CommandHandler(
            "show_portals", 
            with_policies(GroupOnly())(with_language(show_portals)),
        ),
        group=HANDLER_GROUP
    )

    app.add_handler(
        CommandHandler(
            "reviewed", 
            with_policies(GroupOnly())(with_language(review_reading)),
        ),
        group=HANDLER_GROUP
    )

    app.add_handler(
        CallbackQueryHandler(open_portal_callback, pattern="^open_portal:"),
        group=HANDLER_GROUP,
    )

    app.add_handler(
        MessageHandler(
            filters.VOICE & filters.REPLY,
            with_policies(GroupOnly())(with_language(submit_reading)),
        ),
        group=HANDLER_GROUP
    )

    app.add_handler(
        MessageHandler(
            POINT_FILTER,
            with_policies(GroupOnly())(with_language(give_points)),
        ),
        group=HANDLER_GROUP
    )
