import os
from contextlib import contextmanager

from flask_pymongo import PyMongo
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import Session
from sqlalchemy.orm.scoping import scoped_session

psql_db = SQLAlchemy()
mongo_db = PyMongo()


class PSQL:
    """Compose the address for the PostgreSQL database."""
    def __init__(self):
        self.db_name = os.environ.get('POSTGRES_DB_NAME')
        self.user = os.environ.get('POSTGRES_USER')
        self.host = os.environ.get('POSTGRES_HOST')
        self.port = os.environ.get('POSTGRES_PORT')
        self.password = os.environ.get('POSTGRES_PASSWORD')

    def get_address(self) -> str:
        return f'postgresql://{self.user}:{self.password}@{self.host}:{self.port}/{self.db_name}'


@contextmanager
def session_scope(session: Session | scoped_session):
    """Provide a transactional scope around a series of operations."""
    try:
        session.expire_on_commit = False  # type: ignore
        yield session
        session.commit()
    except Exception as e:
        session.rollback()
        raise
