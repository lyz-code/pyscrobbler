"""Gather all the orchestration functionality required by the program to work.

Classes and functions that connect the different domain model objects with the adapters
and handlers to achieve the program's purpose.
"""

from contextlib import suppress
from typing import List, Type, Union

from repository_orm import EntityNotFoundError, Repository

from .exceptions import RatingError, TaggingError, UndoError
from .model import EventType, TrackEvent, TrackRate, TrackScrob, TrackTag

TagOrRate = Union[TrackRate, TrackTag]
TagOrRateErrorModel = Union[Type[RatingError], Type[TaggingError]]


def scrob_track(repo: Repository, scrob: TrackScrob) -> None:
    """Register a track scrob.

    Update the scrob duration of the last rated item.

    Args:
        repo: Repository where to store the scrob.
        scrob: Scrob entity to save in the repository.
    """
    repo.add(scrob)
    repo.commit()


def rate_track(repo: Repository, rating: TrackRate) -> None:
    """Register a track rating.

    Update the track information from the last started item.

    Args:
        repo: Repository where to store the scrob.
        rating: Rating entity to save in the repository.

    Raises:
        RatingError: if there are no track scrobs or if the last scrob is in state
            finished.
    """
    _process_rating_or_tagging(repo, rating)


def tag_track(repo: Repository, tag: TrackTag) -> None:
    """Register a track tagging.

    Update the track information from the last started item.

    Args:
        repo: Repository where to store the scrob.
        rating: Rating entity to save in the repository.

    Raises:
        TaggingError: if there are no track scrobs or if the last scrob is in state
            finished.
    """
    _process_rating_or_tagging(repo, tag)


def _process_rating_or_tagging(
    repo: Repository, item: Union[TrackRate, TrackTag]
) -> None:
    """Gather common processing of rating and tagging.

    Update the track information from the last started item.

    Args:
        repo: Repository where to store the scrob.
        item: The rating or tagging data.

    Raises:
        RatingError: if there are no track scrobs or if the last scrob is in state
            finished, and the data is a rating.
        TaggingError: if there are no track scrobs or if the last scrob is in state
            finished, and the data is a tagging.
    """
    if isinstance(item, TrackRate):
        item_error: TagOrRateErrorModel = RatingError
    else:
        item_error = TaggingError

    try:
        last_scrob = repo.last(TrackScrob)
    except EntityNotFoundError as error:
        raise item_error("There are no track scrobs") from error

    if last_scrob.state == "finished":
        raise item_error("There are no tracks in reproduction")

    item = item.copy(
        update={
            "item_id": last_scrob.item_id,
            "artist": last_scrob.artist,
            "title": last_scrob.title,
            "item_duration": last_scrob.item_duration,
            "duration": (item.date - last_scrob.date).seconds,
        }
    )
    repo.add(item)
    repo.commit()


def undo(repo: Repository) -> TagOrRate:
    """Undo the last rating or tagging.

    Args:
        repo: Repository where to store the scrob.

    Returns:
        the deleted item
    Raises:
        UndoError: if there are no rates and tags to undo.
    """
    rates = True
    tags = True

    try:
        last_rate = repo.last(TrackRate)
    except EntityNotFoundError:
        rates = False

    try:
        last_tag = repo.last(TrackTag)
    except EntityNotFoundError:
        tags = False

    if rates and not tags:
        item_to_delete: TagOrRate = last_rate
    elif not rates and tags:
        item_to_delete = last_tag
    elif not rates and not tags:
        raise UndoError("There are no rates or tags to undo")
    else:
        if last_rate.date > last_tag.date:
            item_to_delete = last_rate
        else:
            item_to_delete = last_tag

    repo.delete(item_to_delete)
    repo.commit()
    return item_to_delete


def history(
    repo: Repository,
    limit: int = 10,
    type_: EventType = EventType.ALL,
    item_id: Union[int, str] = -2,
) -> List[TrackEvent]:
    """Get the music event history.

    Args:
        repo: Repository where to store the scrob.
        limit: Limit the number of returned entities.
        type_: Return only the events of this type, possible values are
            `["scrob", "rate", "tag", "all"]`. Default: `"all"`.
        item_id: Return only events of this item_id. If its `-2` it will show all items.

    Returns:
        List of events.

    Raises:
        EntityNotFoundError: if there are no events in the repository.
    """
    events = []

    if type_ == EventType.ALL:
        event_types = [TrackScrob, TrackRate, TrackTag]
    elif type_ == EventType.SCROB:
        event_types = [TrackScrob]
    elif type_ == EventType.RATE:
        event_types = [TrackRate]
    else:
        event_types = [TrackTag]

    with suppress(EntityNotFoundError):
        if item_id == -2:
            events += repo.all(event_types)
        else:
            events += repo.search({"item_id": item_id}, event_types)

    if len(events) == 0:
        raise EntityNotFoundError("There are no events in the history")

    events = sorted(events, key=lambda x: x.date, reverse=True)

    return events[:limit]
