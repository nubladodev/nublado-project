from django.contrib import admin

from .models import ReadingPortal, PortalReading, ReadingSubmission


@admin.register(ReadingPortal)
class ReadingPortalAdmin(admin.ModelAdmin):
    list_display = (
        "title",
        "chat",
        "is_ready_display",
        "portal_status",
    )
    list_filter = ("portal_status", "chat")
    search_fields = ("title",)
    actions = ["mark_ready", "mark_draft"]

    @admin.display(boolean=True, description="Ready?")
    def is_ready_display(self, obj):
        return obj.is_ready

    def mark_ready(self, request, queryset):
        for portal in queryset:
            try:
                portal.mark_ready()
            except ValidationError as e:
                self.message_user(request, str(e), level="error")

    def mark_draft(self, request, queryset):
        for portal in queryset:
            try:
                portal.mark_draft()
            except ValidationError as e:
                self.message_user(request, str(e), level="error")


@admin.register(PortalReading)
class PortalReadingAdmin(admin.ModelAdmin):
    list_display = ("reading_portal", "language", "message_id", "message_text")
    list_filter = ("language", "reading_portal")


@admin.register(ReadingSubmission)
class ReadingSubmissionAdmin(admin.ModelAdmin):
    list_display = ("portal_reading", "message_id")
