"""Test the music track services."""

from typing import List, Type

import pytest
from repository_orm import Repository

from pyscrobbler import (
    RatingError,
    TaggingError,
    TrackRate,
    TrackScrob,
    TrackTag,
    services,
)
from pyscrobbler.model import EventType, TrackEvent
from pyscrobbler.services import rate_track, tag_track


def test_rate_track_raises_error_if_no_scrobs(repo: Repository) -> None:
    """
    Given: A repo without any scrob
    When: rate_track is called
    Then: an RatingError is raised.
    """
    with pytest.raises(RatingError, match="There are no track scrobs"):
        rate_track(repo, TrackRate(rating=4))


def test_tag_track_raises_error_if_no_scrobs(repo: Repository) -> None:
    """
    Given: A repo without any scrob
    When: tag_track is called
    Then: an TaggingError is raised.
    """
    with pytest.raises(TaggingError, match="There are no track scrobs"):
        tag_track(repo, TrackTag(tag="chill"))


def test_undo_removes_last_rate_over_last_tag(repo: Repository) -> None:
    """
    Given: A repo with a track rating done after a track tagging
    When: undo is called
    Then: The last rating is removed from the repository
    """
    tag = TrackTag(
        item_id=3,
        tag="chill",
    )
    rate = TrackRate(
        item_id=1,
        rating=3,
    )
    repo.add(tag)
    repo.add(rate)
    repo.commit()

    result = services.undo(repo)

    assert result == rate
    assert len(repo.all([TrackRate])) == 0
    tags = repo.all(TrackTag)
    assert len(tags) == 1
    assert tags[0] == tag


def test_undo_removes_last_tag_over_last_rate(repo: Repository) -> None:
    """
    Given: A repo with a track rating done before a track tagging
    When: undo is called
    Then: The last rating is removed from the repository
    """
    rate = TrackRate(
        item_id=1,
        rating=3,
    )
    tag = TrackTag(
        item_id=3,
        tag="chill",
    )
    repo.add(tag)
    repo.add(rate)
    repo.commit()

    result = services.undo(repo)

    assert result == tag
    assert len(repo.all([TrackTag])) == 0
    rates = repo.all(TrackRate)
    assert len(rates) == 1
    assert rates[0] == rate


# W0613: track_events unused, but it is used to add events to the repo.
@pytest.mark.parametrize(
    ("event_name", "event_model"),
    [
        (EventType.SCROB, TrackScrob),
        (EventType.RATE, TrackRate),
        (EventType.TAG, TrackTag),
    ],
)
def test_history_returns_only_one_type_of_event(
    repo: Repository,
    event_name: EventType,
    event_model: Type[TrackEvent],
    track_events: List[TrackEvent],  # noqa: W0613
) -> None:
    """
    Given: A repo with track events
    When: history is called with one event_type
    Then: Only events of that type are returned
    """
    result = services.history(repo, type_=event_name)

    for instance in result:
        assert isinstance(instance, event_model)
