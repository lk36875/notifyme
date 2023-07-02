import datetime

import pytest
from pymongo.collection import Collection

from notify.models.query_params import Frequency
from notify.services.weather_service import WeatherService
from notify.weather.location_provider import OpenMeteoLocationProvider
from notify.weather.weather_manager import WeatherManager
from notify.weather.weather_provider import OpenMeteo

FAKE_TIME = datetime.datetime(2022, 10, 10, 17, 5, 55)


@pytest.fixture
def patch_datetime_now(monkeypatch):
    class mydatetime:
        @classmethod
        def now(cls):
            return FAKE_TIME

    monkeypatch.setattr(datetime, "datetime", mydatetime)

@pytest.mark.skip("API blocked")
def test_weather(mongo_collection: Collection, patch_datetime_now):
    database_service = WeatherService(mongo_collection)

    weather_manager = WeatherManager(
        location_provider=OpenMeteoLocationProvider(), weather_provider=OpenMeteo(), database_service=database_service
    )
    weather = weather_manager.get_weather(Frequency.DAY, "Berlin", "Germany")

    assert weather is not None

    weather2 = weather_manager.get_weather(Frequency.DAY, "Berlin", "Germany")

    assert weather == weather2

    in_collection = database_service.collection.find_one(
        {"date": datetime.datetime.now().strftime("%Y-%m-%d"), "city": "Berlin", "country": "Germany"}
    )

    assert in_collection is not None and in_collection.get("weather") is not None
