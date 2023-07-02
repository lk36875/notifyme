import os
from abc import ABC

from .database import PSQL


class Config(ABC):
    SECRET_KEY: str = os.environ.get('SECRET_KEY', 'secret')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    TESTING = False


class TestConfig(Config):
    TESTING = True
    HOST = os.environ.get('HOST', 'localhost')
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    MONGO_URI = f'mongodb://{HOST}:27017/test'
    CELERY = dict(
        broker_url=f"redis://{HOST}:6379",
        result_backend=f"redis://{HOST}:6379",
        task_ignore_result=True
    )
    MONGO_COLLECTION_NAME = 'test_collection'


class DevConfig(Config):
    TESTING = False
    SQLALCHEMY_DATABASE_URI: str = PSQL().get_address()

    MONGO_URI = os.environ.get('MONGO_URI', 'mongodb://localhost:27017/weather_data')
    MONGO_COLLECTION_NAME = 'collection'
    SQLALCHEMY_TRACK_MODIFICATIONS = True
    CELERY = dict(
        broker_url=os.environ.get("CELERY_BROKER_URL", "redis://localhost:6379"),
        result_backend=os.environ.get("CELERY_RESULT_BACKEND", "redis://localhost:6379"),
        task_ignore_result=True
    )


class ProdConfig(Config):
    TESTING = False
    SQLALCHEMY_DATABASE_URI: str = PSQL().get_address()
    MONGO_URI = os.environ.get('MONGO_URI')
    MONGO_COLLECTION_NAME = 'weather_collection'
    SQLALCHEMY_TRACK_MODIFICATIONS = True
    CELERY = dict(
        broker_url=os.environ.get("CELERY_BROKER_URL"),
        result_backend=os.environ.get("CELERY_RESULT_BACKEND"),
        task_ignore_result=True
    )
