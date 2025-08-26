from backend.scripts import store_competitor_prices as store
from backend.app.models.competitor import CompetitorPrice
from backend.app.db import engine


import pathlib


def test_write_competitor_rows_creates_records(tmp_path: pathlib.Path) -> None:
    # ensure tables exist in the test DB
    CompetitorPrice.metadata.create_all(bind=engine)

    rows: list[dict[str, object]] = [
        {'source': 'booking', 'id': 'h1', 'price': 10},
        {'source': 'tripadvisor', 'id': 'r2', 'price': 5.5},
    ]

    n = store.write_competitor_rows(rows)
    assert n == 2

    # cleanup - drop table
    CompetitorPrice.metadata.drop_all(bind=engine)
