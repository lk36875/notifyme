"""Testing Repositories"""
import pytest
from sqlalchemy.exc import IntegrityError

from notify.models.user import User
from notify.repositories.user_repository import UserRepository


def test_user_repository(session):
    ur = UserRepository(session)
    assert ur.session == session


def test_user_repository_create(user_repo):
    user = User(username='john_doe', password='password123', email='john_doe@example.com')
    user_repo.create(user)
    assert user_repo.session.query(User).count() == 1


def test_user_repository_create_not_unique(user_repo):
    user = User(username='john_doe', password='password123', email='john_doe@example.com')
    user_same = User(username='john_doe', password='password123', email='john_doe@example.com')
    user_username = User(username='john_doe', password='password123', email='sdds@example.com')
    user_mail = User(username='john_doe2', password='password123', email='john_doe@example.com')

    user_repo.create(user)
    for bad_user in [user_same, user_username, user_mail]:
        with pytest.raises(IntegrityError):
            user_repo.create(bad_user)


def test_user_repository_create_multiple(user_repo, example_users):
    for user in example_users:
        user_repo.create(user)
    assert user_repo.session.query(User).count() == 3


def test_user_repository_delete(user_repo_filled):
    user_repo_filled.delete(1)
    assert user_repo_filled.session.query(User).count() == 2
    user_repo_filled.delete(2)
    assert user_repo_filled.session.query(User).count() == 1


def test_user_repository_none(user_repo_filled):
    with pytest.raises(ValueError):
        user_repo_filled.delete(111)


def test_user_repository_update(user_repo_filled):
    user_repo_filled.update(1, {'username': 'john_doe2'})
    user_repo_filled.update(2, {'email': 'bla@gmail.com'})
    user_repo_filled.update(3, {'password': 'pass'})

    assert user_repo_filled.session.get(User, 1).username == 'john_doe2'
    assert user_repo_filled.session.get(User, 2).email == 'bla@gmail.com'
    assert user_repo_filled.session.get(User, 3).password == 'pass'


def test_user_repository_get_by_id(user_repo_filled):
    assert user_repo_filled.get_by_id(1).email == 'john_doe@example.com'


def test_user_repository_get_by_id_missing(user_repo_filled):
    with pytest.raises(ValueError):
        user_repo_filled.get_by_id(123)


def test_user_repository_get_by_id_not_found(user_repo_filled):
    assert user_repo_filled.session.get(User, 123) is None


def test_user_repository_get_by_email(user_repo_filled):
    assert user_repo_filled.get_by_email('john_doe@example.com').username == 'john_doe'


def test_user_repository_get_by_email_not_found(user_repo_filled):
    with pytest.raises(ValueError):
        user_repo_filled.get_by_email('x@example.com')


def test_get_by_name(user_repo_filled):
    username = 'john_doe'
    user = user_repo_filled.get_by_name(username)
    mock_user = User(user_id=1, username=username, email='john_doe@example.com', password='hashed_password')
    assert user == mock_user


def test_get_by_name_not_found(user_repo_filled):
    with pytest.raises(ValueError):
        user_repo_filled.get_by_name('x@example.com')


def test_get_all(user_repo_filled):
    users = user_repo_filled.get_all()
    assert len(users) == 3
    assert users[0].username == 'john_doe'
    assert users[1].username == 'jane_doe'
    assert users[2].username == 'jane_doe2'
