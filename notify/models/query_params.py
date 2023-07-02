"""
Helper enum types for query parameters.

This module defines two enum classes, `EventType` and `Frequency`, which are used as helper
types for query parameters in the NotifyMe API. `EventType` represents the type of event
that a user can subscribe to, and `Frequency` represents the frequency of an event.
They are also used in the `Event` model.
"""
from enum import Enum


class EventType(Enum):
    ALL = "all"
    TEMPERATURE = "temperature"
    PRECIPITATION = "precipitation"


class Frequency(Enum):
    HOUR = "hour"
    DAY = "day"
