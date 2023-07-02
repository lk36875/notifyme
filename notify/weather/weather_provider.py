import json
from abc import ABC, abstractmethod
from time import sleep

import requests

from notify.app.logger import LoggerType, create_logger
from notify.models.measurements import DayMeasurements, HourMeasurements

from . import OPEN_MATEO_CONFIG

logger = create_logger(LoggerType.WEATHER, "OPENMATEO")


class WeatherProvider(ABC):
    @abstractmethod
    def get_weather_daily(self, latitude: float, longitude: float) -> list[DayMeasurements]:
        ...

    @abstractmethod
    def get_weather_hourly(self, latitude: float, longitude: float) -> list[HourMeasurements]:
        ...


class OpenMeteo(WeatherProvider):
    """
    Weather provider using the OpenMeteo API.

    This class provides methods for retrieving daily and hourly weather measurements using the OpenMeteo API.

    Attributes:
        config: A dictionary representing the configuration for the OpenMeteo API.
        base_url: A string representing the base URL for the OpenMeteo API.
    """

    config: dict

    def __init__(self) -> None:
        with open(OPEN_MATEO_CONFIG) as f:
            self.config = json.load(f)
            self.base_url = self.config["base_url"]

        if self.config is None:
            logger.exception("OpenMeteo config not found")
            raise ValueError("OpenMeteo config not found")

    def _format_url_hourly(self, latitude: float, longitude: float) -> str:
        """
        Format the URL for retrieving hourly weather measurements.

        Args:
            latitude: A float representing the latitude of the location for which to retrieve weather measurements.
            longitude: A float representing the longitude of the location for which to retrieve weather measurements.

        Returns:
            A string representing the URL for retrieving hourly weather measurements from the OpenMeteo API.
        """
        url = (
            f"{self.base_url}?latitude={latitude}&longitude={longitude}"
            "&hourly=temperature_2m,relativehumidity_2m,precipitation,"
            "precipitation_probability&timezone=auto&forecast_days=1"
        )
        return url

    def _format_url_daily(self, latitude: float, longitude: float) -> str:
        """
        Format the URL for retrieving daily weather measurements.

        Args:
            latitude: A float representing the latitude of the location for which to retrieve weather measurements.
            longitude: A float representing the longitude of the location for which to retrieve weather measurements.

        Returns:
            A string representing the URL for retrieving daily weather measurements from the OpenMeteo API.
        """
        url = (
            f"{self.base_url}?latitude={latitude}&longitude={longitude}"
            "&daily=temperature_2m_max,temperature_2m_min,precipitation_sum,"
            "precipitation_probability_max&timezone=auto"
        )
        return url

    def get_weather_daily(self, latitude: float, longitude: float) -> list[DayMeasurements]:
        """
        Retrieve daily weather measurements.

        Args:
            latitude: A float representing the latitude of the location for which to retrieve weather measurements.
            longitude: A float representing the longitude of the location for which to retrieve weather measurements.

        Returns:
            A list of `DayMeasurements` objects representing the daily weather measurements for the location.
        """
        url = self._format_url_daily(latitude, longitude)
        logger.info(f"Getting weather for {latitude}, {longitude} at url {url}")

        results = None
        try:
            results = requests.get(url, timeout=(10, 10)).json()
        except requests.exceptions.Timeout:
            logger.exception(f"Timeout while getting daily weather for {latitude}, {longitude}")
        except Exception as e:
            logger.exception(f"Error {e} while getting daily weather for {latitude}, {longitude}")

        if results is None:
            return []

        results = results["daily"]
        measurements = []
        for values in zip(
            results["time"],
            results["temperature_2m_min"],
            results["temperature_2m_max"],
            results["precipitation_sum"],
            results["precipitation_probability_max"],
        ):
            date, *temperature, precipitation, precipitation_probability = values
            measurements.append(
                DayMeasurements(
                    date=date,
                    temperature=tuple(temperature),
                    precipitation=precipitation,
                    precipitation_probability=precipitation_probability,
                )
            )
        return measurements

    def get_weather_hourly(self, latitude: float, longitude: float) -> list[HourMeasurements]:
        """
        Retrieve hourly weather measurements.

        Args:
            latitude: A float representing the latitude of the location for which to retrieve weather measurements.
            longitude: A float representing the longitude of the location for which to retrieve weather measurements.

        Returns:
            A list of `HourMeasurements` objects representing the hourly weather measurements for the location.
        """
        url = self._format_url_hourly(latitude, longitude)
        logger.info(f"Getting weather for {latitude}, {longitude} at url {url}")

        results = None
        try:
            results = requests.get(url, timeout=(10, 10)).json()
        except requests.exceptions.Timeout:
            logger.exception(f"Timeout while getting daily weather for {latitude}, {longitude}")
        except Exception as e:
            logger.exception(f"Error {e} while getting daily weather for {latitude}, {longitude}")

        if results is None:
            return []

        results = results["hourly"]
        measurements = []
        for values in zip(
            results["time"],
            results["temperature_2m"],
            results["relativehumidity_2m"],
            results["precipitation"],
            results["precipitation_probability"],
        ):
            date, temperature, humidity, precipitation, precipitation_probability = values
            measurements.append(
                HourMeasurements(
                    date=date,
                    temperature=temperature,
                    humidity=humidity,
                    precipitation=precipitation,
                    precipitation_probability=precipitation_probability,
                )
            )
        return measurements
