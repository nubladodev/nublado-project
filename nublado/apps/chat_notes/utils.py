import re

def normalize_key(key: str):
    """
    Convert a key string into an lowercase, underscore-delimited key 
    (e.g. Invite link -> invite_link).
    """
    key = key.strip().lower()

    # Treat spaces + underscores as separators
    key = re.sub(r"[ _]+", "_", key)

    # Remove anything not alphanumeric or underscore.
    key = re.sub(r"[^\w]", "", key)

    return key