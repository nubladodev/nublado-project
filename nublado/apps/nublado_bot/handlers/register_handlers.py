from telegram.ext import CommandHandler, MessageHandler, CallbackQueryHandler, filters

from django_nublado_telegram.policies import (
    GroupOnly,
    PrivateOnly,
    GroupOwnerOnly,
    with_policies,
)
from django_nublado_telegram.decorators import with_language
from django_nublado_telegram.constants import HANDLER_GROUP, MIDDLEWARE_GROUP

from ..policies import BotOwnerOnly


def register_handlers(app):
    # import modules that use models here to avoid "app not ready" errors.
    from django_nublado_telegram.handlers import LanguageHandler
    from reading_portal.handlers import (
        show_ready_portals,
        handle_open_portal,
        handle_close_portal,
        show_pending_readings,
        show_reading_submissions,
        handle_submit_reading,
        handle_review_reading,
        open_portal_callback,
        handle_edit_reading,
    )
    from group_points.handlers import give_points, POINT_FILTER
    from chat_notes.handlers import (
        save_repo_item,
        get_repo_item,
        list_repo_items,
        HASHTAG_FILTER,
    )
    from .group_settings import set_bot_language
    from .misc import start, hello, unix_timestamp
    from .admin import list_groups, broadcast_message, register_chat
    from .error_handler import error_handler

    # middleware
    app.add_handler(LanguageHandler(), group=MIDDLEWARE_GROUP)

    # error handler
    app.add_error_handler(with_language(error_handler))

    # admin
    app.add_handler(
        CommandHandler(
            "groups",
            with_policies(BotOwnerOnly)(with_language(list_groups)),
        ),
        group=HANDLER_GROUP,
    )

    app.add_handler(
        CommandHandler(
            "broadcast",
            with_policies(BotOwnerOnly)(with_language(broadcast_message)),
        ),
        group=HANDLER_GROUP,
    )

    app.add_handler(
        CommandHandler(
            "register_chat",
            with_policies(BotOwnerOnly)(with_language(register_chat)),
        ),
        group=HANDLER_GROUP,
    )

    # misc
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
            "unix_timestamp",
            with_policies(GroupOnly)(with_language(unix_timestamp)),
        ),
        group=HANDLER_GROUP,
    )

    # group_settings
    app.add_handler(
        CommandHandler(
            "set_bot_language",
            with_policies(GroupOnly)(with_language(set_bot_language)),
        ),
        group=HANDLER_GROUP,
    )

    # reading_portal
    app.add_handler(
        CommandHandler(
            "open_portal",
            with_policies(GroupOnly)(with_language(handle_open_portal)),
        ),
        group=HANDLER_GROUP,
    )

    app.add_handler(
        CommandHandler(
            "close_portal",
            with_policies(GroupOnly)(with_language(handle_close_portal)),
        ),
        group=HANDLER_GROUP,
    )

    app.add_handler(
        CommandHandler(
            "readings",
            with_policies(GroupOnly)(with_language(show_reading_submissions)),
        ),
        group=HANDLER_GROUP,
    )

    app.add_handler(
        CommandHandler(
            "pending_readings",
            with_policies(GroupOnly)(with_language(show_pending_readings)),
        ),
        group=HANDLER_GROUP,
    )

    app.add_handler(
        CommandHandler(
            "show_portals",
            with_policies(GroupOnly)(with_language(show_ready_portals)),
        ),
        group=HANDLER_GROUP,
    )

    app.add_handler(
        CommandHandler(
            "reviewed",
            with_policies(GroupOnly)(with_language(handle_review_reading)),
        ),
        group=HANDLER_GROUP,
    )

    app.add_handler(
        CommandHandler(
            "edit_reading",
            with_policies(GroupOwnerOnly)(with_language(handle_edit_reading)),
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
            with_policies(GroupOnly)(with_language(handle_submit_reading)),
        ),
        group=HANDLER_GROUP,
    )

    # group_points
    app.add_handler(
        MessageHandler(
            POINT_FILTER,
            with_policies(GroupOnly)(with_language(give_points)),
        ),
        group=HANDLER_GROUP,
    )

    # chat_notes
    app.add_handler(
        CommandHandler(
            "save_note",
            with_policies(GroupOnly)(with_language(save_repo_item)),
        ),
        group=HANDLER_GROUP,
    )

    app.add_handler(
        CommandHandler(
            "notes",
            with_policies(GroupOnly)(with_language(list_repo_items)),
        ),
        group=HANDLER_GROUP,
    )

    app.add_handler(
        MessageHandler(
            HASHTAG_FILTER,
            with_policies(GroupOnly)(with_language(get_repo_item)),
        ),
        group=HANDLER_GROUP,
    )