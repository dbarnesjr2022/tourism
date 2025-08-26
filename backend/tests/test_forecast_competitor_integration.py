from backend.app.services.forecast import predict_demand


def test_forecast_includes_competitor_feature():
    res = predict_demand('2025-09-01', '2025-09-02', property_id=123, mock_competitor=True)
    assert isinstance(res, list)
    assert res and 'competitor_item_count' in res[0]
    assert isinstance(res[0]['competitor_item_count'], int)
    assert int(res[0]['demand']) >= 0
