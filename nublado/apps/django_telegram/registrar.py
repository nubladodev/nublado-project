class HandlerRegistrar:
    def __init__(self, app):
        self.app = app

    def command(self, name, handler, *, group=0):
        from telegram.ext import CommandHandler

        self.app.add_handler(CommandHandler(name, handler), group=group)

    def message(self, filters, handler, *, group=0):
        from telegram.ext import MessageHandler

        self.app.add_handler(MessageHandler(filters, handler), group=group)

    def callback(self, handler, *, pattern=None, group=0):
        from telegram.ext import CallbackQueryHandler

        self.app.add_handler(
            CallbackQueryHandler(handler, pattern=pattern),
            group=group,
        )

    def raw(self, handler, *, group=0):
        self.app.add_handler(handler, group=group)
