
class ReadingPortalError(Exception):
    """Base exception for Reading Portal domain."""

    default_message = "Reading Portal error."

    def __init__(self, message=None):
        self.message = message or self.default_message
        super().__init__(self.message)

    def __str__(self):
        return str(self.message)

class PortalNotReady(ReadingPortalError):
    """
    Exception raised when a portal is required to be ready, and it isn't.
    """
    default_message = "The portal isn't ready to be opened."


class PortalAlreadyOpen(ReadingPortalError):
    default_message = "The portal is already open."


class NoCurrentPortal(ReadingPortalError):
    default_message = "Portal not found."


class NoReadyPortal(ReadingPortalError):
    """
    Exception raised when there is no ready portal to be open.
    """
    default_message = "There are no portals ready to be opened."


class NoOpenPortal(ReadingPortalError):
    default_message = "There is no open portal."


class OpenPortalExists(ReadingPortalError):
    default_message = "An open portal already exists."


class EmptyPortal(ReadingPortalError):
    default_message = "The portal is empty. It must have at least one reading."


class NoPendingReading(ReadingPortalError):
    default_message = "Therare no pending readings."


class NoExistingReading(ReadingPortalError):
    default_message = "The reading doesn't exist."


class NoReadingMessageId(ReadingPortalError):
    default_message = "No reading message id found."
