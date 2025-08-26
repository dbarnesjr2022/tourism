import types
import pytest
from _pytest.monkeypatch import MonkeyPatch
from typing import Any, Callable

@pytest.fixture
def mock_stripe_checkout(monkeypatch: MonkeyPatch) -> Callable[..., types.SimpleNamespace]:
    def _fake_create(**kwargs: Any) -> types.SimpleNamespace:
        # mimic what your code expects to read:
        return types.SimpleNamespace(id="cs_test_123", url="https://stripe.test/checkout/cs_test_123")
    import stripe
    monkeypatch.setattr(stripe.checkout.Session, "create", _fake_create)
    return _fake_create

@pytest.fixture
def mock_stripe_webhook(monkeypatch: MonkeyPatch) -> Callable[[str, str, str], dict[str, Any]]:
    import stripe
    def _fake_construct_event(payload: str, sig_header: str, secret: str) -> dict[str, Any]:
        # return the Event object your handler expects
        return {
            "id": "evt_test_123",
            "type": "checkout.session.completed",
            "data": {"object": {"id": "cs_test_123", "customer": "cus_test_123"}}
        }
    monkeypatch.setattr(stripe.Webhook, "construct_event", _fake_construct_event)
    return _fake_construct_event
