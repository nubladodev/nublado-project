from django.db import models

from django_telegram.models import TelegramChat


class ReadingPortalQuerySet(models.QuerySet):
    """
    QuerySet for ReadingPortalManager
    """

    def draft(self):
        return self.filter(portal_status=self.model.PortalStatus.DRAFT)

    def open(self):
        return self.filter(portal_status=self.model.PortalStatus.OPEN)

    def from_chat(self, chat):
        return self.filter(chat=chat)


class ReadingPortalManager(models.Manager.from_queryset(ReadingPortalQuerySet)):
    """
    Manager for ReadingPortal
    """

    async def aget_open(self, chat: TelegramChat):
        return await (
            self.get_queryset()
            .select_related("chat")
            .prefetch_related("portal_readings")
            .open()
            .from_chat(chat)
            .aget()
        )

    async def anext_draft(self, chat: TelegramChat):
        return await (
            self.get_queryset()
            .select_related("chat")
            .prefetch_related("portal_readings")
            .draft()
            .from_chat(chat)
            .order_by("date_created")
            .afirst()
        )


class PortalReadingQuerySet(models.QuerySet):
    """
    QuerySet for PortalReadingManager
    """
    def with_portal(self):
        return self.select_related("reading_portal")

    def for_portal(self, portal):
        return (
            self.with_portal()
            .filter(reading_portal=portal)
            .order_by("language")
        )


class PortalReadingManager(models.Manager.from_queryset(PortalReadingQuerySet)):
    """
    Manager for PortalReading
    """


class ReadingSubmissionQuerySet(models.QuerySet):
    """
    QuerySet for ReadingSubmission
    """
    def with_portal(self):
        """
        Select related reading portal through portal reading.
        """
        return self.select_related("portal_reading__reading_portal")

    def with_user(self):
        """
        Select related user through member.
        """
        return self.select_related("member__user")

    def pending(self):
        return self.filter(reading_status=self.model.ReadingStatus.PENDING)

    def for_portal(self, portal):
        return (
            self.with_portal()
            .filter(portal_reading__reading_portal=portal)
        )

class ReadingSubmissionManager(models.Manager.from_queryset(ReadingSubmissionQuerySet)):
    """
    Manager for ReadingSubmission
    """
