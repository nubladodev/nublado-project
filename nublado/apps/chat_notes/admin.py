from import_export.admin import ImportExportModelAdmin

from django.contrib import admin

from .models import GroupRepo, RepoItem


@admin.register(GroupRepo)
class GroupRepoAdmin(ImportExportModelAdmin):
    list_display = (
        "group_chat",
        "repo_chat",
    )

@admin.register(RepoItem)
class RepoItemAdmin(ImportExportModelAdmin):
    list_display = ("key", "repo")

