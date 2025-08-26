import pytest

from backend.scripts import fetch_competitor_prices as fcp


def test_live_guard_no_api_key(monkeypatch: pytest.MonkeyPatch) -> None:
    """When RAPIDAPI_KEY is not set, live fetches should abort and return empty lists."""
    monkeypatch.delenv('RAPIDAPI_KEY', raising=False)

    assert fcp.fetch_booking_prices(mock=False) == []
    assert fcp.fetch_booking_attractions(mock=False) == []
    assert fcp.fetch_priceline_cars(mock=False) == []
    assert fcp.fetch_tripadvisor_restaurants(mock=False) == []
