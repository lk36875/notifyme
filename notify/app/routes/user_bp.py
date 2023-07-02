from flask import Blueprint, g, jsonify, request
from flask_jwt_extended import (create_access_token, get_jwt_identity,
                                jwt_required)

from .main_bp import get_user_service

user_bp = Blueprint("user", __name__, url_prefix="/user")


@user_bp.before_request
def before_request_user():
    g.user_service = get_user_service()


@user_bp.get("/")
@user_bp.get("/home")
def home_event():
    """
    Returns the home page for the user blueprint.

    Returns:
        A JSON response containing a welcome message, authorization method, JWT token return route, and available fields.
    """
    fields = {"username": "name of > 3 characters", "email": "valid@email.com", "password": "****"}
    return (
        jsonify(
            {
                "message": "Welcome to user page",
                "authorization method": "jwt_token",
                "jwt_token_return_route": "login",
                "fields": fields,
            }
        ),
        200,
    )


@user_bp.post("/register")
def register():
    """
    Registers a new user.

    Returns:
        A JSON response indicating whether the user was created successfully or not.
    """
    data = request.get_json()
    if g.user_service.create(data):
        return jsonify({"message": "User created successfully"}), 201
    else:
        return jsonify({"message": "User creation failed"}), 400


@user_bp.get("/login")
def login():
    """
    Logs in a user and returns a JWT token.

    Returns:
        A JSON response containing a welcome message and a JWT token.
    """
    data = request.get_json()
    if g.user_service.login(data):
        return jsonify({"message": "Welcome to Notify!", "token": create_access_token(data["username"])}), 200
    else:
        return jsonify({"message": "Invalid credentials"}), 401


@user_bp.post("/change_password")
@jwt_required()
def change_password():
    """
    Changes the password for the current user.

    Returns:
        A JSON response indicating whether the password was changed successfully or not.
    """
    data = request.get_json()
    if "password" not in data.keys():
        return jsonify({"message": "Password not provided"}), 400
    current_user = get_jwt_identity()
    user = g.user_service.get_user({"username": current_user})
    if g.user_service.update({"password": data["password"], "user_id": user.user_id}):
        return jsonify({"message": "Password changed successfully"}), 200
    else:
        return jsonify({"message": "Password change failed"}), 400


@user_bp.post("/update_user")
@jwt_required()
def change_user_data():
    """
    Updates the user data for the current user.

    Returns:
        A JSON response indicating whether the user data was updated successfully or not.
    """
    data = request.get_json()
    if "username" not in data.keys() or "email" not in data.keys():
        return jsonify({"message": "Username or email not provided"}), 400
    current_user = get_jwt_identity()
    user = g.user_service.get_user({"username": current_user})
    data["user_id"] = user.user_id
    if g.user_service.update(data):
        return jsonify({"message": "User updated successfully"}), 200
    else:
        return jsonify({"message": "User update failed"}), 400
