from telegram.ext import filters

from django_telegram.registrar import HandlerRegistrar
from django_telegram.policies import GroupOnly, PrivateOnly, AdminOnly, with_policies
from django_telegram.decorators import with_language
from django_telegram.constants import HANDLER_GROUP, MIDDLEWARE_GROUP


def register_handlers(app):
    r = HandlerRegistrar(app)

    # middleware
    from django_telegram.handlers import LanguageHandler
    r.raw(LanguageHandler(), group=MIDDLEWARE_GROUP)

    # commands
    from .misc import start, hello

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

    # callbacks
    from reading_portal.handlers import open_portal_callback

    r.callback(
        open_portal_callback,
        pattern="^open_portal:",
        group=HANDLER_GROUP,
    )

    # messages
    from .group_points import give_points, POINT_FILTER

    r.message(
        POINT_FILTER,
        with_policies(GroupOnly)(with_language(give_points)),
        group=HANDLER_GROUP,
    )