# backend/tests/conftest.py
# pyright: reportUnknownVariableType=false
from __future__ import annotations

import types
from types import GeneratorType
import pytest
from sqlalchemy import create_engine
from sqlalchemy.engine import Engine
from sqlalchemy.orm import sessionmaker, Session
from fastapi.testclient import TestClient
from typing import Generator, Any

# Project imports (absolute, from the 'backend' package root)
from backend.app.main import app
from backend.app.db import Base, get_db
from backend.app.api.auth import get_current_user


# ---------- DATABASE ----------

@pytest.fixture(scope="session")
def engine() -> Generator[Engine, None, None]:
    """Single in‑memory SQLite engine for the whole test session."""
    url = "sqlite+pysqlite:///:memory:"
    eng = create_engine(url, connect_args={"check_same_thread": False})
    Base.metadata.create_all(bind=eng)
    try:
        yield eng
    finally:
        eng.dispose()


@pytest.fixture(scope="function")
def db(engine: Engine) -> Generator[Session, None, None]:
    """Fresh transaction/session per test."""
    TestingSessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.rollback()
        session.close()


@pytest.fixture(autouse=True)
def override_db_dependency(db: Session):
    """
    Inject our in‑memory DB into the app for all tests.
    If a test patches `app.api.billing.get_db`, delegate to that patched callable so
    the test's MagicMock or custom generator is honored.
    """
    from importlib import import_module

    def _get_db_override() -> Generator[Any, None, None]:
        # Check whether tests patched app.api.billing.get_db
        billing_mod = None
        try:
            billing_mod = import_module("app.api.billing")
        except Exception:
            billing_mod = None

        if billing_mod is not None:
            patched = getattr(billing_mod, "get_db", None)
            if patched is not None and patched is not get_db:
                # If patched returns a generator (like the real get_db), yield from it
                try:
                    rv = patched()
                except TypeError:
                    # Not callable as a function that returns the session — treat as value
                    yield patched
                    return

                # If the patched callable returned a generator-like object, yield from it.
                if isinstance(rv, GeneratorType) or hasattr(rv, "__next__"):
                    # pyright: ignore[reportUnknownVariableType]
                    for v in rv:
                        v_any: Any = v
                        yield v_any
                    return

                # Otherwise it's a plain value (e.g. MagicMock session). Yield it directly.
                yield rv
                return

        # Default behavior: yield the in-memory test session
        try:
            yield db
        finally:
            pass

    app.dependency_overrides[get_db] = _get_db_override
    # Also override the get_db referenced by the billing module (it may be a different
    # function object if tests patched or the route captured it at import time).
    try:
        import importlib
        billing_mod = importlib.import_module("backend.app.api.billing")
        billing_get_db = getattr(billing_mod, "get_db", None)
        if billing_get_db is not None and billing_get_db is not get_db:
            app.dependency_overrides[billing_get_db] = _get_db_override
    except Exception:
        pass
    try:
        yield
    finally:
        app.dependency_overrides.pop(get_db, None)


# ---------- AUTH ----------

def _fake_user():
    """Minimal user object that satisfies handlers (id + email)."""
    return types.SimpleNamespace(id=1, email="test@example.com")


@pytest.fixture
def fake_user() -> types.SimpleNamespace:
    """Provide a named fixture for tests that request `fake_user`."""
    return _fake_user()

@pytest.fixture(autouse=True)
def override_auth():
    """Make authenticated requests by default in tests (no 401)."""
    app.dependency_overrides[get_current_user] = _fake_user
    try:
        yield
    finally:
        app.dependency_overrides.pop(get_current_user, None)


# ---------- CLIENT ----------

@pytest.fixture(scope="function")
def client() -> TestClient:
    """FastAPI TestClient bound to the app with overrides applied."""
    return TestClient(app)
