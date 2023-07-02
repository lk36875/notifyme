from flask import Blueprint, g, jsonify, request
from flask_jwt_extended import get_jwt_identity, jwt_required

from .main_bp import get_event_service, get_user_service

event_bp = Blueprint("event", __name__, url_prefix="/event")


@event_bp.before_request
def before_request_event():
    g.event_service = get_event_service()
    g.user_service = get_user_service()


@event_bp.get("/")
@event_bp.get("/home")
def home_event():
    """
    Returns the home page for the event blueprint.

    Returns:
        A JSON response containing a welcome message, JWT token, and available fields.
    """
    fields = {
        "event_type": "all/precipitation/temperature",
        "frequency": "day/hour",
        "city": "city",
        "country": "country",
    }
    return jsonify({"message": "Welcome to event page", "jwt_token": "obligatory", "fields": fields}), 200


@event_bp.post("/add")
@jwt_required()
def add_event():
    """
    Adds a new event for the current user.

    Returns:
        A JSON response indicating whether the event was created successfully or not.
    """
    current_user = get_jwt_identity()
    user = g.user_service.get_user({"username": current_user})
    if user is None:
        return jsonify({"message": "User not found"}), 404

    data = request.get_json()
    if g.event_service.create(user, data):
        return jsonify({"message": "Event created successfully"}), 201
    else:
        return jsonify({"message": "Event creation failed"}), 400


@event_bp.delete("/remove/<id>")
@jwt_required()
def remove_event(id):
    """
    Removes an event with the specified ID for the current user.

    Args:
        id: The ID of the event to remove.

    Returns:
        A JSON response indicating whether the event was deleted successfully or not.
    """
    current_user = get_jwt_identity()
    user = g.user_service.get_user({"username": current_user})
    if user is None:
        return jsonify({"message": "User not found"}), 404

    if g.event_service.delete(user, id):
        return jsonify({"message": "Event deleted successfully"}), 201
    else:
        return jsonify({"message": "Event id is incorrect."}), 400


@event_bp.get("/<id>")
@jwt_required()
def get_event(id):
    """
    Returns the event with the specified ID for the current user.

    Args:
        id: The ID of the event to retrieve.

    Returns:
        A JSON response containing the event data.
    """
    current_user = get_jwt_identity()
    user = g.user_service.get_user({"username": current_user})
    if user is None:
        return jsonify({"message": "User not found"}), 404

    if event := g.event_service.get_event(user, id):
        return jsonify({"event": f"{event}"}), 200
    else:
        return jsonify({"message": f"Event #{id} not found"}), 400


@event_bp.get("/list")
@jwt_required()
def get_events():
    """
    Returns a list of all events for the current user.

    Returns:
        A JSON response containing a dictionary of event IDs and their corresponding data.
    """
    current_user = get_jwt_identity()
    user = g.user_service.get_user({"username": current_user})
    if user is None:
        return jsonify({"message": "User not found"}), 404

    if events := g.event_service.get_events(user):
        result_dict = {event.event_id: str(event) for event in events}
        return jsonify({"events": result_dict}), 200
