from telegram import Update
from telegram.ext import ContextTypes

from django.db.models import Q

from django_nublado_telegram.models import TelegramChat
from django_nublado_telegram.utils.async_utils import async_call

from .models import GroupRepo, RepoItem
from .utils import normalize_key
from .exceptions import RepoNotConfigured, RepoNotFound


async def save_repo_item_service(
    update: Update, 
    context: ContextTypes.DEFAULT_TYPE, 
    key: str, 
    source_message_id: int,
):
    """
    Save repo item and copy message to repo chat.
    """
    tg_chat = update.effective_chat
    repo_chat_id = context.bot_data.get("repo_chat_id")

    if not repo_chat_id:
        raise RepoNotConfigured("repo_chat_id not set in bot_data")

    repo_chat, created = await async_call(
        TelegramChat.objects.get_or_create_from_chat_id, repo_chat_id
    )
    source_chat, created = await async_call(TelegramChat.objects.get_or_create_from_chat, tg_chat)
    repo, created = await GroupRepo.objects.aget_or_create(
        group_chat=source_chat,
        defaults={"repo_chat": repo_chat},
    )

    copied = await context.bot.copy_message(
        chat_id=repo.repo_chat_id,
        from_chat_id=source_chat.id,
        message_id=source_message_id,
    )

    repo_item, created = await RepoItem.objects.aupdate_or_create(
        repo=repo,
        key=key,
        defaults={
            "message_id": copied.message_id,
        },
    )

    return repo_item


async def get_repo_item_service(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
    key: str
):
    tg_chat = update.effective_chat

    source_chat, created = await async_call(TelegramChat.objects.get_or_create_from_chat, tg_chat)
    repo = await GroupRepo.objects.filter(
        group_chat=source_chat
    ).select_related("repo_chat").afirst()

    if not repo:
        raise RepoNotFound("repo not found")

    key = normalize_key(key)

    repo_item = await RepoItem.objects.select_related(
        "repo"
    ).filter(
        repo=repo,
        key=key
    ).afirst()

    return repo_item


async def list_repo_items_service(update: Update, context: ContextTypes.DEFAULT_TYPE, search_key: str = None):
    tg_chat = update.effective_chat

    source_chat, created = await async_call(TelegramChat.objects.get_or_create_from_chat, tg_chat)
    repo = await GroupRepo.objects.filter(
        group_chat=source_chat
    ).select_related("repo_chat").afirst()

    if not repo:
        raise RepoNotFound("repo not found")

    qs = RepoItem.objects.filter(repo=repo).order_by("key")

    if search_key:
        qs = qs.filter(
            Q(key__startswith=search_key) | Q(key__icontains=search_key)
        )

    results = [item async for item in qs[:20]]

    return results