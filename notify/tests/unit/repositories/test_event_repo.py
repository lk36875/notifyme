"""Testing Repositories"""
import pytest
from sqlalchemy.exc import IntegrityError

from notify.models.event import Event
from notify.models.query_params import EventType, Frequency


class TestEventRepository:
    @pytest.fixture(autouse=True)
    def setup(self, user_repo_filled, event_repo):
        self.user_repo = user_repo_filled
        self.event_repo = event_repo

    def test_event_create(self):
        event = Event(user_id=1, event_type=EventType.ALL, frequency=Frequency.HOUR, city="Warsaw", country="Poland")
        self.event_repo.create(event)
        assert self.event_repo.session.query(Event).count() == 1

    def test_event_create_duplicate(self):
        event1 = Event(user_id=1, event_type=EventType.ALL, frequency=Frequency.HOUR, city="Warsaw", country="Poland")
        event2 = Event(user_id=1, event_type=EventType.ALL, frequency=Frequency.HOUR, city="Warsaw", country="Poland")

        self.event_repo.create(event1)
        with pytest.raises(IntegrityError):
            self.event_repo.create(event2)

    def test_event_delete(self):
        event = Event(user_id=1, event_type=EventType.ALL, frequency=Frequency.HOUR, city="Warsaw", country="Poland")
        self.event_repo.create(event)
        self.event_repo.delete(1, 1)
        assert self.event_repo.session.query(Event).count() == 0

    def test_event_delete_no_event(self):
        with pytest.raises(ValueError):
            self.event_repo.delete(1, 999)

    def test_event_get_event(self):
        event = Event(user_id=1, event_type=EventType.ALL, frequency=Frequency.HOUR, city="Warsaw", country="Poland")
        self.event_repo.create(event)

        retrieved_event = self.event_repo.get_by_id(1, 1)
        assert retrieved_event == event

    def test_event_get_no_event(self):
        with pytest.raises(ValueError):
            self.event_repo.get_by_id(1, 999)


def test_event_get_events(event_repo):
    event1 = Event(user_id=1, event_type=EventType.ALL, frequency=Frequency.HOUR, city="Warsaw", country="Poland")
    event2 = Event(
        user_id=1, event_type=EventType.PRECIPITATION, frequency=Frequency.DAY, city="Warsaw", country="Poland"
    )
    event_repo.create(event1)
    event_repo.create(event2)

    event_repo.get_events(1)
    assert event_repo.session.query(Event).count() == 2


def test_event_get_events_no_events(event_repo):
    events = event_repo.get_events(1)
    assert len(events) == 0


def test_event_get_by_frequency(event_repo):
    event1 = Event(user_id=1, event_type=EventType.ALL, frequency=Frequency.HOUR, city="Warsaw", country="Poland")
    event2 = Event(user_id=1, event_type=EventType.ALL, frequency=Frequency.HOUR, city="London", country="Tokyo")
    event3 = Event(
        user_id=1, event_type=EventType.PRECIPITATION, frequency=Frequency.DAY, city="London", country="Tokyo"
    )
    event_repo.create(event1)
    event_repo.create(event2)
    event_repo.create(event3)

    assert len(event_repo.get_events_by_frequency(1, Frequency.HOUR)) == 2
    assert len(event_repo.get_events_by_frequency(1, Frequency.DAY)) == 1
