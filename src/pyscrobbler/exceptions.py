"""Define the program exceptions."""


class Error(Exception):
    """Base class for exceptions in this module."""


class RatingError(Error):
    """Capture errors when rating an item."""


class TaggingError(Error):
    """Capture errors when tagging an item."""


class UndoError(Error):
    """Capture errors when undoing rates or tags."""
