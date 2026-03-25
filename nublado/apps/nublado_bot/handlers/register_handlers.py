from telegram.ext import filters

from django_telegram.registrar import HandlerRegistrar
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
    r = HandlerRegistrar(app)

    from django_telegram.handlers import LanguageHandler
    from reading_portal.handlers import (
        pending_readings,
        list_draft_portals,
        open_portal,
        close_portal,
        review_reading,
        open_portal_callback,
        handle_voice_submission,
    )
    from .group_settings import set_bot_language
    from .group_points import give_points, POINT_FILTER
    from .misc import start, hello

    # middleware
    r.raw(LanguageHandler(), group=MIDDLEWARE_GROUP)

    # commands
    r.command(
        "start",
        with_policies(PrivateOnly)(with_language(start)),
        group=HANDLER_GROUP,
    )

    r.command(
        "hello",
        with_policies(GroupOnly)(with_language(hello)),
        group=HANDLER_GROUP,
    )

    r.command(
        "set_bot_language",
        with_policies(GroupOnly, AdminOnly)(with_language(set_bot_language)),
        group=HANDLER_GROUP,
    )

    r.command(
        "open_portal",
        with_policies(GroupOnly)(
            with_language(open_portal),
        ),
        group=HANDLER_GROUP,
    )

    r.command(
        "close_portal",
        with_policies(GroupOnly, GroupOwnerOnly)(
            with_language(close_portal),
        ),
        group=HANDLER_GROUP,
    )

    r.command(
        "pending_readings",
        with_policies(GroupOnly)(
            with_language(pending_readings),
        ),
        group=HANDLER_GROUP,
    )

    r.command(
        "show_portals",
        with_policies(GroupOnly)(
            with_language(list_draft_portals),
        ),
        group=HANDLER_GROUP,
    )

    r.command(
        "reviewed",
        with_policies(GroupOnly)(
            with_language(review_reading),
        ),
        group=HANDLER_GROUP,
    )

    r.callback(
        open_portal_callback,
        pattern="^open_portal:",
        group=HANDLER_GROUP,
    )

    r.message(
        filters.VOICE & filters.REPLY, handle_voice_submission, group=HANDLER_GROUP
    )

    r.message(
        POINT_FILTER,
        with_policies(GroupOnly)(with_language(give_points)),
        group=HANDLER_GROUP,
    )
