from telegram import Update
from telegram.error import BadRequest


async def delete_command(update: Update):
    """
    Delete the command message (e.g, /some_command in the chat).
    This is typically called at the  end of a handler once it has done its work
    and the lingering command isn't desired in the chat.
    """
    try:
        await update.effective_message.delete()
    except BadRequest:
        pass