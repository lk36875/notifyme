from flask_jwt_extended import create_access_token


def test_protected(client_with_user):
    token = create_access_token("john_doe")
    headers = {"Authorization": f"Bearer {token}"}
    response = client_with_user.get("/protected", headers=headers)
    assert response.status_code == 200
    assert response.json == {"message": "Hello, john_doe!"}


def test_home(client_with_user):
    response_home = client_with_user.get("/home")
    response_home_2 = client_with_user.get("/")

    assert response_home.status_code == 200
    assert response_home_2.status_code == 200


def test_api(client_with_user):
    repsonse = client_with_user.get("/api")
    assert repsonse.status_code == 200
    assert repsonse.json == {"result": ""}


def test_list_api(client_with_user):
    response = client_with_user.get("/api/help")
    assert response.status_code == 200
