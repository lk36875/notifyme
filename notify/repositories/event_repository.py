from sqlalchemy.orm import Session
from sqlalchemy.orm.scoping import scoped_session

from notify.app.database import session_scope
from notify.app.logger import LoggerType, create_logger
from notify.models.event import Event
from notify.models.query_params import Frequency

from .repository import Repository

logger = create_logger(LoggerType.EVENT, "EVENT_REPOSITORY")


class EventRepository(Repository):
    """
    Repository class for events.

    This class provides an interface for interacting with the events table in the NotifyMe API database.
    It defines methods for creating, deleting, and retrieving events.

    Attributes:
        session: A SQLAlchemy session object representing the database session.

    Methods use scoped_session to ensure that the session is closed after the method is executed.
    In case of an exception, the session is rolled back. Exceptions are raised to the caller.
    """

    def __init__(self, session: Session | scoped_session) -> None:
        self.session = session

    def create(self, event: Event) -> None:
        with session_scope(self.session) as session:
            session.add(event)
            logger.info(f"Event {event} created")

    def delete(self, user_id: int, event_id: int) -> None:
        event = self.get_by_id(user_id, event_id)
        with session_scope(self.session) as session:
            session.delete(event)
            logger.info(f"Event #{event_id} for user {user_id} has been deleted")

    def get_by_id(self, user_id: int, event_id: int) -> Event:
        with session_scope(self.session) as session:
            event = session.query(Event).where(Event.user_id == user_id, Event.event_id == event_id).first()
        if event is None:
            logger.exception(f"Event with id {event_id} not found")
            raise ValueError(f"Event with id {event_id} not found")
        return event

    def get_events(self, user_id: int):
        with session_scope(self.session) as session:
            events = session.query(Event).where(Event.user_id == user_id).all()
        return events

    def get_events_by_frequency(self, user_id: int, frequency: Frequency):
        with session_scope(self.session) as session:
            events = session.query(Event).where(Event.user_id == user_id, Event.frequency == frequency).all()
        return events
