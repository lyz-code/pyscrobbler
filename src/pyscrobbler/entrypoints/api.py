"""Define the pyscrobbler API."""

import logging
from functools import lru_cache
from typing import List, Union

from fastapi import Depends, FastAPI, HTTPException, Response
from fastapi.logger import logger
from repository_orm import EntityNotFoundError, Repository, load_repository

from .. import services
from ..config import Settings
from ..exceptions import RatingError, TaggingError, UndoError
from ..model import EventType, TrackEvent, TrackRate, TrackScrob, TrackTag

log = logging.getLogger("gunicorn.error")
logger.handlers = log.handlers
if __name__ != "main":
    logger.setLevel(log.level)
else:
    logger.setLevel(logging.DEBUG)

app = FastAPI()

# Dependencies


@lru_cache()
def get_settings() -> Settings:
    """Configure the program settings."""
    # no cover: the dependency are injected in the tests
    log.info("Loading the settings")
    return Settings()  # pragma: no cover


def get_repo(settings: Settings = Depends(get_settings)) -> Repository:
    """Configure the repository.

    Returns:
        Configured Repository instance.
    """
    log.info("Loading the repository")
    repo = load_repository([TrackRate, TrackScrob, TrackTag], settings.database_url)

    return repo


# Endpoints


@app.get("/alive")
def alive() -> Response:
    """Return Always.

    Used to see if the application is running.
    """
    return Response(content="Always")


@app.post("/music/scrob", status_code=201)
def scrob(item: TrackScrob, repo: Repository = Depends(get_repo)) -> None:
    """Record a track reproduction.

    Args:
        item: Track scrob information.
        repo: Repository to store the data.
    """
    log.info(f"Scrobbing track {str(item)}")
    services.scrob_track(repo, item)


@app.post("/music/rate", status_code=201)
def rate(item: TrackRate, repo: Repository = Depends(get_repo)) -> None:
    """Record a track rating.

    Args:
        item: Track rate information.
        repo: Repository to store the data.

    Raises:
        HTTPException: if there is a RatingError
    """
    log.info(f"rating track with value {str(item)}")
    try:
        services.rate_track(repo, item)
    except RatingError as error:
        raise HTTPException(status_code=409, detail=str(error)) from error


@app.post("/music/tag", status_code=201)
def tag(item: TrackTag, repo: Repository = Depends(get_repo)) -> None:
    """Record a track tag.

    Args:
        item: Track tag information.
        repo: Repository to store the data.

    Raises:
        HTTPException: if there is a TaggingError
    """
    log.info(f"tagging track with tag {str(item)}")
    try:
        services.tag_track(repo, item)
    except TaggingError as error:
        raise HTTPException(status_code=409, detail=str(error)) from error


@app.get("/music/undo")
def undo(repo: Repository = Depends(get_repo)) -> str:
    """Delete the last rating or tagging.

    Args:
        repo: Repository to store the data.
    """
    log.info("Undoing the last rate or tag")
    try:
        item = services.undo(repo)
        if isinstance(item, TrackRate):
            return (
                f"Removed rating {item.rating} from track {item.item_id}, "
                f"done the {item.date}"
            )
        return f"Removed tag {item.tag} from track {item.item_id}, done the {item.date}"
    except UndoError as error:
        raise HTTPException(status_code=409, detail=str(error)) from error


@app.get("/music")
def history(
    repo: Repository = Depends(get_repo),
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
        item_id: Return only events of this item_id.
    """
    log.info("Printing the history")
    try:
        return services.history(repo=repo, limit=limit, type_=type_, item_id=item_id)
    except EntityNotFoundError as error:
        raise HTTPException(status_code=409, detail=str(error)) from error
