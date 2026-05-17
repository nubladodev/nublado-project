from asgiref.sync import sync_to_async

from django.db import models
from django.db.models import Q
from django.utils import timezone
from django.utils.text import slugify
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

from django_nublado_core.models import TimestampModel, LanguageModel
from django_telegram.models import TelegramChat, TelegramGroupMember

from .managers import (
    ReadingPortalManager,
    PortalReadingManager,
    ReadingSubmissionManager,
)
from .exceptions import EmptyPortal, OpenPortalExists, PortalNotReady, PortalAlreadyOpen


# Constant to keep the "open" value consistent in the meta constraint and in the choices enum.
PORTAL_OPEN = "open"


class ReadingPortal(TimestampModel):
    """
    A Reading Portal session.
    """

    class PortalStatus(models.TextChoices):
        DRAFT = "draft", _("Draft")
        READY = "ready", _("Ready")
        OPEN = PORTAL_OPEN, _("Open")
        CLOSED = "closed", _("Closed")

    chat = models.ForeignKey(
        TelegramChat, on_delete=models.CASCADE, related_name="reading_portals"
    )
    title = models.CharField(max_length=250)
    slug = models.SlugField(
        max_length=250,
        unique=True,
        blank=True,
        help_text="Human-readable unique identifier for the portal",
    )
    description = models.TextField(
        blank=True, help_text="Optional description shown in the portal intro message."
    )
    pinned_message_id = models.BigIntegerField(
        null=True,
        blank=True,
        help_text="Telegram message id of the pinned portal intro message.",
    )
    portal_status = models.CharField(
        max_length=20,
        choices=PortalStatus,
        default=PortalStatus.DRAFT,
    )
    max_mistakes = models.PositiveSmallIntegerField(
        null=True, blank=True, help_text="Maximum number of corrections per submission."
    )
    opened_at = models.DateTimeField(null=True, blank=True)
    closed_at = models.DateTimeField(null=True, blank=True)

    objects = ReadingPortalManager()

    class Meta:
        ordering = ["created_at"]
        indexes = [
            models.Index(fields=["slug"]),
        ]
        constraints = [
            models.UniqueConstraint(
                fields=["chat"],
                # Using constant declared above since Meta can't access
                # PortalStatus.
                condition=Q(portal_status=PORTAL_OPEN),
                name="unique_open_portal_per_chat",
            )
        ]

    def __str__(self):
        return f"Reading Portal: {self.title}"

    def clean(self):
        # Only one Reading Portal session may be open at a time.
        if self.portal_status == self.PortalStatus.OPEN:
            existing_open = ReadingPortal.objects.filter(
                chat=self.chat, portal_status=self.PortalStatus.OPEN
            )
            if self.pk:
                existing_open = existing_open.exclude(pk=self.pk)

            if existing_open.exists():
                # TODO: Redirect user to the curreently opened Reading Portal.
                raise ValidationError("There is already an open Reading Portal.")

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.title)
            slug = base_slug
            counter = 1
            # Ensure uniqueness by appending a counter to the end of a slug if
            # it already exists.
            while ReadingPortal.objects.filter(slug=slug).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1
            self.slug = slug
        super().save(*args, **kwargs)

    @property
    def is_draft(self):
        return self.portal_status == self.PortalStatus.DRAFT

    @property
    def is_ready(self):
        return self.portal_status == self.PortalStatus.READY

    @property
    def is_open(self):
        return (
            self.portal_status == self.PortalStatus.OPEN
            and self.opened_at is not None
        )

    @property
    def is_closed(self):
        return (
            self.portal_status == self.PortalStatus.CLOSED
            and self.closed_at is not None
        )

    def has_readings(self):
        """
        Check if portal has at least one reading.
        """
        return self.portal_readings.exists()

    def can_open(self):
        return (
            self.portal_status in [
                self.PortalStatus.READY,
                self.PortalStatus.CLOSED,
            ]
            and self.has_readings()
        )

    def open(self, pinned_message_id=None):
        if self.is_open:
            raise PortalAlreadyOpen()

        if not self.can_open():
            raise PortalNotReady()

        self.opened_at = timezone.now()
        self.closed_at = None
        self.portal_status = self.PortalStatus.OPEN
        self.pinned_message_id = pinned_message_id

        self.save(
            update_fields=[
                "portal_status",
                "opened_at",
                "closed_at",
                "pinned_message_id",
            ]
        )

    async def aopen(self, pinned_message_id=None):
        await sync_to_async(self.open)(
            pinned_message_id=pinned_message_id
        )

    def close(self):
        self.closed_at = timezone.now()
        self.portal_status = self.PortalStatus.CLOSED

        self.save(
            update_fields=[
                "portal_status",
                "closed_at",
            ]
        )

    async def aclose(self):
        await sync_to_async(self.close)()

    def mark_draft(self):
        # Don't do anything if status is already draft.
        if self.portal_status == self.PortalStatus.DRAFT:
            return

        if self.is_open:
            raise ValidationError("Cannot mark an open portal as draft. Close it first.")

        self.portal_status = self.PortalStatus.DRAFT
        self.opened_at = None
        self.closed_at = None
        self.pinned_message_id = None

        self.save(update_fields=[
            "portal_status",
            "opened_at",
            "closed_at",
            "pinned_message_id",
        ])

    def mark_ready(self):
        # Don't do anything if status is already ready.
        if self.is_ready:
            return

        if self.is_open:
            raise ValidationError("Cannot mark an open portal as ready. Close it first.")

        if not self.has_readings():
            raise ValidationError("Portal must have at least one reading.")

        self.portal_status = self.PortalStatus.READY
        self.opened_at = None
        self.closed_at = None
        self.pinned_message_id = None

        self.save(update_fields=[
            "portal_status",
            "opened_at",
            "closed_at",
            "pinned_message_id",
        ])


class PortalReading(TimestampModel, LanguageModel):
    """
    A language-specific reading provided by a ReadingPortal.
    """

    reading_portal = models.ForeignKey(
        ReadingPortal, related_name="portal_readings", on_delete=models.CASCADE
    )
    message_id = models.BigIntegerField(null=True, blank=True)
    message_text = models.TextField(blank=True)

    objects = PortalReadingManager()

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["reading_portal", "language"],
                name="unique_reading_per_language_per_portal",
            ),
            models.UniqueConstraint(
                fields=["reading_portal", "message_id"],
                condition=models.Q(message_id__isnull=False),
                name="unique_message_id_per_reading_per_portal",
            ),
        ]

    def clean(self):
        if not self.message_id and not self.message_text:
            raise ValidationError("Either message_id or message_text must be provided.")


READING_PENDING = "pending"


class ReadingSubmission(TimestampModel):
    """
    A reading submission for a Reading Portal session.
    """

    RELATED_NAME = "reading_submissions"

    # Note: Superseded status = "This reading is old and doesn't count.
    # A newer version has been submitted that supersedes this one."
    class ReadingStatus(models.TextChoices):
        PENDING = READING_PENDING, _("Pending")
        REVIEWED = "reviewed", _("Reviewed")
        ARCHIVED = "archived", _("Archived")

    portal_reading = models.ForeignKey(
        PortalReading,
        on_delete=models.CASCADE,
        related_name=RELATED_NAME,
    )
    member = models.ForeignKey(
        TelegramGroupMember,
        on_delete=models.CASCADE,
        related_name=RELATED_NAME,
    )

    # Telegram message id of the reading submission.
    message_id = models.BigIntegerField()

    # Optional: message id of the reply message
    # attached to the reading submission (e.g., a #pending tag).
    reply_message_id = models.BigIntegerField(null=True, blank=True)
    reading_status = models.CharField(
        max_length=40,
        choices=ReadingStatus,
        default=ReadingStatus.PENDING,
    )
    submitted_at = models.DateTimeField(auto_now_add=True)

    objects = ReadingSubmissionManager()

    class Meta:
        ordering = ["submitted_at"]
        indexes = [
            models.Index(fields=["portal_reading", "member"]),
        ]
        # Only one pending reading submission per user per language.
        constraints = [
            models.UniqueConstraint(
                fields=["portal_reading", "member"],
                condition=models.Q(reading_status=READING_PENDING),
                name="unique_pending_submission_per_reading_per_member",
            )
        ]

    def __str__(self):
        return f"{self.member.user} for {self.portal_reading.reading_portal.title}"
