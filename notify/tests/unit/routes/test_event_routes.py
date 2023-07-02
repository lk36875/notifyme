import pytest


def test_event_home(client_with_user):
    response = client_with_user.get("/event/home")
    assert response.status_code == 200


def get_test_data():
    for item in [
        {"event_type": "all", "frequency": "day", "city": "Warsaw", "country": "Poland"},
        {"event_type": "precipitation", "frequency": "hour", "city": "Berlin", "country": "Germany"},
        {"event_type": "temperature", "frequency": "day", "city": "Tokyo", "country": "Japan"},
        {"event_type": "all", "frequency": "hour", "city": "Prague", "country": "Czechia"},
    ]:
        yield item


def add_event(client, headers, data):
    response = client.post("/event/add", json=data, headers=headers)
    return response


@pytest.mark.skip("API blocked")
def test_event_add(client_with_user, authorized_header):
    for event in get_test_data():
        response = add_event(client_with_user, authorized_header, event)
        assert response.status_code == 201


@pytest.mark.parametrize(
    "data",
    [
        {"event_type": "alwel", "frequency": "day", "city": "Warsaw", "country": "Poland"},
        {"event_type": "precipitation", "frequency": "", "city": "Warsaw", "country": "Poland"},
        {"event_type": "temperature", "frequency": "day", "city": "", "country": "Japan"},
        {"event_type": "all", "frequency": "hour", "city": "Tokyo", "country": ""},
        {"event_type": "alwel", "frequency": "day", "city": "Warsaw", "country": "asdasdasd"},
        {"event_type": "precipitations or sth", "frequency": "", "city": "Warsaw", "country": "Poland"},
        {"event_type": "temp", "frequency": "day", "city": "", "country": "Japan"},
        {"event_type": "all", "frequency": "week", "city": "Tokyo", "country": ""},
    ],
)
def test_event_add_invalid(client_with_user, authorized_header, data):
    response = client_with_user.post("/event/add", json=data, headers=authorized_header)
    assert response.status_code == 400


def test_event_delete(client_with_user, authorized_header, add_objects):
    client = client_with_user
    response = client.delete("/event/remove/1", headers=authorized_header)
    response2 = client.delete("/event/remove/2", headers=authorized_header)
    response3 = client.delete("/event/remove/3", headers=authorized_header)
    response4 = client.delete("/event/remove/1", headers=authorized_header)

    assert response.status_code == 201
    assert response2.status_code == 201
    assert response3.status_code == 201
    assert response4.status_code == 400


def test_event_get(client_with_user, authorized_header, add_objects):
    response = client_with_user.get("/event/1", headers=authorized_header)

    assert response.status_code == 200
    assert len(response.json) == 1
    assert response.json["event"]


def test_event_get_all(client_with_user, authorized_header, add_objects):
    response = client_with_user.get("/event/list", headers=authorized_header)

    assert response.status_code == 200
    assert len(response.json["events"]) == 4
