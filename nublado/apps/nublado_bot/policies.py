from telegram import Update, User
from telegram.ext import ContextTypes

from django.utils.translation import gettext_lazy as _

from django_nublado_telegram.policies import HandlerPolicy


def is_bot_owner(tg_user: User):
    return tg_user.id == settings.NUBLADO["BOT_OWNER_ID"]


class BotOwnerOnly(HandlerPolicy):
    async def check(
        self,
        update: Update,
        context: ContextTypes.DEFAULT_TYPE,
    ) -> bool:

        tg_chat = update.effective_chat
        tg_user = update.effective_user

        if not tg_chat or not tg_user:
            return False

        if not is_bot_owner(tg_user):
            return await self._reply_and_block(
                update,
                context,
                _("Must be bot owner."),
            )

        return True
