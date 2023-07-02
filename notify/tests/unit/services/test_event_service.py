from unittest.mock import MagicMock

import pytest

from notify.models.event import Event
from notify.models.query_params import EventType, Frequency
from notify.models.user import User
from notify.repositories.event_repository import EventRepository
from notify.services.event_service import EventService


@pytest.fixture
def user():
    return User(user_id=1, username="testuser", email="testuser@example.com", password="password")


@pytest.fixture
def event_repo():
    return MagicMock(spec=EventRepository)


@pytest.fixture
def event_service(event_repo) -> EventService:
    return EventService(event_repo)


def test_create_event(event_service, event_repo, user: User):
    data = {"event_type": "all", "frequency": "day", "city": "Warsaw", "country": "Poland"}
    event_service.create(user, data)
    event_repo.create.assert_called_once_with(
        Event(user_id=user.user_id, event_type=EventType.ALL, frequency=Frequency.DAY, city="Warsaw", country="Poland")
    )


def test_create_event_invalid_data(event_service, event_repo, user: User):
    data = {"event_type": "invalid", "frequency": "day"}
    assert not event_service.create(user, data)


def test_delete_event(event_service, event_repo, user: User):
    event = Event(user_id=user.user_id, event_type=EventType.ALL, frequency=Frequency.HOUR)
    event_repo.get_by_id.return_value = event
    event_service.delete(user, event.event_id)
    event_repo.delete.assert_called_once_with(user.user_id, event.event_id)


def test_delete_event_not_found(event_service, event_repo, user: User):
    event_repo.delete.side_effect = ValueError
    assert event_service.delete(user, 999) is False


def test_get_event(event_service, event_repo, user: User):
    event = Event(event_id=1, user_id=user.user_id, event_type=EventType.ALL, frequency=Frequency.HOUR)
    event_repo.get_by_id.return_value = event
    assert event_service.get_event(user, 1) == event


def test_get_event_not_found(event_service, event_repo, user: User):
    event_repo.get_by_id.return_value = None
    assert event_service.get_event(user, 999) is None


def test_get_events(event_service, event_repo, user: User):
    event1 = Event(user_id=user.user_id, event_type=EventType.ALL, frequency=Frequency.HOUR)
    event2 = Event(user_id=user.user_id, event_type=EventType.PRECIPITATION, frequency=Frequency.DAY)
    event_repo.get_events.return_value = [event1, event2]
    assert event_service.get_events(user) == [event1, event2]


def test_get_events_empty(event_service, event_repo, user: User):
    event_repo.get_events.return_value = []
    assert event_service.get_events(user) == []
