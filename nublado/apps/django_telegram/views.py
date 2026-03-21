import json
import logging

from telegram import Update

from django.http import Http404, JsonResponse
from django.views import View
from django.conf import settings

from .bot_registry import registry

logger = logging.getLogger("django")


class BotWebhookView(View):
    async def post(self, request, *args, **kwargs):
        bot_id = kwargs["bot_id"]

        if bot_id not in settings.BOTS:
            raise Http404("Bot not found")

        # Get bot Application from registry
        try:
            app = registry.get(bot_id)
        except ValueError:
            logger.error(f"Bot '{bot_id}' not found in registry")
            raise Http404

        # Ensure app is initialized (idempotent)
        await registry.ensure_initialized(bot_id)

        # Parse incoming update
        try:
            data = json.loads(request.body.decode("utf-8"))
            update = Update.de_json(data, app.bot)
        except Exception as e:
            logger.error(f"Error parsing update: {e}")
            raise Http404

        # Process the update
        try:
            await app.process_update(update)
            return JsonResponse({"ok": True})
        except Exception as e:
            logger.error(f"Error processing update for bot '{bot_id}': {e}")
            raise Http404