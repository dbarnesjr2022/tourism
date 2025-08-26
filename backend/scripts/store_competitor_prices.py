from __future__ import annotations

from typing import List, Dict, Any, cast
import os

from sqlalchemy.orm import Session

from backend.app.db import SessionLocal, engine
from backend.app.models.competitor import CompetitorPrice


def init_db() -> None:
    # create tables if they don't exist (use Alembic for production migrations)
    CompetitorPrice.metadata.create_all(bind=engine)


def write_competitor_rows(rows: List[Dict[str, Any]]) -> int:
    """Insert normalized competitor rows into the DB. Returns number inserted."""
    inserted = 0
    db: Session = SessionLocal()
    try:
        for r in rows:
            price_val = r.get('price')
            price_conv = None
            if price_val is not None:
                try:
                    price_conv = float(price_val)
                except Exception:
                    price_conv = None

            cp = CompetitorPrice(
                source=str(r.get('source') or ''),
                external_id=str(r.get('id') or r.get('external_id') or ''),
                price=price_conv,
                meta=r,
            )
            db.add(cp)
            inserted += 1
        db.commit()
    finally:
        db.close()
    return inserted


def main():
    # Simple CLI harness: read a JSON snapshot if present and persist it
    import json
    path = os.path.join(os.path.dirname(__file__), '..', 'competitor_prices.json')
    if os.path.exists(path):
        with open(path, 'r', encoding='utf-8') as f:
            rows = cast(List[Dict[str, Any]], json.load(f))
    else:
        rows = []

    init_db()
    n = write_competitor_rows(rows)
    print(f'Inserted {n} rows')


if __name__ == '__main__':
    main()
