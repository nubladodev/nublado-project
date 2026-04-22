from html import escape

from django.utils.timezone import now

from ..models import ReadingPortal, PortalReading


def format_portal_intro(portal: ReadingPortal):
    header = "Welcome to the <b><i>Reading Portal</i></b>."
    description = portal.description or ""

    return f"{header}\n\n{description}"


def format_reading(reading: PortalReading):
    language = reading.language.upper()
    header = f"🌧 <b>Reading: {language}</b>"
    
    return f"{header}\n\n{escape(reading.message_text)}"


def format_edited_reading(reading: PortalReading):
    reading_text = format_reading(reading)
    timestamp = now().strftime("%b %d, %H:%M")
    footer = f"\n\n<i>Edited {timestamp} UTC</i>"

    return f"{reading_text}{footer}"


def format_portal_closed():
    return (
        "The <b><i>Reading Portal</i></b> has vanished.\n\n"
        "Please wait for the reading submissions to be reviewed "
        "and a new portal to appear. Thanks."
    )
