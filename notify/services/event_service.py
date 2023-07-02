from notify.app.logger import LoggerType, create_logger
from notify.models.event import Event
from notify.models.query_params import EventType, Frequency
from notify.models.user import User
from notify.repositories.event_repository import EventRepository
from notify.weather.location_provider import OpenMeteoLocationProvider

logger = create_logger(LoggerType.EVENT, "EVENT_SERVICE")


class EventService:
    """
    Service class for events.

    This class provides methods for creating, deleting, and retrieving events.
    It uses an `EventRepository` object to interact with the events table in the NotifyMe API database.
    Location_provider is used to retrieve location data for cities.

    Attributes:
        event_type: A dictionary mapping strings to `EventType` objects.
        frequency: A dictionary mapping strings to `Frequency` objects.
        repository: An `EventRepository` object representing the repository for events.
        location_provider: A location provider object for retrieving location data.
    """

    event_type = {"all": EventType.ALL, "precipitation": EventType.PRECIPITATION, "temperature": EventType.TEMPERATURE}
    frequency = {"hour": Frequency.HOUR, "day": Frequency.DAY}

    def __init__(self, event_repository: EventRepository, location_provider=OpenMeteoLocationProvider()) -> None:
        self.repository = event_repository
        self.location_provider = location_provider

    def create(self, user: User, data: dict) -> bool:
        """
        Create a new event.

        This method creates a new event in the database with the given data.

        Args:
            user: A `User` object representing the user who owns the event.
            data: A dictionary representing the data to be stored in the database.

        Returns:
            A boolean value indicating whether the event was created successfully.

        Raises:
            ValueError: If the given data is invalid.
        """

        if not self._validate_event(data):
            logger.warning(f"Failed to create event {data}")
            return False

        city, country, event_type, frequency = data["city"], data["country"], data["event_type"], data["frequency"]
        if self.location_provider.get_location(city, country) is None:
            logger.warning(f"Failed to create event, location not found for {city}, {country}")
            return False

        event_type = self.event_type[event_type.lower()]
        frequency = self.frequency[frequency.lower()]
        event = Event(user_id=user.user_id, event_type=event_type, frequency=frequency, city=city, country=country)

        try:
            self.repository.create(event)
            logger.info(f"Created event {event}")
            return True
        except Exception as e:
            logger.exception(e)
            return False

    def delete(self, user: User, event_id: int) -> bool:
        """
        Delete an event based on its ID.

        Args:
            user: A `User` object representing the user who owns the event.
            event_id: An integer representing the ID of the event to be deleted.

        Returns:
            A boolean value indicating whether the event was deleted successfully.
        """
        try:
            self.repository.delete(user.user_id, event_id)
            return True
        except Exception as e:
            logger.exception(e)
            return False

    def get_event(self, user: User, event_id: int) -> Event | None:
        """
        Retrieve an event by ID.

        Args:
            user: A `User` object representing the user who owns the event.
            event_id: An integer representing the ID of the event to be retrieved.

        Returns:
            An `Event` object representing the retrieved event, or None if the event was not found.
        """
        try:
            if event_id is not None:
                return self.repository.get_by_id(user.user_id, event_id)
        except Exception as e:
            logger.exception(e)
            return None

    def get_events(self, user: User) -> list[Event] | None:
        """
        Retrieve an event for user.

        Args:
            user: A `User` object representing the user who owns the event.

        Returns:
            A list of `Event` objects representing the retrieved event, or None if an error occurred.
        """
        try:
            return self.repository.get_events(user.user_id)
        except Exception as e:
            logger.exception(e)
            return None

    def get_events_by_frequency(self, user: User, frequency: Frequency) -> list[Event] | None:
        """
        Retrieve events for a user by frequency.

        Args:
            user: A `User` object representing the user whose events are to be retrieved.
            frequency: A `Frequency` object representing the frequency of the events to be retrieved.

        Returns:
            A list of `Event` objects representing the retrieved events, or None if an error occurred.
        """
        try:
            return self.repository.get_events_by_frequency(user.user_id, frequency)
        except Exception as e:
            logger.exception(e)
            return None

    def _validate_event(self, data: dict) -> bool:
        """
        Validate event data for creating a new event.

        Args:
            data: A dictionary representing the data to be validated.

        Returns:
            A boolean value indicating whether the data is valid.
        """
        if data.get("event_type", "").lower() not in self.event_type.keys():
            return False
        if data.get("frequency", "").lower() not in self.frequency.keys():
            return False

        if (city := data.get("city")) is None or len(city) < 2 or len(city) > 70:
            return False
        if (country := data.get("country")) is None or len(country) < 2 or len(country) > 70:
            return False

        return True
