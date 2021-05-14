"""Store the classes and fixtures used throughout the tests."""

from typing import List

import pytest
from py._path.local import LocalPath
from repository_orm import Repository, TinyDBRepository
from tests.factories import TrackRateFactory, TrackScrobFactory, TrackTagFactory

from pyscrobbler import TrackRate, TrackScrob, TrackTag
from pyscrobbler.model import TrackEvent


@pytest.fixture(name="db_tinydb")
def db_tinydb_(tmpdir: LocalPath) -> str:
    """Create an TinyDB database engine.

    Returns:
        database_url: Url used to connect to the database.
    """
    # ignore: Call of untyped join function in typed environment.
    # Until they give typing information there is nothing else to do.
    tinydb_file_path = str(tmpdir.join("tinydb.db"))  # type: ignore
    return f"tinydb:///{tinydb_file_path}"


@pytest.fixture(name="repo")
def repo_(db_tinydb: str) -> TinyDBRepository:
    """Return an instance of the TinyDBRepository."""
    return TinyDBRepository([TrackRate, TrackScrob, TrackTag], db_tinydb)


# Model fixtures


@pytest.fixture(name="track_events")
def track_events_(repo: Repository) -> List[TrackEvent]:
    """Create a list of track events."""
    entities = (
        TrackScrobFactory.create_batch(5)
        + TrackRateFactory.create_batch(5)
        + TrackTagFactory.create_batch(5)
    )
    for entity in entities:
        repo.add(entity)
    repo.commit()
    return entities
