from abc import ABC, abstractmethod


class Repository(ABC):
    """
    Abstract base class for data repositories.

    This abstract base class defines the interface for data repositories in the NotifyMe API.
    It defines two abstract methods, `create` and `delete`, which must be implemented by concrete subclasses.
    """
    @abstractmethod
    def create(self, data):
        ...

    @abstractmethod
    def delete(self, id):
        ...
