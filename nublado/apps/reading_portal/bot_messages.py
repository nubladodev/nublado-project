from django.utils.translation import gettext_lazy as _

# Translators: Message when there are no draft portals.
# Example: There are no draft portals.
NO_DRAFT_PORTALS = _("reading_portal.bot.no_draft_portals")

# Translators: Message header when listing portals in the queue ready to be posted.
# Example: Reading Portals:
READY_PORTALS = _("reading_portal.bot.ready_reading_portals")

# Translators: Message when there is no open portal in the chat.
# Example: There is no open Reading Portal.
NO_OPEN_PORTAL = _("reading_portal.bot.no_open_portal")

# Translators: Message when there are no portals in the queue ready to be posted.
# Example: There are no portals ready to be posted.
NO_READY_PORTALS = _("reading_portal.bot.no_ready_portals")

# Translators: Message when... 
# Example: ...
ERROR_REVIEW_NO_PENDING_READING = _("reading_portal.bot.error.review_no_pending_reading")

# Translators: Message when a portal isn't found.
# Example: Reading Portal not found.
ERROR_PORTAL_NOT_FOUND = _("reading_portal.bot.error.portal_not_found")

# Translators: Message when a portal required to be ready but isn't.
# Example: Reading Portal not ready to be posted.
ERROR_PORTAL_NOT_READY = _("reading_portal.bot.error.portal_not_ready")

# Translators: Message when an attempt is made to open an already open portal.
# Example: The Reading Portal is already open.
ERROR_PORTAL_ALREADY_OPEN = _("reading_portal.bot.error.portal_already_open")

# Translators: Message when a reading is reviewed by a user.
# {reviewer_name} = username of user who reviewed the reading.
# Example: Reviewed by @fooman.
READING_REVIEWED = _("reading_portal.bot.reading_reviewed {reviewer_name}")

# Translators: Message header when listing pending reading submissions.
# Example: Pending Readings, Pending Reading Submissions
PENDING_READINGS = _("reading_portal.bot.pending_readings")

# Translators: Message when there are no reading submissions pending review for the current Reading Portal pending review.
# Example: There are no pending readings. There are no pending reading submissions.
NO_PENDING_READINGS = _("reading_portal.bot.no_pending_readings")

# Translators: Message header when listing reading submissions.
# Example: Readings, Reading Submissions
READINGS = _("reading_portal.bot.readings")

# Translators: Message when there are no reading submissions for the current Reading Portal.
# Example: There are no readings. There are no reading submissions.
NO_READINGS = _("reading_portal.bot.no_readings")

BOT_MESSAGES = {
    "error.review_no_pending_reading": ERROR_REVIEW_NO_PENDING_READING,
    "error.portal_not_found": ERROR_PORTAL_NOT_FOUND,
    "error.portal_not_ready": ERROR_PORTAL_NOT_READY,
    "error.portal_already_open": ERROR_PORTAL_ALREADY_OPEN,
    "no_draft_portals": NO_DRAFT_PORTALS,
    "no_ready_portals": NO_READY_PORTALS,
    "no_open_portal": NO_OPEN_PORTAL,
    "reading_reviewed": READING_REVIEWED,
    "ready_reading_portals": READY_PORTALS,
    "readings": READINGS,
    "no_readings": NO_READINGS,
    "pending_readings": PENDING_READINGS,
    "no_pending_readings": NO_PENDING_READINGS,
}
