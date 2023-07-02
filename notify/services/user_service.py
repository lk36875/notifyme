import re
from typing import Protocol

from notify.app.logger import LoggerType, create_logger
from notify.exceptions.exceptions import InvalidUserDataException
from notify.models.user import User
from notify.repositories.user_repository import UserRepository

logger = create_logger(LoggerType.USER, "USER_SERVICE")


class HashClass(Protocol):
    def hash(self, password: str) -> str:
        ...

    def check(self, password: str, hashed_password: str) -> bool:
        ...


class UserService:
    """
    Service class for managing user data.

    This class provides methods for creating, updating, deleting, and retrieving user data.
    It uses a `UserRepository` object to interact with the database,
    and a `HashClass` object to hash and check passwords.

    Attributes:
        email_pattern: A regular expression pattern for validating email addresses.
        repository: A `UserRepository` object for interacting with the database.
        hash_provider: A `HashClass` object for hashing and checking passwords.
    """

    email_pattern = r"^[\w\.-]+@[\w\.-]+\.\w+$"

    def __init__(self, user_repository: UserRepository, hash_provider: HashClass) -> None:
        self.repository = user_repository
        self.hash_provider = hash_provider

    def create(self, data: dict) -> bool:
        """
        Create a new user.
        It also validates the data, hashes the password, and saves the user to the database.

        Args:
            data: A dictionary representing the data for the new user.

        Returns:
            A boolean value indicating whether the user was created successfully.
        """
        logger.info("Creating user")
        if not self._validate_user(data):
            try:
                data.pop("password")
            finally:
                logger.exception(f"Failed to create user {data}")
            raise InvalidUserDataException(data)

        password = self.hash_provider.hash(data["password"])
        user = User(username=data["username"], email=data["email"], password=password)

        try:
            self.repository.create(user)
            logger.info(f"Created user {user}")
            return True
        except Exception as e:
            logger.warning(f"Failed to create user {user}")
            logger.exception(e)
            return False

    def update(self, data: dict) -> bool:
        """
        Update a user.

        Args:
            data: A dictionary representing the data for the user to be updated.

        Returns:
            A boolean value indicating whether the user was updated successfully.
        """
        validate = {
            "username": self._validate_username,
            "password": self._validate_password,
            "email": self._validate_email,
        }
        user_id = data.pop("user_id")
        key, value = data.popitem()

        if key not in validate.keys() or not validate[key](value):
            logger.warning(f"Failed to update user {user_id} with {key}")
            return False

        try:
            logger.info(f"Updated user {user_id} with {key}")
            return True
        except Exception as e:
            logger.exception(e)
            return False

    def delete(self, user_id: int) -> bool:
        """
        Delete a user with the given ID.

        Args:
            user_id: An integer representing the ID of the user to be deleted.

        Returns:
            A boolean value indicating whether the user was deleted successfully.
        """
        try:
            self.repository.delete(user_id)
            logger.warning(f"Deleted user {user_id}")
            return True
        except Exception as e:
            logger.exception(e)
            return False

    def login(self, data: dict) -> bool:
        """
        Authenticate a user.

        This method authenticates a user with the given username and password.
        It retrieves the user from the database, and checks the password against the hashed password.

        Args:
            data: A dictionary representing the username and password of the user.

        Returns:
            A boolean value indicating whether the user was authenticated successfully.
        """
        if (username := data.get("username")) is None or (password := data.get("password")) is None:
            return False
        user = self.repository.get_by_name(username)
        if user is None:
            logger.info(f"User {username} failed to login")
            return False
        return self.hash_provider.check(password, user.password)

    def get_user(self, data: dict) -> User | None:
        """
        Retrieve a user.

        This method retrieves a user from the database based on the given data.
        It can retrieve a user by ID, username, or email address.

        Args:
            data: A dictionary representing the data for the user to be retrieved.

        Returns:
            A `User` object representing the retrieved user, or `None` if the user could not be found.
        """
        try:
            if (user_id := data.get("user_id")) is not None:
                return self.repository.get_by_id(user_id)
            if (username := data.get("username")) is not None:
                return self.repository.get_by_name(username)
            if (email := data.get("email")) is not None:
                return self.repository.get_by_email(email)
        except Exception as e:
            return None

    def get_users(self) -> list[User] | None:
        """
        Retrieve all users.

        Returns:
            A list of `User` objects representing the retrieved users, or `None` if the users could not be retrieved.
        """
        try:
            return self.repository.get_all()
        except Exception as e:
            logger.exception(e)
            return None

    def _validate_user(self, data: dict) -> bool:
        """
        Validate user data.

        This method validates user data by checking the username, password, and email address.

        Args:
            data: A dictionary representing the data for the user to be validated.

        Returns:
            A boolean value indicating whether the user data is valid.
        """
        email = data.get("email")
        password = data.get("password")
        username = data.get("username")

        return all((self._validate_email(email), self._validate_password(password), self._validate_username(username)))

    def _validate_username(self, username: str | None) -> bool:
        if username is None:
            return False
        return len(username) <= 30

    def _validate_password(self, password: str | None) -> bool:
        if password is None:
            return False
        return len(password) <= 120

    def _validate_email(self, email: str | None) -> bool:
        if email is None:
            return False
        return bool(re.match(self.email_pattern, email))
