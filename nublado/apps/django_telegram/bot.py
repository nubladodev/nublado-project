from telegram.ext import Application, Defaults


def create_app(
    bot_token, post_init=None, defaults: Defaults | None = None
) -> Application:

    builder = Application.builder().token(bot_token)

    if defaults is not None:
        builder = builder.defaults(defaults)

    if post_init is not None:
        builder = builder.post_init(post_init)

    return builder.build()
