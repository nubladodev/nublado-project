from html import escape
from collections import defaultdict

from django.utils.timezone import now

from django_nublado_telegram.utils.helpers import message_link
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
    *,
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

    submissions_by_member = defaultdict(list)

    for submission in reading_submissions:
        submissions_by_member[submission.member].append(submission)

    submissions_list = [f"{list_header} \n"]

    for member, submissions in submissions_by_member.items():
        language_links = []

        for submission in submissions:
            link = message_link(portal.chat_id, submission.message_id)
            language = submission.portal_reading.language.upper()
            language_links.append(f'<a href="{link}">{language}</a>')

        submissions_list.append(f"{member.mention_html}: {', '.join(language_links)}")

    return submissions_list