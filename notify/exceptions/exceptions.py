
class InvalidUserDataException(Exception):
    """User data is invalid."""
    def __init__(self, data: dict) -> None:
        self.message = f"Invalid user data: {data.get('username'), data.get('email')}"
        super().__init__(self.message)
