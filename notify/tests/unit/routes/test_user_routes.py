from flask_jwt_extended import create_access_token


def test_home(client_with_user):
    response = client_with_user.get("/user/home")
    assert response.status_code == 200


def test_register(client_with_user):
    data = {"username": "john_doe2", "password": "password123", "email": "john_doe2@example.com"}
    response = client_with_user.post("/user/register", json=data)
    assert response.status_code == 201
    assert response.json == {"message": "User created successfully"}


def test_register_duplicate(client_with_user):
    data = {"username": "john_doe", "email": "john_doe@example.com", "password": "password123"}
    response = client_with_user.post("/user/register", json=data)
    assert response.status_code == 400
    assert response.json == {"message": "User creation failed"}


def test_login(client_with_user):
    data = {"username": "john_doe", "password": "password123"}
    response = client_with_user.get("/user/login", json=data)
    assert response.status_code == 200
    assert "token" in response.json


def test_login_invalid(client_with_user):
    data = {"email": "john_doe@example.com", "password": "wrong_password"}
    response = client_with_user.get("/user/login", json=data)
    assert response.status_code == 401
    assert response.json == {"message": "Invalid credentials"}


def test_change_password(client_with_user):
    data = {"password": "new_password"}
    token = create_access_token("john_doe")
    headers = {"Authorization": f"Bearer {token}"}
    response = client_with_user.post("/user/change_password", json=data, headers=headers)
    assert response.status_code == 200
    assert response.json == {"message": "Password changed successfully"}


def test_change_user_data(client_with_user):
    data = {"username": "jane_doe", "email": "jane_doe@example.com"}
    token = create_access_token("john_doe")
    headers = {"Authorization": f"Bearer {token}"}
    response = client_with_user.post("/user/update_user", json=data, headers=headers)
    assert response.status_code == 200
    assert response.json == {"message": "User updated successfully"}


def test_change_user_data_invalid(client_with_user):
    data = {"sth": "sth"}
    token = create_access_token("john_doe")
    headers = {"Authorization": f"Bearer {token}"}
    response = client_with_user.post("/user/update_user", json=data, headers=headers)
    assert response.status_code == 400
    assert response.json == {"message": "Username or email not provided"}


def test_protected(client_with_user):
    token = create_access_token("john_doe")
    headers = {"Authorization": f"Bearer {token}"}
    response = client_with_user.get("/protected", headers=headers)
    assert response.status_code == 200
    assert response.json == {"message": "Hello, john_doe!"}
