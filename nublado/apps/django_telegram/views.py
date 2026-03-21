import json

from telegram import Update

from django.http import Http404, JsonResponse
from django.views import View
from django.conf import settings

from .bot_registry import registry


class BotWebhookView(View):
    async def post(self, request, *args, **kwargs):
        # bot_id = kwargs["bot_id"]
        # if bot_id not in settings.BOTS:
        #     await registry.ensure_initialized(bot_id)

        #     app = registry.get(bot_id)

        #     try:
        #         data = json.loads(request.body.decode("utf-8"))
        #     except Exception as e:
        #         logger.error(f"Error in decoding update: {e}")
        #         raise Http404
        #     try:
        #         update = Update.de_json(data, app.bot)
        #         await app.process_update(update)
        #         return JsonResponse({"ok": True})
        #     except Exception as e:
        #         logger.error(f"Error in processing update: {e}")
        #         raise Http404
        # else:
        #     raise Http404

        # bot_id = kwargs["bot_id"]

        # if bot_id not in settings.BOTS:
        #     raise Http404(f"Bot '{bot_id}' not recognized.")

        # Get the already-initialized bot from the registry
        bot_id = kwargs["bot_id"]
        app = registry.get(bot_id)

        try:
            # Parse the incoming Telegram update
            data = json.loads(request.body.decode("utf-8"))
            update = Update.de_json(data, app.bot)

            # Process the update (handlers already registered)
            await app.process_update(update)

            return JsonResponse({"ok": True})

        except Exception as e:
            logger.error(f"Error processing update for bot '{bot_id}': {e}")
            raise Http404

