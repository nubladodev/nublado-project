import asyncio
import logging

from telegram import Bot

from django.core.management.base import BaseCommand
from django.conf import settings
from django_telegram.bot_registry import registry

logger = logging.getLogger("django")


class Command(BaseCommand):
    help = "Initialize all registered bots (webhook mode) and start their JobQueues"

    def handle(self, *args, **kwargs):
        logger.info("Starting webhook bots...")
        asyncio.run(self.start_bots())

    async def start_bots(self):

        for bot_name, (bot_token, webhook_url, webhook_token) in settings.BOTS.items():
            # Initialize bot Application + JobQueue
            if registry.in_registry(bot_name):
                logger.info(f"Initializing bot '{bot_name}'...")
                await registry.ensure_initialized(bot_name)
                # Set webhook AFTER app is ready
                bot = Bot(bot_token)
                await bot.set_webhook(
                    url=webhook_url,
                    # secret_token=webhook_token,
                    drop_pending_updates=True  # or False if you prefer
                )
                logger.info(f"Bot '{bot_name}' is ready.")
            else:
                logger.warning(f"Bot '{bot_name}' not registered in registry!")

            self.stdout.write(self.style.SUCCESS(f"{bot_name} webhook set and bot started"))

        # Keep the JobQueues running indefinitely
        logger.info("All bots initialized.")
        await asyncio.Event().wait()
