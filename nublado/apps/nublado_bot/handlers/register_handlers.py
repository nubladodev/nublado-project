from telegram.ext import CommandHandler, MessageHandler, CallbackQueryHandler, filters

from django_telegram.policies import (
    GroupOnly,
    GroupOwnerOnly,
    PrivateOnly,
    with_policies,
)
from django_telegram.decorators import with_language
from django_telegram.constants import HANDLER_GROUP, MIDDLEWARE_GROUP


def register_handlers(app):
    from django_telegram.handlers import LanguageHandler
    from reading_portal.handlers import (
        list_draft_portals,
        pending_readings,
        open_portal,
        close_portal,
        submit_reading,
        review_reading,
        open_portal_callback,
    )
    from group_points.handlers import give_points, POINT_FILTER
    from .group_settings import set_bot_language
    from .misc import start, hello
    from .admin import list_groups, broadcast_message
    from .error_handler import error_handler

    # middleware
    app.add_handler(LanguageHandler(), group=MIDDLEWARE_GROUP)

    # error handler
    app.add_error_handler(with_language(error_handler))

    # commands
    app.add_handler(
        CommandHandler(
            "groups",
            with_language(list_groups),
        ),
        group=HANDLER_GROUP,
    )

    app.add_handler(
        CommandHandler(
            "broadcast",
            with_language(broadcast_message),
        ),
        group=HANDLER_GROUP,
    )

    app.add_handler(
        CommandHandler(
            "start",
            with_policies(PrivateOnly)(with_language(start)),
        ),
        group=HANDLER_GROUP,
    )

    app.add_handler(
        CommandHandler(
            "hello",
            with_policies(GroupOnly)(with_language(hello)),
        ),
        group=HANDLER_GROUP,
    )

    app.add_handler(
        CommandHandler(
            "set_bot_language",
            with_policies(GroupOnly)(with_language(set_bot_language)),
        ),
        group=HANDLER_GROUP,
    )

    app.add_handler(
        CommandHandler(
            "open_portal",
            with_policies(GroupOnly)(with_language(open_portal)),
        ),
        group=HANDLER_GROUP,
    )

    app.add_handler(
        CommandHandler(
            "close_portal",
            with_policies(GroupOnly)(with_language(close_portal)),
        ),
        group=HANDLER_GROUP,
    )

    app.add_handler(
        CommandHandler(
            "pending_readings",
            with_policies(GroupOnly)(with_language(pending_readings)),
        ),
        group=HANDLER_GROUP,
    )

    app.add_handler(
        CommandHandler(
            "show_portals",
            with_policies(GroupOnly)(with_language(list_draft_portals)),
        ),
        group=HANDLER_GROUP,
    )

    app.add_handler(
        CommandHandler(
            "reviewed",
            with_policies(GroupOnly)(with_language(review_reading)),
        ),
        group=HANDLER_GROUP,
    )

    app.add_handler(
        CallbackQueryHandler(open_portal_callback, pattern="^open_portal:"),
        group=HANDLER_GROUP,
    )

    app.add_handler(
        MessageHandler(
            filters.VOICE & filters.REPLY,
            with_policies(GroupOnly)(with_language(submit_reading)),
        ),
        group=HANDLER_GROUP,
    )

    app.add_handler(
        MessageHandler(
            POINT_FILTER,
            with_policies(GroupOnly)(with_language(give_points)),
        ),
        group=HANDLER_GROUP,
    )
