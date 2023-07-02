import pytest

from notify.models.user import User
from notify.repositories.event_repository import EventRepository
from notify.repositories.user_repository import UserRepository


@pytest.fixture()
def user_repo(session):
    yield UserRepository(session)


@pytest.fixture()
def example_users():
    good_user1 = User(username='john_doe', password='password123', email='john_doe@example.com')
    good_user2 = User(username='jane_doe', password='password456', email='jane_doe@example.com')
    good_user3 = User(username='jane_doe2', password='password456', email='jane_doe2@example.com')

    yield [good_user1, good_user2, good_user3]


@pytest.fixture()
def user_repo_filled(example_users, user_repo):
    for user in example_users:
        user_repo.create(user)
    yield user_repo


@pytest.fixture()
def event_repo(session):
    yield EventRepository(session)
