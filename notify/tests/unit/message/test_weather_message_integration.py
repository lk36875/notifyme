import pytest

from notify.models.event import Event
from notify.models.measurements import DayMeasurements, HourMeasurements
from notify.models.query_params import EventType, Frequency
from notify.services.weather_service import WeatherService
from notify.weather.location_provider import OpenMeteoLocationProvider
from notify.weather.message_builder import TextMessageBuilder
from notify.weather.weather_manager import WeatherManager
from notify.weather.weather_provider import OpenMeteo


@pytest.fixture
def events_hour():
    event = Event(event_type=EventType.PRECIPITATION, frequency=Frequency.HOUR, city="Berlin", country="Germany")
    event2 = Event(event_type=EventType.ALL, frequency=Frequency.HOUR, city="Berlin", country="Germany")
    event3 = Event(event_type=EventType.TEMPERATURE, frequency=Frequency.HOUR, city="Berlin", country="Germany")
    yield [event, event2, event3]

@pytest.mark.skip("API blocked")
def test_weather_hour(mongo_collection, events_hour: list[Event]):
    database_service = WeatherService(mongo_collection)
    weather_manager = WeatherManager(
        location_provider=OpenMeteoLocationProvider(), weather_provider=OpenMeteo(), database_service=database_service
    )
    weather: list[HourMeasurements] = weather_manager.get_weather(Frequency.HOUR, "Berlin", "Germany")  # type: ignore

    builder = TextMessageBuilder()

    for event in events_hour:
        assert builder.compose_hourly_message(weather, event.event_type) is not None


@pytest.fixture
def events_day():
    event = Event(event_type=EventType.PRECIPITATION, frequency=Frequency.DAY, city="Berlin", country="Germany")
    event2 = Event(event_type=EventType.ALL, frequency=Frequency.DAY, city="Berlin", country="Germany")
    event3 = Event(event_type=EventType.TEMPERATURE, frequency=Frequency.DAY, city="Berlin", country="Germany")
    yield [event, event2, event3]

@pytest.mark.skip("API blocked")
def test_weather_day(mongo_collection, events_day: list[Event]):
    database_service = WeatherService(mongo_collection)
    weather_manager = WeatherManager(
        location_provider=OpenMeteoLocationProvider(), weather_provider=OpenMeteo(), database_service=database_service
    )
    weather: list[DayMeasurements] = weather_manager.get_weather(Frequency.DAY, "Berlin", "Germany")  # type: ignore

    builder = TextMessageBuilder()

    for event in events_day:
        assert builder.compose_daily_message(weather, event.event_type) is not None
