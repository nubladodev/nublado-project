from django.db import models
from django.db.models import Q
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

# Constant to keep the "open" value consistent in the meta constraint and in the choices enum.
PORTAL_OPEN = "open"


class ReadingPortal(TimestampModel):
    """
    A Reading Portal session.
    """

    class PortalStatus(models.TextChoices):
        DRAFT = "draft", _("Draft")
        SCHEDULED = "scheduled", _("Scheduled")
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

    objects = ReadingPortalManager()

    class Meta:
        ordering = ["date_created"]
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
        return self.portal_satus == self.PortalStatus.OPEN

    async def has_readings(self):
        """
        Check if portal has at least one reading.
        """
        return self.portal_readings.exists()

    async def ahas_readings(self):
        """
        async: Check if portal has at least one reading.
        """
        return await self.portal_readings.aexists()

    async def open_portal(self):
        if not await self.ahas_readings:
            raise ValidationError("A Reading Portal must have at least one reading.")

        self.portal_status = self.PortalStatus.OPEN
        await self.asave(update_fields=["portal_status"])

    def mark_draft(self):
        # Don't do anything if status is already draft.
        if self.portal_status == self.PortalStatus.DRAFT:
            return

        if self.portal_status == self.PortalStatus.OPEN:
            raise ValidationError("Can't mark an open portal as draft. Close it first.")

        self.portal_status = self.PortalStatus.DRAFT
        self.save(update_fields=["portal_status"])

    def mark_ready(self):
        # Don't do anything if status is already ready.
        if self.portal_status == self.PortalStatus.READY:
            return

        if self.portal_status == self.PortalStatus.OPEN:
            raise ValidationError("Can't mark an open portal as ready. Close it first.")

        if not self.has_readings():
            raise ValidationError("Portal must have at least one reading.")

        # Optional: enforce required languages
        # languages = set(self.portal_readings.values_list("language", flat=True))
        # required = {"en", "es"} 

        # if not required.issubset(languages):
        #     raise ValidationError("Missing required languages.")

        self.portal_status = self.PortalStatus.READY
        self.save(update_fields=["portal_status"])


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
