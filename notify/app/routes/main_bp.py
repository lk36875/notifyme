from flask import Blueprint, current_app, g, jsonify
from flask_jwt_extended import get_jwt_identity, jwt_required

from notify.app.database import psql_db as db
from notify.repositories.event_repository import EventRepository
from notify.repositories.hash_functions import BcryptHash
from notify.repositories.user_repository import UserRepository
from notify.services.event_service import EventService
from notify.services.user_service import UserService

main_bp = Blueprint("main", __name__)


def get_user_service():
    with current_app.app_context():
        if "user_service" not in g:
            user_repository = UserRepository(db.session)  # type: ignore
            g.user_service = UserService(user_repository, BcryptHash)
        return g.user_service


def get_event_service():
    with current_app.app_context():
        if "event_service" not in g:
            user_repository = EventRepository(db.session)  # type: ignore
            g.event_service = EventService(user_repository)
        return g.event_service


@main_bp.route("/")
@main_bp.route("/home")
def index():
    """
    Returns the home page for the main blueprint.

    Returns:
        A JSON response containing a welcome message and a link to the API help page.
    """
    return jsonify({"message": "Welcome to NotifyMe! For endpoint information, reach /api/help route."}), 200


@main_bp.route("/protected")
@jwt_required()
def protected():
    """
    Does nothing. Used to test JWT authorization.

    Returns:
        A JSON response containing a welcome message and the username of the authenticated user.
    """
    current_user = get_jwt_identity()
    return jsonify({"message": f"Hello, {current_user}!"}), 200


@main_bp.route("/api", methods=["GET"])
def this_func():
    """
    Does nothing.

    Returns:
        An empty JSON response.
    """
    return jsonify({"result": ""})


@main_bp.route("/api/help", methods=["GET"])
def help():
    """
    Returns a list of available functions for the API.

    Returns:
        A JSON response containing a dictionary of available functions and their docstrings.
    """
    func_list = {}
    for rule in current_app.url_map.iter_rules():
        if rule.endpoint != "static":
            func_list[rule.rule] = current_app.view_functions[rule.endpoint].__doc__
    return jsonify(func_list)
