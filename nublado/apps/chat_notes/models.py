from django.db import models

from django_nublado_telegram.models import TelegramChat

from .utils import normalize_key


class GroupRepo(models.Model):
    group_chat = models.ForeignKey(
        TelegramChat,
        on_delete=models.CASCADE,
        related_name="grouprepo_groups"
    )
    repo_chat = models.ForeignKey(
        TelegramChat, 
        on_delete=models.CASCADE,
        related_name="grouprepo_repos"
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["group_chat"],
                name="unique_repo_per_group"
            ),
            models.UniqueConstraint(
                fields=["repo_chat"],
                name="unique_group_per_repo"
            )
        ]


class RepoItem(models.Model):
    repo = models.ForeignKey(GroupRepo, on_delete=models.CASCADE)
    key = models.SlugField()
    message_id = models.BigIntegerField()

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["repo", "key"],
                name="unique_key_per_repo"
            ),
        ]

    def save(self, *args, **kwargs):
        normalized = normalize_key(self.key)

        if self.key != normalized:
            self.key = normalized

        super().save(*args, **kwargs)