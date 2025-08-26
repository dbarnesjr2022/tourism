from typing import Any, Dict, Optional

import pytest

import backend.scripts.fetch_competitor_prices as fcp


class DummyResponse:
    def __init__(self, data: Any, status_code: int = 200) -> None:
        self._data: Any = data
        self.status_code: int = status_code

    def raise_for_status(self) -> None:
        if not (200 <= self.status_code < 300):
            raise Exception('status')

    def json(self) -> Any:
        return self._data


class DummyClient:
    def __init__(self, *args: Any, **kwargs: Any) -> None:
        self._called: Dict[str, Any] = {}

    def get(self, url: str, params: Optional[Dict[str, Any]] = None, headers: Optional[Dict[str, str]] = None) -> DummyResponse:
        # record headers for assertions and return a dummy JSON payload
        self._called['url'] = url
        self._called['params'] = params
        self._called['headers'] = headers
        return DummyResponse({'ok': True, 'hotel_id': 123, 'price': 45})

    def __enter__(self) -> 'DummyClient':
        return self

    def __exit__(self, exc_type: Optional[type], exc: Optional[BaseException], tb: Optional[Any]) -> bool:
        return False


def test_live_get_by_env_uses_headers(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv('RAPIDAPI_KEY', 'testkey')
    monkeypatch.setenv('HOTELS_RAPIDAPI_HOST', 'hotels.p.rapidapi.com')

    # Patch httpx.Client to our DummyClient
    monkeypatch.setattr('backend.scripts.fetch_competitor_prices.httpx.Client', DummyClient)

    res = fcp.fetch_booking_prices(mock=False)
    assert isinstance(res, list)
    assert res and res[0].get('id') == 123
