import asyncio
import logging

from django.core.management.base import BaseCommand
from django.conf import settings

from django_telegram.bot_registry import registry

logger = logging.getLogger("django")


# class Command(BaseCommand):
#     help = "Initialize bots and webhooks."

#     def handle(self, *args, **kwargs):
#         logger.info("Starting webhook bots (pre-set only)...")
#         asyncio.run(self.run())

#     async def run(self):
#         for bot_name, (bot_token, webhook_url, webhook_token) in settings.BOTS.items():
#             if registry.in_registry(bot_name):
#                 await registry.ensure_webhook(
#                     name=bot_name,
#                     webhook_url=webhook_url,
#                     secret_token=webhook_token,
#                 )
#                 logger.info(f"Bot '{bot_name}' webhook ensured")
#             else:
#                 logger.warning(f"Bot '{bot_name}' not registered")
#         logger.info("All webhooks ensured. Exiting start_bots.")


class Command(BaseCommand):
    def handle(self, *args, **kwargs):
        asyncio.run(self.run())

    async def run(self):
        for bot in registry.all():
            await bot.ensure_webhook()