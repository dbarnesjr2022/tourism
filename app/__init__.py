# Lightweight compatibility package so tests that import `app.*` still work.
# This module maps the name `app` to the actual package `backend.app` at import time.
import importlib
import sys

_backend_app = importlib.import_module("backend.app")
# Expose backend.app as top-level 'app' package
sys.modules["app"] = _backend_app

# Also expose subpackages if needed
try:
    importlib.import_module("backend.app.api")
    importlib.import_module("backend.app.models")
except Exception:
    pass
from importlib import import_module as _import_module
import sys as _sys
try:
    _sys.modules["app.api"] = _import_module("backend.app.api")
    _sys.modules["app.models"] = _import_module("backend.app.models")
except Exception:
    pass
