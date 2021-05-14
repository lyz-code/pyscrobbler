"""Self-hosted open source multimedia scrobbler."""

from typing import List

from .entrypoints.api import app
from .exceptions import RatingError, TaggingError, UndoError
from .model import TrackRate, TrackScrob, TrackTag

__all__: List[str] = [
    "TrackScrob",
    "TrackRate",
    "TrackTag",
    "app",
    "RatingError",
    "TaggingError",
    "UndoError",
]
