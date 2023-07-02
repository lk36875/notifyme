import pytest

from notify.models.event import Event
from notify.models.measurements import DayMeasurements, HourMeasurements
from notify.models.query_params import EventType, Frequency
from notify.weather.message_builder import TextMessageBuilder

# Event, Weather


@pytest.fixture
def filled_day():
    event = Event(event_type=EventType.ALL, frequency=Frequency.DAY, city="Warsaw", country="Poland")
    weather = [
        DayMeasurements("2021-10-10", (1, 2), 2.1, 3),
        DayMeasurements("2021-10-11", (1, 123), 5.234, 3.24),
        DayMeasurements("2021-10-12", (-23, 23.42), 5.1523, 3),
    ]
    yield event, weather


@pytest.fixture
def filled_hour():
    event = Event(event_type=EventType.ALL, frequency=Frequency.HOUR, city="Warsaw", country="Poland")
    weather = [
        HourMeasurements("2021-10-12 12:12:12", -3.42, 5.1523, 3, 42),
        HourMeasurements("2021-10-11 22:23:12", 23, 5.234, 3.24, 42),
        HourMeasurements("2021-10-10 23:01:23", 12, 2.1, 3, 42),
    ]
    yield event, weather


def create_filled(event_type, event_frequency):
    event = Event(event_type=event_type, frequency=event_frequency, city="Warsaw", country="Poland")
    if event_frequency == Frequency.DAY:
        weather = [
            DayMeasurements("2021-10-10", (1, 2), 2.1, 3),
            DayMeasurements("2021-10-11", (1, 123), 5.234, 3.24),
            DayMeasurements("2021-10-12", (-23, 23.42), 5.1523, 3),
        ]
    else:
        weather = [
            HourMeasurements("2021-10-12 12:12:12", -3.42, 5.1523, 3, 42),
            HourMeasurements("2021-10-11 22:23:12", 23, 5.234, 3.24, 42),
            HourMeasurements("2021-10-10 23:01:23", 12, 2.1, 3, 42),
        ]
    return event, weather


def test_get_all_hour(filled_day):
    builder = TextMessageBuilder()
    message = builder.compose_message(*filled_day)
    expected_text = (
        "2021-10-10\nTemperature: min: 1°C; max: 2°C.\nPrecipitation of 2.1mm, with probability of"
        " 3%.\n2021-10-11\nTemperatur"
    )
    title, text = message
    assert title == "Weather report for Warsaw"
    assert text is not None and text.startswith(expected_text)


def test_get_all_day(filled_hour):
    builder = TextMessageBuilder()
    assert (
        builder.compose_message(*filled_hour)[1]
        == "Weather for 2021-10-12\n12:12:12\nTemperature: -3.42°C.\nHumidity of 5.1523%.\nPrecipitation of 3mm, with"
        " probability of 42%.\n\n22:23:12\nTemperature: 23°C.\nHumidity of 5.234%.\nPrecipitation of 3.24mm, with"
        " probability of 42%.\n\n23:01:23\nTemperature: 12°C.\nHumidity of 2.1%.\nPrecipitation of 3mm, with"
        " probability of 42%.\n\n"
    )


@pytest.mark.parametrize("event_type, event_frequency", [(et, ev) for et in EventType for ev in Frequency])
def test_get_combinations(event_type, event_frequency):
    builder = TextMessageBuilder()
    print(event_type, event_frequency)
    event, weather = create_filled(event_type, event_frequency)
    assert builder.compose_message(event, weather)
