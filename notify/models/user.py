from typing import Self

from notify.app.database import psql_db as db


class User(db.Model):
    """
    Represents a user for SQLAlchemy table.

    Each user has a unique ID, a username, a password, and an email address.
    Users can subscribe to events and receive weather reports for those events.

    Attributes:
        user_id: An integer representing the unique ID of the user.
        username: A string representing the username of the user.
        password: A string representing the password of the user. Password should be hashed before storing.
        email: A string representing the email address of the user.
        events: A list of `Event` objects representing the events that the user has subscribed to.
    """

    user_id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(30), index=True, unique=True)
    password = db.Column(db.String(120))
    email = db.Column(db.String(120), index=True, unique=True)

    events = db.relationship("Event", backref="user")

    def __str__(self) -> str:
        return f"<User#{self.user_id}| {self.username}, {self.email}>"

    def __eq__(self, other: Self) -> bool:
        return self.user_id == other.user_id and self.username == other.username and self.email == other.email
