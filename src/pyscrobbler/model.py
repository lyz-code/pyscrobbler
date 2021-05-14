"""Define the business model of the entitites."""

from datetime import datetime
from enum import Enum
from typing import Optional, Union

from pydantic import Field
from repository_orm import Entity


class EventEntity(Entity):
    """Define the model of a generic scrob."""

    date: datetime = Field(default_factory=datetime.utcnow)


class EventType(str, Enum):
    """Define the possible events."""

    SCROB = "scrob"
    RATE = "rate"
    TAG = "tag"
    ALL = "all"


class TrackEvent(EventEntity):
    """Define the model of a track."""

    item_id: Optional[Union[int, str]] = None
    artist: Optional[str] = None
    title: Optional[str] = None
    duration: Optional[int] = None
    item_duration: Optional[int] = None


class TrackScrobState(str, Enum):
    """Define the possible track scrob states."""

    STARTED = "started"
    FINISHED = "finished"


class TrackScrob(TrackEvent):
    """Define the model of a track reproduction."""

    item_id: Union[int, str]
    state: TrackScrobState = TrackScrobState.FINISHED


class TrackRate(TrackEvent):
    """Define the model of a track rating."""

    rating: int


class TrackTag(TrackEvent):
    """Define the model of a track tag."""

    tag: str
