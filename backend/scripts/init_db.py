
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))
from backend.app.db import engine, Base

# Explicit imports so SQLAlchemy model classes register on Base.
import backend.app.models.user as _user
import backend.app.models.billing as _billing
import backend.app.models.lead as _lead
import backend.app.models.offer as _offer

# Reference the imported modules so linters consider them used (they register models on SQLAlchemy Base).
__all__ = ["_user", "_billing", "_lead", "_offer"]


def init_db():
    Base.metadata.create_all(bind=engine)


if __name__ == "__main__":
    init_db()
