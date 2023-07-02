from dataclasses import dataclass


@dataclass
class HourMeasurements:
    """
    Represents the weather measurements for a single hour.

    This class represents the weather measurements for a single hour, including the date, the temperature,
    the humidity, the precipitation amount, and the probability of precipitation.

    Attributes:
        date: A string representing the date of the weather measurements.
        temperature: A tuple of two floats representing the minimum and maximum temperatures for the day.
        precipitation: A float representing the amount of precipitation for the day.
        precipitation_probability: A float representing the probability of precipitation for the day.
    """
    date: str
    temperature: float
    humidity: float
    precipitation: float
    precipitation_probability: float


@dataclass
class DayMeasurements:
    """
    Represents the weather measurements for a single day.

    This class represents the weather measurements for a single day, including the date, the temperature range
    (as a tuple of floats), the precipitation amount, and the probability of precipitation.
    The temperature range is represented as a tuple of two floats, where the first float is the minimum temperature
    and the second float is the maximum temperature.

    Attributes:
        date: A string representing the date of the weather measurements.
        temperature: A tuple of two floats representing the minimum and maximum temperatures for the day.
        precipitation: A float representing the amount of precipitation for the day.
        precipitation_probability: A float representing the probability of precipitation for the day.
    """

    date: str
    temperature: tuple[float, float]
    precipitation: float
    precipitation_probability: float

    def __post_init__(self):
        self.temperature = tuple(self.temperature)
