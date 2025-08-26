from backend.scripts.fetch_competitor_prices import (
    main,
    fetch_booking_prices,
    fetch_booking_attractions,
    fetch_priceline_cars,
    fetch_tripadvisor_restaurants,
)


def test_individual_fetchers_mock():
    b = fetch_booking_prices(mock=True)
    assert isinstance(b, list)
    assert b and b[0].get('source') == 'booking'

    ba = fetch_booking_attractions(mock=True)
    assert isinstance(ba, list)
    assert ba and ba[0].get('source') == 'booking_attractions'

    pc = fetch_priceline_cars(mock=True)
    assert isinstance(pc, list)
    assert pc and pc[0].get('source') == 'priceline'

    tr = fetch_tripadvisor_restaurants(mock=True)
    assert isinstance(tr, list)
    assert tr and tr[0].get('source') == 'tripadvisor'


def test_main_returns_combined_items():
    items = main([])
    assert isinstance(items, list)
    # Expect at least one item from each mocked source
    sources = {i.get('source') for i in items}
    assert {'booking', 'booking_attractions', 'priceline', 'tripadvisor'}.issubset(sources)
