import datetime
from unittest.mock import MagicMock

from notify.celery_app.scheduled_events import MailScheduler
from notify.models.event import Event
from notify.models.measurements import DayMeasurements
from notify.models.query_params import EventType, Frequency
from notify.models.user import User


def test_mail_scheduler():
    # Create mock objects for the dependencies
    mock_sender = MagicMock()
    mock_database_users = MagicMock()
    mock_database_events = MagicMock()
    mock_weather_provider = MagicMock()
    mock_message_builder = MagicMock()

    event = Event(event_type=EventType.ALL, frequency=Frequency.DAY, city="London", country="UK")
    day_measurements = Event(event_type=EventType.ALL, frequency=Frequency.DAY), [
        DayMeasurements("2021-10-10", (1, 2), 2.1, 3),
        DayMeasurements("2021-10-11", (1, 123), 5.234, 3.24),
        DayMeasurements("2021-10-12", (-23, 23.42), 5.1523, 3),
    ]
    user = User(username="Alice", email="alice@example.com")

    # Set up the mock objects to return some test data
    mock_database_users.get_users.return_value = [user]
    mock_database_events.get_events_by_frequency.return_value = [event]

    mock_weather_provider.get_weather.return_value = day_measurements
    mock_message_builder.compose_message.return_value = ("Subject", "Message")

    # Create a MailScheduler object with the mock dependencies
    scheduler = MailScheduler(
        mock_sender,
        mock_database_users,
        mock_database_events,
        mock_weather_provider,
        mock_message_builder,
        Frequency.DAY,
    )

    # Call the send_mail method
    scheduler.run()

    # Check that the mock objects were called with the correct arguments
    mock_database_users.get_users.assert_called_once()
    mock_database_events.get_events_by_frequency.assert_called_once_with(user, Frequency.DAY)
    mock_weather_provider.get_weather.assert_called_once_with(Frequency.DAY, "London", "UK")
    mock_message_builder.compose_message.assert_called_once_with(event, day_measurements)
    mock_sender.send.assert_called_once_with("Subject", "Message", "alice@example.com")
