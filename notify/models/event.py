from typing import Self

from notify.app.database import psql_db as db
from notify.models.query_params import EventType, Frequency


class Event(db.Model):
    """
    Represents an event that a user has subscribed to.

    Each event has a unique ID, an event type, a frequency (e.g. "day", "hour"), a city,
    a country and a user ID indicating which user the event belongs to.

    Attributes:
        event_id: An integer representing the unique ID of the event.
        event_type: An `EventType` object representing the type of the weather report.
        frequency: A `Frequency` object representing the frequency of report.
        city: A string representing the city.
        country: A string representing the country.
        user_id: An integer representing the ID of the user who subscribed to the event.
    """

    event_id = db.Column(db.Integer, primary_key=True)
    event_type = db.Column(db.Enum(EventType), nullable=False)
    frequency = db.Column(db.Enum(Frequency), nullable=False)
    city = db.Column(db.String(70), nullable=False)
    country = db.Column(db.String(70), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey("user.user_id"))

    __table_args__ = (db.UniqueConstraint("user_id", "frequency", "city", "country", name="unique_event"),)

    def __str__(self: Self) -> str:
        return (
            f"<Event#{self.event_id}: {self.city},  {self.country} - {self.event_type}, {self.frequency} for user"
            f" #{self.user_id}>"
        )

    def __repr__(self: Self) -> str:
        return self.__str__()

    def __eq__(self, other: Self) -> bool:
        if other is None:
            return False
        return (
            self.event_type == other.event_type
            and self.frequency == other.frequency
            and self.user_id == other.user_id
            and self.city == other.city
            and self.country == other.country
        )
