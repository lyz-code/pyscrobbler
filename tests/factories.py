"""Define the factories of the program models."""

import factory
from faker_enum import EnumProvider
from faker_optional import OptionalProvider

from pyscrobbler import TrackRate, TrackScrob, TrackTag
from pyscrobbler.model import EventEntity, TrackEvent, TrackScrobState

factory.Faker.add_provider(EnumProvider)
factory.Faker.add_provider(OptionalProvider)


class EventFactory(factory.Factory):  # type: ignore
    """Generate a fake Event."""

    id_ = factory.Faker("pyint")
    date = factory.Faker("date_time")

    class Meta:
        """Declare the factory model."""

        model = EventEntity


class TrackFactory(EventFactory):
    """Generate a fake TrackEvent."""

    artist = factory.Faker("optional_word")
    title = factory.Faker("optional_sentence")
    duration = factory.Faker("optional_int")
    item_duration = factory.Faker("optional_int")

    class Meta:
        """Declare the factory model."""

        model = TrackEvent


class TrackScrobFactory(TrackFactory):
    """Generate a fake Scrob."""

    item_id = factory.Faker("pyint")
    state = factory.Faker("enum", enum_cls=TrackScrobState)

    class Meta:
        """Declare the factory model."""

        model = TrackScrob


class TrackRateFactory(TrackFactory):
    """Generate a fake Rate."""

    item_id = factory.Faker("optional_int")
    rating = factory.Faker("pyint", max_value=5, min_value=1)

    class Meta:
        """Declare the factory model."""

        model = TrackRate


class TrackTagFactory(TrackFactory):
    """Generate a fake Tag."""

    item_id = factory.Faker("optional_int")
    tag = factory.Faker("word")

    class Meta:
        """Declare the factory model."""

        model = TrackTag
