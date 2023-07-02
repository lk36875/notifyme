import json
from unittest.mock import MagicMock

import pytest
import requests

from notify.weather.weather_provider import (OPEN_MATEO_CONFIG,
                                             DayMeasurements, HourMeasurements,
                                             OpenMeteo)


@pytest.fixture(scope="session")
def om_config():
    with open(OPEN_MATEO_CONFIG, "r") as f:
        config = json.load(f)
    yield config


def test_open_meteo_config_found(om_config):
    provider = OpenMeteo()
    assert provider.config == om_config


def test_format_url_hourly(om_config):
    provider = OpenMeteo()
    provider.config = om_config

    url = provider._format_url_hourly(52.23, 21.01)

    expected_url = (
        f"{om_config['base_url']}?latitude=52.23&longitude=21.01"
        "&hourly=temperature_2m,relativehumidity_2m,precipitation,"
        "precipitation_probability&timezone=auto&forecast_days=1"
    )
    assert url == expected_url


def test_format_url_daily(om_config):
    provider = OpenMeteo()
    provider.config = om_config

    url = provider._format_url_daily(52.23, 21.01)

    expected_url = (
        f"{om_config['base_url']}?latitude=52.23&longitude=21.01"
        "&daily=temperature_2m_max,temperature_2m_min,precipitation_sum,"
        "precipitation_probability_max&timezone=auto"
    )
    assert url == expected_url


def test_get_weather_daily(om_config, monkeypatch):
    mock_results = {
        "daily": {
            "time": ["2022-01-01"],
            "temperature_2m_min": [-5.0],
            "temperature_2m_max": [5.0],
            "precipitation_sum": [0.0],
            "precipitation_probability_max": [0.0],
        }
    }

    mock_get = MagicMock()
    mock_get.return_value = MagicMock(ok=True, json=lambda: mock_results)

    monkeypatch.setattr(requests, "get", mock_get)

    provider = OpenMeteo()
    provider.config = om_config
    measurements = provider.get_weather_daily(52.23, 21.01)

    expected_measurements = [
        DayMeasurements(date="2022-01-01", temperature=(-5.0, 5.0), precipitation=0.0, precipitation_probability=0.0)
    ]

    assert measurements == expected_measurements


def test_get_weather_hourly(om_config, monkeypatch):
    mock_results = {
        "hourly": {
            "time": ["2022-01-01T00:00:00Z", "2022-01-01T01:00:00Z"],
            "temperature_2m": [0.0, 1.0],
            "relativehumidity_2m": [50.0, 60.0],
            "precipitation": [0.0, 0.1],
            "precipitation_probability": [0.0, 0.2],
        }
    }
    mock_get = MagicMock()
    mock_get.return_value = MagicMock(ok=True, json=lambda: mock_results)

    monkeypatch.setattr(requests, "get", mock_get)

    provider = OpenMeteo()
    provider.config = om_config
    measurements = provider.get_weather_hourly(52.23, 21.01)

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
