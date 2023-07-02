from sqlalchemy.orm import Session
from sqlalchemy.orm.scoping import scoped_session

from notify.app.database import session_scope
from notify.app.logger import LoggerType, create_logger
from notify.models.user import User

from .repository import Repository

logger = create_logger(LoggerType.USER, "USER_REPOSITORY")


class UserRepository(Repository):
    """
    Repository class for users.

    This class provides an interface for interacting with the users table in the NotifyMe API database.
    It defines methods for creating, deleting, and retrieving users.

    Attributes:
        session: A SQLAlchemy session object representing the database session.

    Methods use scoped_session to ensure that the session is closed after the method is executed.
    In case of an exception, the session is rolled back. Exceptions are raised to the caller.
    """

    def __init__(self, session: Session | scoped_session) -> None:
        self.session = session

    def create(self, user: User) -> None:
        with session_scope(self.session) as session:
            session.add(user)
            logger.info(f"User {user} created")

    def update(self, user_id: int, data: dict) -> None:
        user = self.get_by_id(user_id)
        attr, value = data.popitem()
        with session_scope(self.session):
            user.__setattr__(attr, value)

    def delete(self, user_id: int) -> None:
        user = self.get_by_id(user_id)
        with session_scope(self.session):
            self.session.delete(user)
            logger.info(f"User {user} deleted")

    def get_by_id(self, user_id: int) -> User:
        user = self.session.get(User, user_id)
        if not user:
            logger.warning(f"User with id {user_id} not found")
            raise ValueError(f"User with id {user_id} not found")
        return user

    def get_by_name(self, name: str) -> User:
        user = self.session.query(User).where(User.username == name).first()
        if not user:
            raise ValueError(f"User with name {name} not found")
        return user

    def get_by_email(self, email: str) -> User:
        user = self.session.query(User).where(User.email == email).first()
        if not user:
            raise ValueError(f"User with email {email} not found")
        return user

    def get_all(self) -> list[User]:
        return self.session.query(User).all()
