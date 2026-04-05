from django.utils.translation import gettext_lazy as _

# Translators: Message when there are no draft portals in the queue to be posted.
# Example: There are no portals ready to be posted.
ERROR_NO_DRAFT_PORTALS = _("reading_portal.bot.error.no_draft_portals")

# Translators: Message when there are no readings submissions pending review.
# Example: There are no pending readings. There are no pending reading submissions.
ERROR_NO_PENDING_READINGS = _("reading_portal.bot.error.no_pending_readings")

# Translators: Message when... 
# Example: ...
ERROR_REVIEW_NO_PENDING_READING = _("reading_portal.bot.error.review_no_pending_reading")

# Translators: Message when a portal isn't found.
# Example: Reading Portal not found.
ERROR_PORTAL_NOT_FOUND = _("reading_portal.bot.error.portal_not_found")

# Translators: Message when a reading is reviewed by a user.
# {reviewer_name} = username of user who reviewed the reading.
# Example: Reviewed by @fooman.
READING_REVIEWED = _("reading_portal.bot.reading_reviewed {reviewer_name}")

# Translators: Message header when listing pending reading submissions.
# Example: Pending Reading Submissions:
PENDING_READINGS = _("reading_portal.bot.pending_readings")

# Translators: Message header when listing portals in the queue ready to be posted.
# Example: Reading Portals:
READING_PORTALS = _("reading_portal.bot.draft_reading_portals")

BOT_MESSAGES = {
    "error.no_draft_portals": ERROR_NO_DRAFT_PORTALS,
    "error.no_pending_readings": ERROR_NO_PENDING_READINGS,
    "error.review_no_pending_reading": ERROR_REVIEW_NO_PENDING_READING,
    "error.portal_not_found": ERROR_PORTAL_NOT_FOUND,
    "reading_reviewed": READING_REVIEWED,
    "pending_readings": PENDING_READINGS,
    "draft_reading_portals": READING_PORTALS,
}
