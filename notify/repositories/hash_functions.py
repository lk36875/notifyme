from . import bcrypt


class BcryptHash:
    """
    Hashing functions using the bcrypt algorithm.

    This class provides two static methods for hashing and checking passwords using the bcrypt algorithm.
    The `hash` method takes a password string and returns a hashed password string.
    The `check` method takes a password string and a hashed password string. It Returns True if the password
    matches the hashed password, and False otherwise.

    Attributes:
        None
    """

    @staticmethod
    def hash(password: str) -> str:
        return bcrypt.generate_password_hash(password).decode("utf-8")

    @staticmethod
    def check(password: str, hashed_password: str) -> bool:
        return bcrypt.check_password_hash(hashed_password, password)
