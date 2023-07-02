from typing import Any, Protocol

from notify.app.logger import LoggerType, create_logger
from notify.models.event import Event
from notify.models.query_params import Frequency
from notify.models.user import User

logger = create_logger(LoggerType.WEATHER, "SCHEDULER")


class Sender(Protocol):
    def send(self, subject: str, msg: str, receiver: str) -> bool:
        ...


class DatabaseUsers(Protocol):
    def get_users(self) -> list[User] | None:
        ...


class DatabaseEvents(Protocol):
    def get_events_by_frequency(self, user: User, frequency: Frequency) -> list[Event] | None:
        ...


class WeatherProvider(Protocol):
    def get_weather(self, frequency: Frequency, city: str, country: str) -> list[Any] | None:
        ...


class MessageBuilder(Protocol):
    def compose_message(self, event: Event, weather: list) -> tuple[str, Any] | tuple[None, None]:
        ...


class MailScheduler:
    """
    Class for scheduling emails.

    Attributes:
        sender: A `Sender` object representing the email sender to use.
        database_users: A `DatabaseUsers` object representing the user database to use.
        database_events: A `DatabaseEvents` object representing the event database to use.
        weather_provider: A `WeatherProvider` object representing the weather provider to use.
        message_builder: A `MessageBuilder` object representing the message builder to use.
        frequency: A `Frequency` object representing the frequency of the email sends.
    """

    def __init__(
        self,
        sender: Sender,
        database_users: DatabaseUsers,
        database_events: DatabaseEvents,
        weather_provider: WeatherProvider,
        message_builder: MessageBuilder,
        frequency: Frequency,
    ) -> None:
        self.sender = sender
        self.database_users = database_users
        self.database_events = database_events
        self.weather_provider = weather_provider
        self.message_builder = message_builder
        self.frequency = frequency

    def get_users(self) -> list[User] | None:
        return self.database_users.get_users()

    def get_events(self, user: User) -> list[Event] | None:
        return self.database_events.get_events_by_frequency(user, self.frequency)

    def get_weather(self, city: str, country: str) -> list[Any] | None:
        return self.weather_provider.get_weather(self.frequency, city, country)

    def build_message(self, event: Event, weather: list) -> tuple[str, Any] | tuple[None, None]:
        return self.message_builder.compose_message(event, weather)

    def send_mail(self, subject: str, body: str, recipient: str) -> None:
        self.sender.send(subject, body, recipient)

    def run(self) -> None:
        users = self.get_users()
        if users is None:
            return
        logger.info(f"Found {len(users)} users")

        for user in users:
            self.process_user(user)

    def process_user(self, user: User) -> None:
        """
        Processes all events for a given user.

        This function retrieves all events for a given user and processes
        each event using the `process_event` function.
        If an event has already been processed, it is skipped.

        Args:
            user: A `User` object representing the user whose events should be processed.
        """
        events = self.get_events(user)
        if events is None:
            return
        logger.info(f"Found {len(events)} events for {user.email}")

        for event in events:
            self.process_event(user, event)

    def process_event(self, user: User, event: Event) -> None:
        """
        Processes all events for a given user.

        This function retrieves all events for a given user and processes
        each event using the `process_event` function.
        If an event has already been processed, it is skipped.

        Args:
            user: A `User` object representing the user whose events should be processed.
        """
        try:
            weather = self.get_weather(event.city, event.country)
            if weather is None:
                return
            logger.debug("Weather fetched")

            title, message = self.build_message(event, weather)
            if title is not None and message is not None:
                logger.info("Message built successfully")

                self.send_mail(title, message, user.email)
                logger.info(f"Email sent to {user.email}")
        except Exception as e:
            logger.exception(e)
