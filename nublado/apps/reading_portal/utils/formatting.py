from html import escape
from collections import defaultdict

from django.utils.timezone import now

from django_telegram.utils.helpers import message_link
from ..models import ReadingPortal, PortalReading, ReadingSubmission


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


def format_reading_submission_list(
    portal: ReadingPortal,
    reading_submissions: list[ReadingSubmission],
    list_header: str = "Readings",
):
    """
    Return a list of members and corresponding reading-submission links by language.

    Example:
        Readings:
        @user_1: EN, ES
        @user_2: EN
        @user_3: ES
    """

    readings_by_member = defaultdict(list)

    for reading_submission in reading_submissions:
        readings_by_member[reading_submission.member].append(reading_submission)

    readings_list = [f"{list_header} \n"]

    for member, readings in readings_by_member.items():
        language_links = []

        for reading in readings:
            link = message_link(portal.chat_id, reading.message_id)
            language = reading.portal_reading.language.upper()
            language_links.append(f'<a href="{link}">{language}</a>')

        readings_list.append(f"{member.mention_html}: {', '.join(language_links)}")

    return readings_list