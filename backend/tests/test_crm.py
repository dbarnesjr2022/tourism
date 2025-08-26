


from __future__ import annotations
import sys, pathlib
from fastapi import FastAPI

from fastapi.testclient import TestClient
from unittest.mock import MagicMock

# Add <backend> to sys.path so "app" resolves
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))

# Try common locations for the FastAPI instance
try:
    from backend.app.main import app as _fastapi_app  # preferred
except ModuleNotFoundError:
    try:
        from main import app as _fastapi_app  # fallback if run differently
    except ModuleNotFoundError as e:
        raise RuntimeError("Could not import FastAPI app; ensure backend/app/main.py exists.") from e

app: FastAPI = _fastapi_app
client: TestClient = TestClient(app)

def test_sync_lead():
    app.dependency_overrides = {}
    from backend.app.api.crm import get_current_user
    app.dependency_overrides[get_current_user] = lambda: MagicMock(id=1, email="test@example.com")
    client = TestClient(app)
    payload = {
        "name": "Test User",
        "email": "test@example.com",
        "phone": "1234567890",
        "source": "website"
    }
    response = client.post("/crm/sync", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "id" in data
    assert data["status"] == "synced"
    app.dependency_overrides = {}

def test_crm_webhook():
    client = TestClient(app)
    payload: dict[str, object] = {"event": "lead_created", "lead_id": 1}
    response = client.post("/crm/webhook", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["received"] is True
