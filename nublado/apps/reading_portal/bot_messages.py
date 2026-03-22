from django.utils.translation import gettext_lazy as _


BOT_MESSAGES = {
    "error.no_draft_portals": _("reading_portal.bot.error.no_draft_portals"),
    "error.no_pending_readings": _("reading_portal.bot.error.no_pending_readings"),
    "error.review_no_pending_reading": _("reading_portal.bot.error.review_no_pending_reading"),
    "reading_reviewed": _("reading_portal.bot.reading_reviewed {reviewer_name}"),
    "pending_readings": _("reading_portal.bot.pending_readings"),
}