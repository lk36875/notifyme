from notify.app.database import mongo_db as mongo
from notify.app.database import psql_db as psql
from notify.mail.mail_sender import MailSender
from notify.models.query_params import Frequency
from notify.repositories.event_repository import EventRepository
from notify.repositories.hash_functions import BcryptHash
from notify.repositories.user_repository import UserRepository
from notify.services.event_service import EventService
from notify.services.user_service import UserService
from notify.services.weather_service import WeatherService
from notify.weather.location_provider import OpenMeteoLocationProvider
from notify.weather.message_builder import TextMessageBuilder
from notify.weather.weather_manager import WeatherManager
from notify.weather.weather_provider import OpenMeteo

from .scheduled_events import MailScheduler


def setup_scheduled_events(frequency: Frequency):
    """
    This function initializes the services and providers needed for scheduled events, including the mail sender,
    user service, event service, MongoDB database service, and weather manager.
    These services and providers are used to send weather reports to users on a periodic basis.

    Args:
        frequency: A `Frequency` object indicating the frequency of the weather reports.

    Returns:
        A `MailScheduler` object that schedules weather reports to be sent to users on a periodic basis.
    """
    mail_sender = MailSender()

    session = psql.session
    user_service = UserService(UserRepository(session), BcryptHash())

    event_service = EventService(EventRepository(session))

    collection = "weather_collection"
    mongo_db = mongo.db
    if mongo_db is None:
        raise Exception("MongoDB is not available.")

    db_service = WeatherService(mongo_db[collection])

    weather_manager = WeatherManager(
        location_provider=OpenMeteoLocationProvider(), weather_provider=OpenMeteo(), database_service=db_service
    )

    message_builder = TextMessageBuilder()

    ms = MailScheduler(mail_sender, user_service, event_service, weather_manager, message_builder, frequency)
    return ms
