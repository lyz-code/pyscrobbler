"""Test the API backend."""

from typing import List

import pytest
from fastapi.testclient import TestClient
from repository_orm import Repository

from pyscrobbler import TrackRate, TrackScrob, TrackTag, app
from pyscrobbler.config import Settings
from pyscrobbler.entrypoints.api import get_settings
from pyscrobbler.model import TrackEvent


@pytest.fixture(name="client")
def client_(db_tinydb: str) -> TestClient:
    """Configure FastAPI TestClient."""

    def override_settings() -> Settings:
        """Inject the testing database in the application settings."""
        return Settings(database_url=db_tinydb)

    app.dependency_overrides[get_settings] = override_settings
    return TestClient(app)


def test_alive(client: TestClient) -> None:
    """
    Given: The API backend
    When: alive is called
    Then: always is returned
    """
    result = client.get("/alive")

    assert result.status_code == 200
    assert result.text == "Always"


def test_scrob_track_by_id(client: TestClient, repo: Repository) -> None:
    """
    Given: The API backend
    When: /scrob is called with just the id
    Then: the scrob is recorded
    """
    desired_scrob = TrackScrob(id_=0, item_id=3)

    result = client.post("/music/scrob", json={"item_id": 3})

    assert result.status_code == 201
    scrob = repo.last(TrackScrob)
    assert scrob.id_ == desired_scrob.id_
    assert scrob.item_id == desired_scrob.item_id
    assert scrob.state == "finished"
    assert (scrob.date - desired_scrob.date).seconds < 1


def test_scrob_can_mark_track_as_started(client: TestClient, repo: Repository) -> None:
    """
    Given: The API backend
    When: /scrob is called with the id and state started
    Then: the scrob is recorded
    """
    desired_scrob = TrackScrob(id_=0, item_id=3, state="started")

    result = client.post("/music/scrob", json={"item_id": 3, "state": "started"})

    assert result.status_code == 201
    scrob = repo.last(TrackScrob)
    assert scrob.id_ == desired_scrob.id_
    assert scrob.item_id == desired_scrob.item_id
    assert scrob.state == "started"
    assert (scrob.date - desired_scrob.date).seconds < 1


def test_scrob_track_by_id_full_scrob_data(
    client: TestClient, repo: Repository
) -> None:
    """
    Given: The API backend
    When: /scrob is called with all the possible data
    Then: the scrob is recorded
    """
    desired_scrob = TrackScrob(
        id_=0,
        item_id=3,
        artist="JENIX",
        title="Catch Fire",
        duration=360,
        item_duration=360,
    )

    result = client.post(
        "/music/scrob",
        json={
            "item_id": desired_scrob.item_id,
            "artist": desired_scrob.artist,
            "title": desired_scrob.title,
            "duration": desired_scrob.duration,
            "item_duration": desired_scrob.item_duration,
        },
    )

    assert result.status_code == 201
    scrob = repo.last(TrackScrob)
    assert scrob is not None
    assert scrob.id_ == desired_scrob.id_
    assert scrob.item_id == desired_scrob.item_id
    assert scrob.artist == desired_scrob.artist
    assert scrob.title == desired_scrob.title
    assert scrob.state == "finished"
    assert scrob.duration == desired_scrob.duration
    assert scrob.item_duration == desired_scrob.item_duration
    assert (scrob.date - desired_scrob.date).seconds < 1


def test_rate_track(repo: Repository, client: TestClient) -> None:
    """
    Given: The API backend, and a TrackScrob with state started.
    When: /rate is called with just the rating
    Then: The Track rate is recorded, the track attributes are guessed, and the
        duration shows in what second did the rate occur.
    """
    started_track = TrackScrob(id_=0, item_id=3, state="started", item_duration=360)
    repo.add(started_track)
    repo.commit()
    desired_rate = TrackRate(
        id_=0,
        rating=5,
    )

    result = client.post(
        "/music/rate",
        json={
            "rating": desired_rate.rating,
        },
    )

    assert result.status_code == 201
    rate = repo.last(TrackRate)
    assert rate is not None
    assert rate.id_ == desired_rate.id_
    assert rate.rating == desired_rate.rating
    assert rate.item_id == started_track.item_id
    assert rate.item_duration == started_track.item_duration
    assert rate.duration == (desired_rate.date - started_track.date).seconds


def test_rate_track_returns_error_if_no_started_track(
    client: TestClient, repo: Repository
) -> None:
    """
    Given: A repo with a last Scrob with state finished (no track in reproduction)
    When: rate_track is called
    Then: an RatingError is raised.
    """
    last_scrob = TrackScrob(item_id=3, state="finished")
    repo.add(last_scrob)
    repo.commit()

    result = client.post(
        "/music/rate",
        json={
            "rating": 4,
        },
    )

    assert result.status_code == 409
    assert result.json() == {"detail": "There are no tracks in reproduction"}


def test_tag_track(repo: Repository, client: TestClient) -> None:
    """
    Given: The API backend, and a TrackScrob with state started.
    When: /tag is called with the tag
    Then: The Track tag is recorded, the track attributes are guessed, and the duration
        shows in what second did the tag occur.
    """
    started_track = TrackScrob(id_=0, item_id=3, state="started", item_duration=360)
    repo.add(started_track)
    repo.commit()
    desired_tag = TrackTag(
        id_=0,
        tag="chill",
    )

    result = client.post(
        "/music/tag",
        json={
            "tag": desired_tag.tag,
        },
    )

    assert result.status_code == 201
    tag = repo.last(TrackTag)
    assert tag is not None
    assert tag.id_ == desired_tag.id_
    assert tag.tag == desired_tag.tag
    assert tag.item_id == started_track.item_id
    assert tag.item_duration == started_track.item_duration
    assert tag.duration == (desired_tag.date - started_track.date).seconds


def test_tag_track_returns_error_if_no_started_track(
    client: TestClient, repo: Repository
) -> None:
    """
    Given: A repo with a last Scrob with state finished (no track in reproduction)
    When: tag_track is called
    Then: an TaggingError is raised.
    """
    last_scrob = TrackScrob(item_id=3, state="finished")
    repo.add(last_scrob)
    repo.commit()

    result = client.post(
        "/music/tag",
        json={
            "tag": "chill",
        },
    )

    assert result.status_code == 409
    assert result.json() == {"detail": "There are no tracks in reproduction"}


def test_undo_removes_last_rate(client: TestClient, repo: Repository) -> None:
    """
    Given: A repo with a track rating
    When: undo is called
    Then: The last rating is removed from the repository
    """
    first_rate = TrackRate(
        item_id=3,
        rating=5,
    )
    last_rate = TrackRate(
        item_id=1,
        rating=3,
    )
    repo.add(first_rate)
    repo.add(last_rate)
    repo.commit()

    result = client.get("/music/undo")

    assert result.status_code == 200
    assert result.json() == f"Removed rating 3 from track 1, done the {last_rate.date}"
    rates = repo.all(TrackRate)
    assert len(rates) == 1
    assert rates[0] == first_rate


def test_undo_removes_last_tag(client: TestClient, repo: Repository) -> None:
    """
    Given: A repo with a track tag
    When: undo is called
    Then: The last tag is removed from the repository
    """
    first_tag = TrackTag(
        item_id=3,
        tag="chill",
    )
    last_tag = TrackTag(
        item_id=1,
        tag="happy",
    )
    repo.add(first_tag)
    repo.add(last_tag)
    repo.commit()

    result = client.get("/music/undo")

    assert result.status_code == 200
    assert result.json() == f"Removed tag happy from track 1, done the {last_tag.date}"
    tags = repo.all(TrackTag)
    assert len(tags) == 1
    assert tags[0] == first_tag


def test_undo_shows_error_if_no_tags_or_rates(client: TestClient) -> None:
    """
    Given: A repo without any rate or tag
    When: undo is called
    Then: The last rating is removed from the repository
    """
    result = client.get("/music/undo")

    assert result.status_code == 409
    assert result.json() == {"detail": "There are no rates or tags to undo"}


# W0613: track_events unused, but it is used to add events to the repo.
def test_history_shows_the_expected_default_behaviour(
    client: TestClient, track_events: List[TrackEvent]  # noqa: W0613
) -> None:
    """
    Given: A repository with more than 10 events of all types, scrob, tag, rate
    When: /music is called
    Then: Only 10 items are returned of every type.
    """
    result = client.get("/music")

    assert result.status_code == 200
    result_json = result.json()
    assert len(result_json) == 10


# W0613: track_events unused, but it is used to add events to the repo.
def test_history_can_limit_the_entries(
    client: TestClient, track_events: List[TrackEvent]  # noqa: W0613
) -> None:
    """
    Given: A repository with more than 10 events of all types, scrob, tag, rate
    When: /music is called with the limit=2 argument
    Then: Only 2 items are returned of every type.
    """
    result = client.get("/music?limit=2")

    assert result.status_code == 200
    result_json = result.json()
    assert len(result_json) == 2


# W0613: track_events unused, but it is used to add events to the repo.
def test_history_can_select_the_type(
    client: TestClient, track_events: List[TrackEvent]  # noqa: W0613
) -> None:
    """
    Given: A repository with more than 10 events of all types, scrob, tag, rate
    When: /music is called with the type_='scrob'
    Then: Only scrob items are returned.
    """
    result = client.get("/music?type_=scrob")

    assert result.status_code == 200
    result_json = result.json()
    assert len(result_json) == 5


def test_history_can_select_item_id(
    client: TestClient, track_events: List[TrackEvent]
) -> None:
    """
    Given: A repository with more than 10 events of all types, scrob, tag, rate
    When: /music is called with the item_id
    Then: Only events with that item_id are returned.
    """
    item_id = track_events[0].item_id

    result = client.get(f"/music?item_id={item_id}")

    assert result.status_code == 200
    result_json = result.json()
    assert len(result_json) >= 1
    for data in result_json:
        assert data["item_id"] == item_id


def test_history_raises_error_if_no_events_in_repo(client: TestClient) -> None:
    """
    Given: An empty repository
    When: /music is called
    Then: An error is raised.
    """
    result = client.get("/music")

    assert result.status_code == 409
    assert result.json() == {"detail": "There are no events in the history"}
