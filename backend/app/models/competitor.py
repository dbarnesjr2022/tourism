from __future__ import annotations

from datetime import datetime, timezone

from sqlalchemy import Column, Integer, String, Float, DateTime, JSON

from backend.app.db import Base


class CompetitorPrice(Base):
    __tablename__ = 'competitor_prices'

    id = Column(Integer, primary_key=True, index=True)
    source = Column(String, index=True, nullable=False)
    external_id = Column(String, index=True, nullable=True)
    # SQLAlchemy Column objects are dynamically typed; silence static checker here
    price = Column(Float, nullable=True)  # type: ignore[assignment]
    meta = Column(JSON, nullable=True)
    # Use timezone-aware UTC timestamps
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
