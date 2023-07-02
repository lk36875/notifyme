import os
import random
import string

import pytest
import requests

TEMP_MAIL = os.environ.get("TEMP_MAIL")
BASE = "http://127.0.0.1:5000"


@pytest.fixture(scope="session")
def auth_session():
    session = requests.Session()
    user = {"username": "test_user", "password": "test", "email": TEMP_MAIL}
    session.post(f"{BASE}/user/register", json=user)
    token = session.get(f"{BASE}/user/login", json=user).json()["token"]
    session.headers.update({"Authorization": f"Bearer {token}"})
    yield session


@pytest.fixture(scope="session")
def user():
    SIGN = "".join(random.choices(string.ascii_lowercase, k=6))
    user = {"username": f"test_user{SIGN}", "password": "test", "email": f"{SIGN}@example.com"}
    yield user


def test_get_home():
    response = requests.get(f"{BASE}/")
    assert response.status_code == 200


def test_register(user):
    print(user)
    response = requests.post(f"{BASE}/user/register", json=user)
    assert response.status_code == 201


def test_login(user):
    requests.post(f"{BASE}/user/register", json=user)
    user.pop("email")
    response = requests.get(f"{BASE}/user/login", json=user)
    assert response.status_code == 200


def test_protected(auth_session):
    response = auth_session.get(f"{BASE}/protected")
    assert response.status_code == 200


def test_add_event(auth_session):
    event = {"event_type": "ALL", "frequency": "HOUR", "city": "Warsaw", "country": "Poland"}
    response = auth_session.post(f"{BASE}/event/add", json=event)
    assert response.status_code == 201
    event = {"event_type": "temperature", "frequency": "DAY", "city": "Tokyo", "country": "Japan"}
    response = auth_session.post(f"{BASE}/event/add", json=event)
    assert response.status_code == 201
    event = {"event_type": "precipitation", "frequency": "HOUR", "city": "Berlin", "country": "Germany"}
    response = auth_session.post(f"{BASE}/event/add", json=event)
    assert response.status_code == 201
    response = auth_session.get(f"{BASE}/event/list")
    assert response.status_code == 200
