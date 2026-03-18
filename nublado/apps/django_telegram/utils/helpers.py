from telegram import Update, User, Chat, ChatMember
from telegram.ext import ContextTypes
from telegram.constants import ChatType, ChatMemberStatus

from django.utils.translation import override


# Helper functions
def _is_group(tg_chat: Chat):
    return tg_chat.type in {ChatType.GROUP, ChatType.SUPERGROUP}


def _is_private(tg_chat: Chat):
    return tg_chat.type == ChatType.PRIVATE


def _is_admin(tg_member: ChatMember):
    return tg_member.status in [
        ChatMemberStatus.ADMINISTRATOR,
        ChatMemberStatus.OWNER,
    ]


def _is_group_owner(tg_member: ChatMember):
    return tg_member.status == ChatMemberStatus.OWNER


def message_link(tg_chat_id: str, tg_message_id: str):
    tg_chat_id = str(tg_chat_id)

    if tg_chat_id.startswith("-100"):
        tg_chat_id = tg_chat_id[4:]

    return f"https://t.me/c/{tg_chat_id}/{tg_message_id}"
