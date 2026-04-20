import os
import httpx

from telegram import Update
from telegram.ext import ContextTypes

from django.conf import settings


async def transcribe(update: Update, context: ContextTypes.DEFAULT_TYPE):
    tg_message = update.effective_message

    # Must be a reply to a voice message
    if not tg_message.reply_to_message or not tg_message.reply_to_message.voice:
        await tg_message.reply_text("Reply to a voice message.")
        return

    voice = tg_message.reply_to_message.voice

    # Optional: language arg (/transcribe en)
    language = context.args[0] if context.args else "en"

    # Telegram file download
    file = await context.bot.get_file(voice.file_id)
    file_path = f"/tmp/{file.file_unique_id}.ogg"

    msg = await tg_message.reply_text("Transcribing… ⏳")

    try:
        await file.download_to_drive(custom_path=file_path)

        url = "https://api.deepgram.com/v1/listen"

        headers = {
            "Authorization": f"Token {settings.DEEPGRAM_API_TOKEN}",
        }

        params = {
            "model": "nova-2",
            "language": language,
            "punctuate": "true",
            "smart_format": "true",
        }

        async with httpx.AsyncClient(timeout=60.0) as client:
            with open(file_path, "rb") as f:
                response = await client.post(
                    url,
                    headers=headers,
                    params=params,
                    files={"file": ("audio.ogg", f, "audio/ogg")},
                )

        # Handle HTTP errors cleanly
        if response.status_code != 200:
            await msg.edit_text(f"Deepgram error: {response.text}")
            return

        result = response.json()

        # Extract transcript safely
        try:
            transcript = result["results"]["channels"][0]["alternatives"][0]["transcript"]
        except (KeyError, IndexError):
            transcript = None

        if not transcript:
            await msg.edit_text("Could not transcribe audio.")
            return

        await msg.edit_text(transcript)

    except Exception as e:
        await msg.edit_text(f"Error: {str(e)}")

    finally:
        if os.path.exists(file_path):
            os.remove(file_path)