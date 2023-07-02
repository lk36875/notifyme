import datetime
from unittest.mock import MagicMock

import pytest

from notify.models.measurements import DayMeasurements
from notify.models.query_params import Frequency
from notify.services.weather_service import WeatherService


@pytest.fixture
def mock_collection():
    return MagicMock()


def test_store_weather(mock_collection):
    date = datetime.datetime.now().strftime("%Y-%m-%d")
    create_dict = {"date": date, "temperature": (20, 20), "precipitation": 0.5, "precipitation_probability": 0.5}
    service = WeatherService(mock_collection)
    day_measurement = DayMeasurements(**create_dict)
    service.store_weather(Frequency.DAY, "New York", "USA", [day_measurement])
    mock_collection.insert_one.assert_called_once_with(
        {"frequency": "day", "city": "New York", "country": "USA", "date": date, "weather": [create_dict]}
    )


def test_check_weather_not_found(mock_collection):
    service = WeatherService(mock_collection)
    mock_collection.find_one.return_value = None
    assert service.get_weather(Frequency.HOUR, "sdfsdffdsdsffd", "UaasSA", "2022-01-01") is None  # type: ignore


def test_get_weather(mock_collection):
    create_dict = {
        "date": "2022-01-01",
        "temperature": [20, 20],
        "precipitation": 0.5,
        "precipitation_probability": 0.5,
    }
    day_measurement = DayMeasurements(**create_dict)
    service = WeatherService(mock_collection)
    mock_collection.find_one.return_value = {
        "frequency": "day",
        "city": "New York",
        "country": "USA",
        "date": "2022-01-01",
        "weather": [create_dict],
    }
    assert service.get_weather(Frequency.DAY, "New York", "USA", "2022-01-01") == [day_measurement]
    mock_collection.find_one.assert_called_once_with(
        {"frequency": "day", "city": "New York", "country": "USA", "date": "2022-01-01"}
    )
