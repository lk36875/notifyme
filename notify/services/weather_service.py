import datetime
from typing import Any

from pymongo.collection import Collection

from notify.app.logger import LoggerType, create_logger
from notify.models.measurements import DayMeasurements, HourMeasurements
from notify.models.query_params import Frequency

logger = create_logger(LoggerType.WEATHER, "WEATHER_SERVICE")


class WeatherService:
    """
    Service class for weather data.

    This class provides methods for storing and retrieving weather data.
    It uses a MongoDB collection to store the data.

    Attributes:
        collection: A `Collection` object representing the MongoDB collection for weather data.
    """

    def __init__(self, collection: Collection[Any]) -> None:
        self.collection = collection

    def store_weather(
        self, frequency: Frequency, city: str, country: str, weather: list[DayMeasurements] | list[HourMeasurements]
    ) -> None:
        """
        Store weather data in MongoDB collection.

        Args:
            frequency: A `Frequency` object representing the frequency of the weather data.
            city: A string representing the city for which the weather data is being stored.
            country: A string representing the country for which the weather data is being stored.
            weather: A list of `DayMeasurements` or `HourMeasurements` objects representing
                the weather data to be stored.
        """
        serialize_weather = [weather.__dict__ for weather in weather]
        data = {
            "frequency": frequency.value,
            "city": city,
            "country": country,
            "date": datetime.datetime.now().strftime("%Y-%m-%d"),
            "weather": serialize_weather,
        }
        try:
            self.collection.insert_one(data)
        except Exception as e:
            logger.exception(e)

    def get_weather(
        self, frequency: Frequency, city: str, country: str, date: str
    ) -> list[DayMeasurements] | list[HourMeasurements] | None:
        """
        Retrieve weather data from mongoDB.

        Args:
            frequency: A `Frequency` object representing the frequency of the weather data.
            city: A string representing the city for which the weather data is being retrieved.
            country: A string representing the country for which the weather data is being retrieved.
            date: A string representing the date for which the weather data is being retrieved.

        Returns:
            A list of `DayMeasurements` or `HourMeasurements` objects representing the retrieved weather data,
                or None if the data was not found.
        """
        logger.info(f"Attempt to retrieve weather for {city}, {country}, {date}")
        data = {"frequency": frequency.value, "city": city, "country": country, "date": date}

        try:
            if (result := self.collection.find_one(data)) is not None and "weather" in result.keys():
                logger.info(f"Weather found for {city}, {country}, {date}")
                weather = result.get("weather")
                if weather is None:
                    raise ValueError("Weather in database is of type None")

                if frequency == Frequency.DAY:
                    deserialized_weather = [DayMeasurements(**weather) for weather in weather]
                else:
                    deserialized_weather = [HourMeasurements(**weather) for weather in weather]
                return deserialized_weather

        except Exception as e:
            logger.exception(e)
        logger.info(f"No weather found for {city}, {country}, {date}")

        return None
