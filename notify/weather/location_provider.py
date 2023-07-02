import json

import requests
from geopy.geocoders import Nominatim

from notify.app.logger import LoggerType, create_logger

from . import OPEN_MATEO_CONFIG

logger = create_logger(LoggerType.WEATHER, "LOCATION_PROVIDER")


class NominatimLocationProvider:
    """
    Location provider using the Nominatim geocoding service.

    This class provides a method for retrieving the latitude and longitude of
    a given city and country using the Nominatim geocoding service.

    Attributes:
        geolocator: A `Nominatim` object representing the geocoding service.
    """

    def __init__(self) -> None:
        logger.info("Initializing location provider")
        self.geolocator = Nominatim(user_agent="notify")

    def get_location(self, city: str, country: str) -> tuple[float, float] | None:
        location = self.geolocator.geocode(f"{city}, {country}")
        logger.info(f"Location found for {city}, {country}, {location}")
        if location is None:
            return None
        return location.latitude, location.longitude  # type: ignore


class OpenMeteoLocationProvider:
    """
    Location provider using the OpenMeteo API.

    This class provides a method for retrieving the latitude and longitude
    of a given city and country using the OpenMeteo API.

    Attributes:
        config: A dictionary representing the configuration for the OpenMeteo API.
    """

    config: dict

    def __init__(self) -> None:
        logger.info("Initializing location provider")

        with open(OPEN_MATEO_CONFIG) as f:
            self.config = json.load(f)

        if self.config is None:
            logger.exception("OpenMeteo config not found")
            raise ValueError("OpenMeteo config not found")

    def get_location(self, city: str, country: str) -> tuple[float, float] | None:
        """
        Retrieve the latitude and longitude of a location using the OpenMeteo API.

        Args:
            city: A string representing the city for which to retrieve the location.
            country: A string representing the country for which to retrieve the location.

        Returns:
            A tuple of floats representing the latitude and longitude of the location, or None
                if the location could not be found.
        """

        location = None

        if city in [None, ""] or country in [None, ""]:
            return location

        try:
            url = self.get_url(city, country)
            logger.debug(f"Url <{url}> | {city}, {country}")
            location = requests.get(url, timeout=(10, 10)).json()
        except requests.exceptions.Timeout as e:
            logger.exception(f"Timeout while getting location for {city}, {country}")
        except Exception as e:
            logger.exception(f"Error {e} while getting location for {city}, {country}")

        if location is None:
            return location

        if location.get("results") is None:
            logger.warning(f"Location not found for {city}, {country}")
            return None
        results: dict[str, float] = location["results"][0]
        latitude, longitude = results["latitude"], results["longitude"]
        return latitude, longitude

    def get_url(self, city: str, country: str) -> str:
        """
        Generate the URL for the OpenMeteo API based on the given city and country.

        Args:
            city: A string representing the city for which to generate the URL.
            country: A string representing the country for which to generate the URL.

        Returns:
            A string representing the URL for the OpenMeteo API.
        """
        base_url = self.config["base_url_location"]
        return f"{base_url}?name={city}%2C+{country}&count=1&language=en&format=json"
