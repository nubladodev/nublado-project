import logging
import asyncio

from telegram import Bot
from telegram.ext import Application

logger = logging.getLogger("django")


class BotRegistry:
    """
    Registry for multiple Application instances.

    Ensures each Application.initialize() is called exactly once,
    """

    def __init__(self):
        self._apps: dict[str, Application] = {}
        self._locks: dict[str, asyncio.Lock] = {}
        self._initialized: set[str] = set()
        self._webhook_set: set[str] = set()

    def register(self, name: str, app: Application):
        self._apps[name] = app
        self._locks[name] = asyncio.Lock()

    def get(self, name: str) -> Application:
        """
        Get bot from the regisry by name.
        """
        try:
            app = self._apps[name]
            return app
        except KeyError:
            raise ValueError(f"Bot '{name}' not found in registry.")

    def get_all(self) -> dict[str, Application]:
        return self._apps

    def in_registry(self, name: str):
        return name in self._apps

    def is_initialized(self, name: str):
        return name in self._initialized

    async def ensure_initialized(self, name: str):
        """
        Ensures each Application.initialize() is called exactly once.
        """
        # Skip if name isn't in app registry.
        if not self.in_registry(name):
            return

        # Skip if app is already initialized.
        if self.is_initialized(name):
            return

        async with self._locks[name]:
            app = self._apps[name]
            await app.initialize()
            await app.start()
            self._initialized.add(name)
            logger.info(f"Bot '{name}' initialized.")

    async def ensure_webhook(
        self,
        *,
        name: str, 
        webhook_url: str, 
        secret_token: str | None = None,
    ):
        """
        Ensure the bot is initialized and webhook is set.
        Idempotent: does nothing if already initialized or webhook is already set.
        """
        if not self.in_registry(name):
            logger.warning(f"Cannot set webhook — bot '{name}' not in registry")
            return

        # Ensure the Application is initialized.
        await self.ensure_initialized(name)

        # Skip if webhook already set.
        if name in self._webhook_set:
            logger.info(f"Webhook already set for bot '{name}', skipping")
            return

        # Set the webhook using the Bot object.
        bot_token = self._apps[name].bot.token
        bot = Bot(bot_token)

        try:
            await bot.set_webhook(
                url=webhook_url,
                secret_token=secret_token,
                drop_pending_updates=True,
            )
            self._webhook_set.add(name)
            logger.info(f"Webhook set for bot '{name}'")
        except Exception as e:
            logger.error(f"Failed to set webhook for bot '{name}': {e}")


registry = BotRegistry()
