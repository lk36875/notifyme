from datetime import datetime
from typing import Protocol

from notify.app.logger import LoggerType, create_logger
from notify.models.measurements import DayMeasurements, HourMeasurements
from notify.models.query_params import Frequency

from .weather_provider import WeatherProvider

logger = create_logger(LoggerType.WEATHER, "WEATHER_MANAGER")


class LocationProvider(Protocol):
    def get_location(self, city: str, country: str) -> tuple[float, float] | None:
        ...


class DatabaseService(Protocol):
    def store_weather(self, frequency, city, country, weather) -> None:
        ...

    def get_weather(
        self, frequency: Frequency, city: str, country: str, date: str
    ) -> list[DayMeasurements] | list[HourMeasurements] | None:
        ...


class WeatherManager:
    """
    Weather manager for retrieving weather data.

    This class provides methods for retrieving weather data from a `WeatherProvider`
    and storing it in a `DatabaseService`.
    It also provides methods for retrieving temperature and precipitation data.

    Attributes:
        weather_provider: A `WeatherProvider` object representing the weather provider to use.
        location_provider: A `LocationProvider` object representing the location provider to use.
        database_service: A `DatabaseService` object representing the database service to use.
    """

    measurement_type = {"day": DayMeasurements, "hour": HourMeasurements}

    def __init__(
        self, weather_provider: WeatherProvider, location_provider: LocationProvider, database_service: DatabaseService
    ) -> None:
        self.weather_provider = weather_provider
        self.location_provider = location_provider
        self.database_service = database_service

    def get_weather(
        self, frequency: Frequency, city: str, country: str
    ) -> list[DayMeasurements] | list[HourMeasurements]:
        logger.info(f"Getting weather for {city}, {country}, {frequency}")

        data = self._get_measurements(city, country, frequency)
        return data

    def get_temperature(self, city: str, country: str, frequency: Frequency) -> list[dict]:
        data = self._get_measurements(city, country, frequency)
        return [{d.date: d.temperature} for d in data]

    def get_precipitation(self, city: str, country: str, frequency: Frequency) -> list[dict]:
        data = self._get_measurements(city, country, frequency)
        return [{d.date: (d.precipitation, d.precipitation_probability)} for d in data]

    def _get_measurements(
        self, city: str, country: str, frequency: Frequency
    ) -> list[DayMeasurements] | list[HourMeasurements]:
        """
        Retrieve weather measurements.

        This method retrieves weather measurements for a given city, country, and frequency.
        It first checks the `DatabaseService` for cached data, and if none is found,
        it retrieves data from the `WeatherProvider` and stores it in the `DatabaseService`.

        Args:
            city: A string representing the city for which to retrieve the weather measurements.
            country: A string representing the country for which to retrieve the weather measurements.
            frequency: A `Frequency` object representing the frequency of the weather measurements to retrieve.

        Returns:
            A list of `DayMeasurements` or `HourMeasurements` objects representing the weather measurements
                for the given city, country, and frequency.
        """
        date = datetime.now().strftime("%Y-%m-%d")
        logger.info(f"Getting weather for {city}, {country}, {date}, {frequency}")

        if weather := self.database_service.get_weather(frequency, city, country, date):
            return weather

        location = self.location_provider.get_location(city, country)
        logger.info(f"Location found for {city}, {country}")
        if location is None:
            raise ValueError(f"Location not found for {city}, {country}")

        if frequency == frequency.DAY:
            weather_received = self.weather_provider.get_weather_daily(*location)
        else:
            weather_received = self.weather_provider.get_weather_hourly(*location)
        logger.info(f"Weather received for {city}, {country}")

        self.database_service.store_weather(frequency, city, country, weather_received)
        logger.info(f"Weather stored for {city}, {country}")
        return weather_received

    def check_location(self, city: str, country: str) -> bool:
        """
        Check if a location is valid.

        Args:
            city: A string representing the city to check.
            country: A string representing the country to check.

        Returns:
            A boolean representing whether the location is valid.
        """
        return self.location_provider.get_location(city, country) is not None
