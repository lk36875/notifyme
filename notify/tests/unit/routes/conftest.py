import pytest
from flask_jwt_extended import create_access_token

from notify.app import create_app
from notify.app.config import TestConfig
from notify.app.database import psql_db as db
from notify.models.event import Event
from notify.models.query_params import EventType, Frequency
from notify.models.user import User
from notify.repositories.hash_functions import BcryptHash


@pytest.fixture()
def client_with_user():
    """Create and configure the app for testing."""
    app = create_app(TestConfig)
    app.testing = True
    with app.app_context():
        try:
            db.create_all()
        finally:
            pass
        user = User(username="john_doe", email="john_doe@example.com", password="password123")
        user.password = BcryptHash().hash(user.password)
        db.session.add(user)
        yield app.test_client()
        db.session.rollback()
        db.drop_all()


@pytest.fixture()
def authorized_header(client_with_user):
    token = create_access_token("john_doe")
    headers = {"Authorization": f"Bearer {token}"}
    yield headers


@pytest.fixture()
def add_objects(client_with_user):
    def create_events(user_id):
        event = Event(
            user_id=user_id, event_type=EventType.ALL, frequency=Frequency.DAY, city="Warsaw", country="Poland"
        )
        event1 = Event(
            user_id=user_id,
            event_type=EventType.PRECIPITATION,
            frequency=Frequency.HOUR,
            city="Warsaw",
            country="Poland",
        )
        event2 = Event(
            user_id=user_id, event_type=EventType.ALL, frequency=Frequency.DAY, city="Tokyo", country="Japan"
        )
        event3 = Event(
            user_id=user_id, event_type=EventType.ALL, frequency=Frequency.HOUR, city="Tokyo", country="Japan"
        )
        return [event, event1, event2, event3]

    test_client = client_with_user
    test_client.post(
        "/user/register", json={"username": "john_doe2", "email": "abc2@example.com", "password": "password123"}
    )

    for event in create_events(1):
        db.session.add(event)

    for event in create_events(2):
        db.session.add(event)
    db.session.commit()
    yield
