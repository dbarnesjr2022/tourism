from typing import List, Dict, Union, Any

# Lightweight integration point for competitor prices. This imports the
# mock-first fetcher and derives a tiny feature (competitor_item_count)
# that the forecasting model would consume.
def _load_competitor_feature(mock: bool = True) -> Dict[str, Any]:
    try:
        from backend.scripts.fetch_competitor_prices import main as fetch_main
    except Exception:
        # If import fails (tests that isolate modules), return empty feature
        return {"competitor_item_count": 0}

    items = fetch_main([]) if mock else fetch_main(['--live'])
    return {"competitor_item_count": len(items)}


def predict_demand(start_date: str, end_date: str, property_id: int, *, mock_competitor: bool = True) -> List[Dict[str, Union[str, int]]]:
    """Predict demand between start_date and end_date for a property.

    This MVP function loads a tiny competitor-derived feature and returns
    mock predictions that incorporate the feature for demonstration.
    """
    # Load competitor-derived feature
    feat = _load_competitor_feature(mock=mock_competitor)
    competitor_count = feat.get('competitor_item_count', 0)

    # Simple mock logic: scale base demand by number of competitor items
    base_start = 120
    base_end = 95
    demand_start = max(10, base_start - competitor_count)
    demand_end = max(5, base_end - int(competitor_count / 2))

    return [
        {"date": start_date, "demand": demand_start, "competitor_item_count": competitor_count},
        {"date": end_date, "demand": demand_end, "competitor_item_count": competitor_count}
    ]
