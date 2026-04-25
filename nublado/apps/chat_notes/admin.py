from django.contrib import admin

from .models import GroupRepo, RepoItem


@admin.register(GroupRepo)
class GroupRepoAdmin(admin.ModelAdmin):
    list_display = (
        "group_chat",
        "repo_chat",
    )

@admin.register(RepoItem)
class RepoItemAdmin(admin.ModelAdmin):
    list_display = ("key", "repo")

