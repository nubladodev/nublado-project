from django.db import models

from django_telegram.models import TelegramChat


class ReadingPortalQuerySet(models.QuerySet):
    """
    QuerySet for ReadingPortalManager
    """
    def base_qs(self):
        """
        A fully hyrated base queryset.
        """
        return self.select_related("chat").prefetch_related("portal_readings")

    def draft(self):
        return self.filter(portal_status=self.model.PortalStatus.DRAFT)

    def ready(self):
        return self.filter(portal_status=self.model.PortalStatus.READY)

    def open(self):
        return self.filter(
            portal_status=self.model.PortalStatus.OPEN,
            opened_at__isnull=False,
        )

    def closed(self):
        return self.filter(
            portal_status=self.model.PortalStatus.CLOSED,
            closed_at__isnull=False,
        )

    def from_chat(self, chat: TelegramChat):
        return self.filter(chat=chat)

    def open_in_chat(self, chat: TelegramChat):
        return (
            self.open()
            .from_chat(chat)
        )

    def closed_in_chat(self, chat: TelegramChat):
        return (
            self.closed()
            .from_chat(chat)
            .order_by("-closed_at", "-id")
        )


class ReadingPortalManager(models.Manager.from_queryset(ReadingPortalQuerySet)):
    """
    Manager for ReadingPortal
    """

    def get_open(self, chat: TelegramChat):
        base = self.get_queryset().base_qs()

        return base.open_in_chat(chat).get()

    def current(self, chat: TelegramChat):
        """
        Get currently open portal in the chat, or fall back to last closed portal.
        """
        base = self.get_queryset().base_qs()

        portal = base.open_in_chat(chat).first()

        if portal:
            return portal

        return base.closed_in_chat(chat).first()

    def next_ready(self, chat: TelegramChat):
        base = self.get_queryset().base_qs()
        return (
            base.ready()
            .from_chat(chat)
            .order_by("created_at")
            .first()
        )

    def existing_open(self, chat: TelegramChat):
        return (
            self.get_queryset()
            .open()
            .from_chat(chat)
            .exists()
        )


class PortalReadingQuerySet(models.QuerySet):
    """
    QuerySet for PortalReadingManager
    """

    def with_portal(self):
        return self.select_related("reading_portal")

    def for_portal(self, portal):
        return self.with_portal().filter(reading_portal=portal).order_by("language")


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
        return self.with_portal().filter(portal_reading__reading_portal=portal)


class ReadingSubmissionManager(models.Manager.from_queryset(ReadingSubmissionQuerySet)):
    """
    Manager for ReadingSubmission
    """
    pass