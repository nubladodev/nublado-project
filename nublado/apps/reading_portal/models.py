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

# Constant to keep the "open" value consistent in the meta constraint and in the choices enum.
PORTAL_OPEN = "open"


class ReadingPortal(TimestampModel):
    """
    A Reading Portal session.
    """

    class PortalStatus(models.TextChoices):
        DRAFT = "draft", _("Draft")
        SCHEDULED = "scheduled", _("Scheduled")
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

    # Lifecycle.
    opens_at = models.DateTimeField(null=True, blank=True)
    closes_at = models.DateTimeField(null=True, blank=True)

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

        # The opens_at timestamp must be before the closes_at timestamp.
        if self.opens_at and self.closes_at:
            if self.opens_at >= self.closes_at:
                raise ValidationError("opens_at must be earlier than closes_at.")

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
    def is_open(self):
        now = timezone.now()

        if not self.opens_at or not self.closes_at:
            return False

        return (
            self.portal_status == self.PortalStatus.OPEN
            and self.opens_at <= now <= self.closes_at
        )

    async def ahas_readings(self):
        return await self.portal_readings.aexists()

    async def open_portal(self):
        if not self.has_readings:
            raise ValidationError("A Reading Portal must have at least one reading.")

        self.portal_status = self.PortalStatus.OPEN
        await self.asave(update_fields=["portal_status"])

    # def members_incomplete_readings(self):
    #     """
    #     Return member readers who submitted at least one reading but not in all languages
    #     for this Reading Portal session.
    #     """
    #     required_count = len(self.REQUIRED_LANGUAGES)

    #     members = (
    #         TelegramGroupMember.objects.filter(
    #             chat=self.chat, is_active=True, reading_sessions__reading_portal=self
    #         )
    #         .annotate(
    #             submitted_count=Count(
    #                 "reading_submissions",
    #                 filter=Q(reading_submissions__reading_portal=self),
    #             )
    #         )
    #         .filter(submitted_count__lt=required_count, submitted_count__gt=0)
    #     )

    #     return members

    # def members_complete_readings(self):
    #     """
    #     Return members who have submitted all required readings
    #     for this Reading Portal session.
    #     """
    #     required_count = self.portal_readings.count()

    #     members = (
    #         TelegramGroupMember.objects.filter(
    #             chat=self.chat,
    #             is_active=True,
    #             # Only consider members who have at least one submission in this portal.
    #             reading_submissions__reading_portal=self,
    #         )
    #         .annotate(
    #             submitted_count=Count(
    #                 "reading_submissions",
    #                 # Only count submissions that belong to this session.
    #                 filter=Q(reading_submissions__reading_portal=self),
    #             )
    #         )
    #         .filter(submitted_count=required_count)
    #     )

    #     return members

    # def non_participants(self):
    #     """
    #     Return active members who haven't submitted any readings for
    #     this Reading Portal session.
    #     """
    #     members = TelegramGroupMember.objects.filter(
    #         chat=self.chat, is_active=True
    #     ).exclude(reading_submissions__reading_portal=self)

    #     return members

    # # Queue helpers
    # def pending_readings(self, language: str):
    #     """
    #     Return pending reading submissions for the given language,
    #     ordered by submission time.
    #     """
    #     return self.reading_submissions.filter(
    #         language=language,
    #         status=ReadingSubmission.ReadingStatus.PENDING,
    #         member__is_active=True,
    #     ).order_by("submitted_at")

    # def next_pending_reading(self, language: str):
    #     """
    #     Peek at the next pending submission in the queue for a language.
    #     """
    #     return self.pending_readings(language).first()


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
