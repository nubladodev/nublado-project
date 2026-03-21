import asyncio
import logging

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
        # Initialize all bots in the registry
        for bot_id in settings.BOTS:
            if registry.in_registry(bot_id):
                logger.info(f"Initializing bot '{bot_id}'...")
                await registry.ensure_initialized(bot_id)
                logger.info(f"Bot '{bot_id}' is ready.")
            else:
                logger.warning(f"Bot '{bot_id}' not registered in registry!")

        # Keep the JobQueues running indefinitely
        logger.info("All bots initialized.")
        await asyncio.Event().wait()