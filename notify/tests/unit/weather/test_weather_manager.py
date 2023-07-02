from datetime import datetime
from unittest.mock import MagicMock

import pytest

from notify.models.measurements import DayMeasurements, HourMeasurements
from notify.weather.weather_manager import (DatabaseService, LocationProvider,
                                            WeatherManager)
from notify.weather.weather_provider import OpenMeteo


@pytest.fixture
def mock_database_service():
    return MagicMock(spec=DatabaseService)


@pytest.fixture
def mock_location_provider():
    return MagicMock(spec=LocationProvider)


@pytest.fixture
def mock_weather_provider():
    return MagicMock(spec=OpenMeteo)


@pytest.fixture
def weather_manager(mock_database_service, mock_location_provider, mock_weather_provider):
    return WeatherManager(mock_weather_provider, mock_location_provider, mock_database_service)


def test_get_measurements_daily_from_database(mock_database_service, mock_location_provider, weather_manager):
    expected_measurements = [
        DayMeasurements(date="2022-01-01", temperature=(-5.0, 0.0), precipitation=0.0, precipitation_probability=0.0),
        DayMeasurements(date="2022-01-02", temperature=(-10.0, -5.0), precipitation=0.1, precipitation_probability=0.2),
    ]
    mock_database_service.get_weather.return_value = expected_measurements

    mock_location_provider.get_location.return_value = (52.23, 21.01)

    measurements = weather_manager._get_measurements("Warsaw", "Poland", Frequency.DAY)

    assert measurements == expected_measurements
    mock_database_service.get_weather.assert_called_once_with(
        Frequency.DAY, "Warsaw", "Poland", datetime.now().strftime("%Y-%m-%d")
    )


def test_get_measurements_daily_from_provider(
    mock_database_service, mock_location_provider, mock_weather_provider, weather_manager
):
    mock_results = [
        DayMeasurements(date="2022-01-01", temperature=(-5.0, 0.0), precipitation=0.0, precipitation_probability=0.0),
        DayMeasurements(date="2022-01-02", temperature=(-10.0, -5.0), precipitation=0.1, precipitation_probability=0.2),
    ]
    mock_weather_provider.get_weather_daily.return_value = mock_results

    mock_database_service.get_weather.return_value = None

    mock_location_provider.get_location.return_value = (52.23, 21.01)

    measurements = weather_manager._get_measurements("Warsaw", "Poland", Frequency.DAY)

    expected_measurements = [
        DayMeasurements(date="2022-01-01", temperature=(-5.0, 0.0), precipitation=0.0, precipitation_probability=0.0),
        DayMeasurements(date="2022-01-02", temperature=(-10.0, -5.0), precipitation=0.1, precipitation_probability=0.2),
    ]

    assert measurements == expected_measurements
    mock_database_service.get_weather.assert_called_once_with(
        Frequency.DAY, "Warsaw", "Poland", datetime.now().strftime("%Y-%m-%d")
    )
    mock_database_service.store_weather.assert_called_once_with(Frequency.DAY, "Warsaw", "Poland", mock_results)


def test_get_measurements_hourly_from_database(mock_database_service, mock_location_provider, weather_manager):
    expected_measurements = [
        HourMeasurements(
            date="2022-01-01T00:00:00Z",
            temperature=0.0,
            humidity=50.0,
            precipitation=0.0,
            precipitation_probability=0.0,
        ),
        HourMeasurements(
            date="2022-01-01T01:00:00Z",
            temperature=1.0,
            humidity=60.0,
            precipitation=0.1,
            precipitation_probability=0.2,
        ),
    ]

    mock_database_service.get_weather.return_value = expected_measurements

    mock_location_provider.get_location.return_value = (52.23, 21.01)

    measurements = weather_manager._get_measurements("Warsaw", "Poland", Frequency.HOUR)

    assert measurements == expected_measurements
    mock_database_service.get_weather.assert_called_once_with(
        Frequency.HOUR, "Warsaw", "Poland", datetime.now().strftime("%Y-%m-%d")
    )


def test_get_measurements_hourly_from_provider(
    mock_database_service, mock_location_provider, mock_weather_provider, weather_manager
):
    mock_results = [
        HourMeasurements(
            date="2022-01-01T00:00:00Z",
            temperature=0.0,
            humidity=50.0,
            precipitation=0.0,
            precipitation_probability=0.0,
        ),
        HourMeasurements(
            date="2022-01-01T01:00:00Z",
            temperature=1.0,
            humidity=60.0,
            precipitation=0.1,
            precipitation_probability=0.2,
        ),
    ]
    mock_weather_provider.get_weather_hourly.return_value = mock_results

    mock_database_service.get_weather.return_value = None

    mock_location_provider.get_location.return_value = (52.23, 21.01)

    measurements = weather_manager._get_measurements("Warsaw", "Poland", Frequency.HOUR)

    expected_measurements = [
        HourMeasurements(
            date="2022-01-01T00:00:00Z",
            temperature=0.0,
            humidity=50.0,
            precipitation=0.0,
            precipitation_probability=0.0,
        ),
        HourMeasurements(
            date="2022-01-01T01:00:00Z",
            temperature=1.0,
            humidity=60.0,
            precipitation=0.1,
            precipitation_probability=0.2,
        ),
    ]

    assert measurements == expected_measurements
    mock_database_service.get_weather.assert_called_once_with(
        Frequency.HOUR, "Warsaw", "Poland", datetime.now().strftime("%Y-%m-%d")
    )
    mock_database_service.store_weather.assert_called_once_with(Frequency.HOUR, "Warsaw", "Poland", mock_results)


from notify.models.query_params import Frequency
