import os

from flask import Flask
from flask.json.provider import DefaultJSONProvider

from notify.authentication.user_authorization import jwt
from notify.celery_app.init_celery import celery_init_app
from notify.celery_app.tasks import celery_app
from notify.repositories import bcrypt

from .config import Config, DevConfig, ProdConfig, TestConfig
from .database import mongo_db, psql_db
from .routes import event_bp, main_bp, user_bp


class CustomJSONProvider(DefaultJSONProvider):
    sort_keys = False


def create_app(config: type[Config] = DevConfig) -> Flask:
    """
    Application factory for Flask.

    This function creates a new Flask application with the given configuration.
    It initializes extensions, databases, Celery and registers blueprints.

    Args:
        config: A subclass of `Config` representing the configuration to use for the application.

    Returns:
        A `Flask` object representing the new application.
    """

    if os.environ.get("FLASK_ENV", "").lower() == "test":
        config = TestConfig
    elif os.environ.get("FLASK_ENV", "").lower() == "production":
        config = ProdConfig

    # Config and Json Provider initialization
    app = Flask(__name__)
    app.config.from_object(config)
    app.json = CustomJSONProvider(app)

    # Extensions initialization
    jwt.init_app(app)
    bcrypt.init_app(app)

    # Database initialization
    psql_db.init_app(app)
    mongo_db.init_app(app)

    celery_init_app(celery_app, app)

    if os.environ.get("FLASK_ENV") == "development":
        with app.app_context():
            psql_db.drop_all()
            psql_db.create_all()
    elif os.environ.get("FLASK_ENV") == "production":
        with app.app_context():
            psql_db.create_all()

    # Blueprints registration
    app.register_blueprint(main_bp)
    app.register_blueprint(user_bp)
    app.register_blueprint(event_bp)

    return app
