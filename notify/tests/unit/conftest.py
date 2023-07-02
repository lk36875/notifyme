import pytest
from flask_jwt_extended import create_access_token

from notify.app import create_app
from notify.app.config import TestConfig
from notify.app.database import mongo_db as mongo
from notify.app.database import psql_db as db


@pytest.fixture(scope="session")
def app():
    """Create and configure the app for testing."""
    app = create_app(TestConfig)
    app.testing = True
    with app.app_context():
        try:
            db.drop_all()
        finally:
            db.create_all()
        yield app
        db.drop_all()


@pytest.fixture(scope="session")
def client_auth(app):
    """A test client for making requests."""
    token = create_access_token("test_user")
    client = app.test_client()
    client.environ_base["HTTP_AUTHORIZATION"] = f"Bearer {token}"
    yield client


@pytest.fixture()
def session():
    """Create and configure the app for testing."""
    app = create_app(TestConfig)
    app.testing = True
    with app.app_context():
        db.drop_all()
        db.create_all()
        yield db.session
        db.drop_all()


@pytest.fixture()
def mongo_db(app):
    """A test client for making requests."""
    mongo_database = mongo.db
    yield app.test_client(), mongo_database
    if mongo_database is not None:
        collection_name = app.config["MONGO_COLLECTION_NAME"]
        mongo_database.drop_collection(collection_name)


@pytest.fixture()
def mongo_collection(app):
    """A test client for making requests."""
    mongo_database = mongo.db
    collection_name = app.config["MONGO_COLLECTION_NAME"]
    yield mongo_database[collection_name]  # type: ignore
    if mongo_database is not None:
        collection_name = app.config["MONGO_COLLECTION_NAME"]
        mongo_database.drop_collection(collection_name)
