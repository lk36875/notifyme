from unittest.mock import MagicMock

import pytest

from notify.models.user import User
from notify.services.user_service import InvalidUserDataException, UserService


def test_create_valid_user():
    mock_repository = MagicMock()
    mock_hash_provider = MagicMock()
    service = UserService(mock_repository, mock_hash_provider)

    data = {"username": "john_doe", "email": "john_doe@example.com", "password": "password123"}
    mock_hash_provider.hash.return_value = "hashed_password"

    expected_user = User(user_id=None, username=data["username"], email=data["email"], password="hashed_password")
    mock_repository.create.return_value = True

    assert service.create(data) is True

    mock_repository.create.assert_called_once()
    mock_repository.create.assert_called_once_with(expected_user)


def test_create_invalid_user():
    mock_repository = MagicMock()
    mock_hash_provider = MagicMock()
    service = UserService(mock_repository, mock_hash_provider)
    data = {"username": "john_doe", "email": "invalid_email", "password": "password123"}
    mock_hash_provider.hash.return_value = "hashed_password"
    with pytest.raises(InvalidUserDataException):
        service.create(data)


def test_delete_user():
    mock_repository = MagicMock()
    mock_hash_provider = MagicMock()
    service = UserService(mock_repository, mock_hash_provider)
    user_id = 1
    mock_repository.delete.return_value = None
    assert service.delete(user_id) is True
    mock_repository.delete.assert_called_once_with(user_id)


def test_get_user_by_id():
    mock_repository = MagicMock()
    mock_hash_provider = MagicMock()
    service = UserService(mock_repository, mock_hash_provider)
    user_id = 1
    mock_repository.get_by_id.return_value = User(
        user_id=user_id, username="john_doe", email="john_doe@example.com", password="hashed_password"
    )
    data = {"user_id": user_id}
    user: User = service.get_user(data)
    assert user is not None
    assert user.user_id == user_id
    assert user.username == "john_doe"
    assert user.email == "john_doe@example.com"
    assert user.password == "hashed_password"


def test_get_user_by_email():
    mock_repository = MagicMock()
    mock_hash_provider = MagicMock()
    service = UserService(mock_repository, mock_hash_provider)
    email = "john_doe@example.com"
    mock_repository.get_by_email.return_value = User(
        user_id=1, username="john_doe", email=email, password="hashed_password"
    )
    data = {"email": email}
    user = service.get_user(data)
    assert user is not None
    assert user.user_id == 1
    assert user.username == "john_doe"
    assert user.email == email
    assert user.password == "hashed_password"


def test_get_user_invalid_data():
    mock_repository = MagicMock()
    mock_hash_provider = MagicMock()
    service = UserService(mock_repository, mock_hash_provider)
    data = {"invalid_key": "invalid_value"}
    user = service.get_user(data)
    assert user is None


def test_login():
    mock_repository = MagicMock()
    mock_hash_provider = MagicMock()
    service = UserService(mock_repository, mock_hash_provider)
    username = "john_doe"
    password = "password123"
    mock_repository.get_by_name.return_value = User(
        user_id=1, username=username, email="john_doe@example.com", password="hashed_password"
    )
    mock_hash_provider.check.return_value = True
    data = {"username": username, "password": password}
    result = service.login(data)
    assert result is True


def test_login_invalid():
    mock_repository = MagicMock()
    mock_hash_provider = MagicMock()
    service = UserService(mock_repository, mock_hash_provider)
    email = "john_doe@example.com"
    password = "password123"
    mock_repository.get_by_email.return_value = User(
        user_id=1, username="john_doe", email=email, password="hashed_password"
    )
    mock_hash_provider.check.return_value = False
    data = {"email": email, "password": password}
    result = service.login(data)
    assert result is False
