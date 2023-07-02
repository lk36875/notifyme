import pytest

from notify.weather.location_provider import (NominatimLocationProvider,
                                              OpenMeteoLocationProvider)


@pytest.mark.skip("API unavailable")
def test_get_location_found():
    provider = NominatimLocationProvider()
    lon, lat = provider.get_location("Warsaw", "Poland")  # type: ignore
    lon, lat = round(lon, 2), round(lat, 2)
    assert (lon, lat) == (52.23, 21.01)


@pytest.mark.skip("API unavailable")
def test_get_location_not_found():
    provider = NominatimLocationProvider()
    assert provider.get_location("my home", "Outer space") is None


@pytest.mark.skip("API unavailable")
def test_get_location_invalid_input():
    provider = NominatimLocationProvider()
    assert provider.get_location("", "") is None


@pytest.mark.skip("API blocked")
class TestOpenMeteo:
    @pytest.fixture(autouse=True)
    def open_mateo(self):
        self.provider = OpenMeteoLocationProvider()

    def test_get_location_found_om(self):
        location = self.provider.get_location("Warsaw", "Poland")
        assert location is not None

        lon, lat = location
        lon, lat = round(lon, 2), round(lat, 2)
        assert (lon, lat) == (52.23, 21.01)

    def test_get_location_not_found_om(self):
        assert self.provider.get_location("my home", "Outer space") is None

    def test_get_location_invalid_input_om(self):
        assert self.provider.get_location("", "") is None
