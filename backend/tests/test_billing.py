from unittest.mock import patch, MagicMock
from typing import Any, Dict
from fastapi.testclient import TestClient


def test_create_checkout_dev_fallback(client: TestClient):
    # Ensure env defaults in code cause dev fallback when STRIPE_SECRET not set.
    resp = client.post("/billing/create-checkout")
    assert resp.status_code == 200
    body = resp.json()
    assert body.get("mock") is True
    assert "checkout_url" in body


@patch("app.api.billing.stripe")
@patch("app.api.billing.get_db")
def test_create_checkout_calls_stripe_and_persists(mock_get_db: Any, mock_stripe: Any, client: TestClient, fake_user: MagicMock):
    # Mock DB session with minimal API used in handler
    db = MagicMock()
    # existing customer query returns None
    db.query.return_value.filter.return_value.first.return_value = None
    mock_get_db.return_value = db

    # `client` fixture provides TestClient with fake_user dependency injected

    # Mock stripe.Customer.create and checkout.Session.create
    mock_customer = {"id": "cus_test_123"}
    mock_stripe.Customer.create.return_value = mock_customer
    mock_session = MagicMock()
    mock_session.url = "https://stripe.test/checkout"
    mock_session.id = "cs_test_123"
    # Make checkout.Session.create return an object
    mock_stripe.checkout.Session.create.return_value = mock_session

    # Ensure the billing module uses Stripe path (it reads these at import-time)
    old_secret: str | None = getattr(__import__("app.api.billing", fromlist=["billing"]), "STRIPE_SECRET", None)
    old_price: str | None = getattr(__import__("app.api.billing", fromlist=["billing"]), "STRIPE_PRICE_ID", None)
    import backend.app.api.billing as billing
    try:
        billing.STRIPE_SECRET = "sk_test_x"
        billing.STRIPE_PRICE_ID = "price_123"
        resp = client.post("/billing/create-checkout")
        # Should return a checkout url
        assert resp.status_code == 200
        data = resp.json()
        assert data["checkout_url"] == "https://stripe.test/checkout"
        assert data["session_id"] == "cs_test_123"
    finally:
        # restore module constants
        billing.STRIPE_SECRET = old_secret
        billing.STRIPE_PRICE_ID = old_price


def test_webhook_accepts_raw_json_and_returns_received(client: TestClient):
    payload: Dict[str, Any] = {
        "type": "checkout.session.completed",
        "data": {"object": {"customer": "cus_1", "subscription": "sub_1"}},
    }
    resp = client.post("/billing/webhook", json=payload)
    assert resp.status_code == 200
    assert resp.json() == {"received": True}
