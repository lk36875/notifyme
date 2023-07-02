from datetime import datetime

from notify.app.logger import LoggerType, create_logger
from notify.models.event import Event
from notify.models.measurements import DayMeasurements, HourMeasurements
from notify.models.query_params import EventType, Frequency

logger = create_logger(LoggerType.MAIL, "MESSAGE_BUILDER")


class TextMessageBuilder:
    """
    Class for building text messages from weather data.

    This class provides methods for composing text messages from weather data.
    It defines methods for getting temperature, humidity, and precipitation data,
    as well as methods for composing hourly and daily messages.

    Attributes:
        measurements: A dictionary mapping event types to functions for getting the corresponding weather data.
    """

    def __init__(self):
        self.measurements = {
            EventType.ALL: self.get_all,
            EventType.TEMPERATURE: self.get_temperature,
            EventType.PRECIPITATION: self.get_precipitation,
        }

    def compose_message(self, event: Event, weather: list[HourMeasurements] | list[DayMeasurements]):
        """
        Compose a text message from an event and weather data.

        This method composes a text message from an event and weather data.
        It calls the appropriate method for composing an hourly or daily message based on the event frequency.

        Args:
            event: An `Event` object representing the event for which to compose the message.
            weather: A list of `HourMeasurements` or `DayMeasurements` objects representing the weather data.

        Returns:
            A tuple containing the title and message of the text message, or tuple of None, None
                if the message could not be composed.
        """
        logger.info(f"Composing message for {event.city}, {event.country}")

        event_type = event.event_type
        event_frequency = event.frequency
        title = f"Weather report for {event.city}"

        if event_frequency == Frequency.HOUR:
            message = self.compose_hourly_message(weather, event_type)  # type: ignore
        elif event_frequency == Frequency.DAY:
            message = self.compose_daily_message(weather, event_type)  # type: ignore
        else:
            logger.info(f"Could not compose message for {event.city}, {event.country}")
            return None, None
        return title, message

    def compose_hourly_message(self, weather: list[HourMeasurements], event_type: EventType) -> str | None:
        """
        Compose an hourly message from a list of `HourMeasurements` objects.

        Args:
            weather: A list of `HourMeasurements` objects representing the weather data.
            event_type: An `EventType` object representing the type of event for which to compose the message.

        Returns:
            A string representing the hourly message, or None if the message could not be composed.
        """
        if weather == []:
            return None
        date = weather[0].date
        datetime_object = datetime.fromisoformat(date)
        date_string = datetime_object.strftime("%Y-%m-%d")

        result = []
        result.append(f"Weather for {date_string}\n")
        for measurement in weather:
            time = datetime.fromisoformat(measurement.date).strftime("%H:%M:%S")
            result.append(f"{time}\n{self.measurements[event_type](measurement)}\n\n")

        return "".join(result)

    def compose_daily_message(self, weather: list[DayMeasurements], event_type: EventType) -> str | None:
        """
        Compose a daily message from a list of `DayMeasurements` objects.

        Args:
            weather: A list of `DayMeasurements` objects representing the weather data.
            event_type: An `EventType` object representing the type of event for which to compose the message.

        Returns:
            A string representing the daily message, or None if the message could not be composed.
        """
        if weather == []:
            return None
        result = []
        for measurement in weather:
            result.append(f"{measurement.date}\n{self.measurements[event_type](measurement)}\n")
        return "".join(result)

    def get_temperature(self, measurement: HourMeasurements | DayMeasurements):
        temperature = measurement.temperature
        if isinstance(temperature, tuple):
            return f"Temperature: min: {temperature[0]}°C; max: {temperature[1]}°C."
        else:
            return f"Temperature: {temperature}°C."

    def get_humidity(self, measurement: HourMeasurements):
        return f"Humidity of {measurement.humidity}%."

    def get_precipitation(self, measurement: HourMeasurements | DayMeasurements):
        return (
            f"Precipitation of {measurement.precipitation}mm, "
            f"with probability of {measurement.precipitation_probability}%."
        )

    def get_all(self, measurement: HourMeasurements | DayMeasurements) -> str:
        temperature = self.get_temperature(measurement)
        precipitation = self.get_precipitation(measurement)

        if isinstance(measurement, HourMeasurements):
            humidity = self.get_humidity(measurement)
            return f"{temperature}\n{humidity}\n{precipitation}"
        else:
            return f"{temperature}\n{precipitation}"
