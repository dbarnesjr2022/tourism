"""
Script to scrape OTA competitor prices (Booking, Expedia, Airbnb).

- Provides template functions for each OTA.
- Results can be saved as JSON/CSV for ETL.
- Note: Most OTAs require API access or advanced scraping (anti-bot measures).
"""
import json
from typing import List, Dict, Optional, Any, cast
import argparse
import os
import time
import random
import threading
import logging

import httpx

# Repo-local cache path for mocked raw responses
CACHE_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), '..', 'data', 'raw', 'rapidapi')

# Basic logger
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


def _rapidapi_headers(host_env_key: str) -> Dict[str, str]:
    """Build RapidAPI headers from env. Expects RAPIDAPI_KEY and per-host env var."""
    key = os.getenv('RAPIDAPI_KEY')
    host = os.getenv(host_env_key)
    headers: Dict[str, str] = {}
    if key:
        headers['x-rapidapi-key'] = key
    if host:
        headers['x-rapidapi-host'] = host
    return headers


def _live_get(base_host: Optional[str], path: str = '/', params: Optional[Dict[str, str]] = None, retries: int = 3, backoff: float = 0.5, headers: Optional[Dict[str, str]] = None) -> Optional[Dict[str, Any]]:
    """Make a simple GET request to a RapidAPI host with retries.

    This function is intentionally minimal — the project currently uses a mock-first
    approach. Live calls are only attempted when `--live` is supplied.
    """
    if not base_host:
        logger.warning("No host provided for live fetch")
        return None

    url = base_host
    # allow callers to pass full URL or host; normalize to URL
    if not base_host.startswith('http'):
        url = f"https://{base_host}{path}"
    else:
        url = base_host + path

    # Prefer explicit headers passed by caller (so callers can choose the correct
    # per-provider env var). Fall back to a generic RAPIDAPI_KEY check.
    if headers is None:
        headers = _rapidapi_headers('RAPIDAPI_HOST')
    if not headers.get('x-rapidapi-key'):
        logger.warning('RAPIDAPI_KEY not set; aborting live call')
        return None

    for attempt in range(1, retries + 1):
        try:
            with httpx.Client(timeout=10.0) as c:
                resp = c.get(url, params=params or {}, headers=headers)
                resp.raise_for_status()
                return resp.json()
        except Exception as exc:
            logger.warning('live GET failed (attempt %d/%d) %s: %s', attempt, retries, url, exc)
            if attempt < retries:
                # exponential backoff with small jitter
                delay = backoff * (2 ** (attempt - 1)) + random.uniform(0, 0.1)
                time.sleep(delay)
            else:
                logger.error('exhausted retries for %s', url)
                return None


def _live_get_by_env(host_env_key: str, path: str = '/', params: Optional[Dict[str, str]] = None, retries: int = 3, backoff: float = 0.5) -> Optional[Dict[str, Any]]:
    """Derive host and headers from environment and perform a live GET.

    This helper centralizes per-provider RapidAPI env usage so callers only
    need to pass the env var name (for example 'HOTELS_RAPIDAPI_HOST').
    """
    host = os.getenv(host_env_key)
    if not host:
        logger.warning('host env %s not set; skipping live call', host_env_key)
        return None
    headers = _rapidapi_headers(host_env_key)
    # Respect per-provider minimum interval to avoid vendor throttling.
    _respect_rate_limit(host_env_key)
    return _live_get(host, path=path, params=params, retries=retries, backoff=backoff, headers=headers)


# Simple per-provider rate limiting state
_last_call_at: Dict[str, float] = {}
_rate_limit_lock = threading.Lock()


def _respect_rate_limit(host_env_key: str) -> None:
    """Sleep if the last call to this provider was too recent.

    The minimum interval can be configured with `RAPIDAPI_MIN_INTERVAL_SECONDS` env var
    (defaults to 0.2s). This is intentionally conservative and easy to test.
    """
    min_interval = float(os.getenv('RAPIDAPI_MIN_INTERVAL_SECONDS', '0.2'))
    now = time.time()
    with _rate_limit_lock:
        last = _last_call_at.get(host_env_key)
        if last is None:
            _last_call_at[host_env_key] = now
            return
        elapsed = now - last
        if elapsed < min_interval:
            to_sleep = min_interval - elapsed
            logger.info('rate limiting %s sleeping %.3fs', host_env_key, to_sleep)
            time.sleep(to_sleep)
        _last_call_at[host_env_key] = time.time()


def _read_cached(cache_key: str) -> Optional[Dict[str, Any]]:
    path = os.path.join(CACHE_DIR, f"{cache_key}.json")
    if not os.path.exists(path):
        return None
    with open(path, 'r', encoding='utf-8') as f:
        return json.load(f)


def fetch_booking_prices(mock: bool = True) -> List[Dict[str, Any]]:
    """Fetch booking prices (mock-first).

    When `mock` is True this reads a cached JSON at
    `data/raw/rapidapi/hotels_photos_1178275040.json` and returns a
    small normalized shape for tests.
    """
    if mock:
        raw = _read_cached('hotels_photos_1178275040')
        if not raw:
            return []
        # Normalize to a simple price-like shape for ETL tests
        return [{
            'source': 'booking',
            'id': raw.get('hotel_id'),
            'price': None,
        }]

    # Minimal live implementation using RapidAPI host from env. This will only run
    # when the caller passes --live. It uses _live_get and returns a similar
    # normalized shape to the mock response.
    raw = _live_get_by_env('HOTELS_RAPIDAPI_HOST', path='/hotels/list', params={'locale': 'en_US'})
    if not raw:
        return []
    # Attempt to extract hotel id / price where available
    hotel_id = raw.get('hotel_id') or raw.get('id')
    price = None
    # Some RapidAPI hotel endpoints nest rates under 'rates' or 'price'
    if isinstance(raw.get('price'), (int, float, str)):
        price = raw.get('price')
    else:
        rates_obj = raw.get('rates')
        # Narrow dynamic types for the type-checker: ensure rates_obj is a list
        # and cast it to List[Any] so subsequent indexing is typed.
        if isinstance(rates_obj, list):
            rates_list = cast(List[Any], rates_obj)
            if len(rates_list) > 0:
                first = rates_list[0]
                if isinstance(first, dict):
                    first_map = cast(Dict[str, Any], first)
                    price = first_map.get('price')
    return [{'source': 'booking', 'id': hotel_id, 'price': price}]


def fetch_booking_attractions(mock: bool = True) -> List[Dict[str, Any]]:
    if mock:
        raw = _read_cached('booking_attractions_PRFZkGSVnM5d')
        if not raw:
            return []
        return [{
            'source': 'booking_attractions',
            'id': raw.get('attraction_id'),
            'name': raw.get('name'),
        }]

    raw = _live_get_by_env('BOOKING_RAPIDAPI_HOST', path='/attractions/list')
    if not raw:
        return []
    return [{'source': 'booking_attractions', 'id': raw.get('attraction_id'), 'name': raw.get('name')}]


def fetch_priceline_cars(mock: bool = True) -> List[Dict[str, Any]]:
    if mock:
        raw = _read_cached('priceline_cars_Seattle')
        if not raw:
            return []
        # type hints for the type checker
        raw_map: Dict[str, Any] = raw  # type: ignore
        items: List[Dict[str, Any]] = []
        for c_any in raw_map.get('cars', []):
            c: Dict[str, Any] = c_any  # type: ignore
            items.append({'source': 'priceline', 'city': raw_map.get('city'), 'price_per_day': c.get('price_per_day')})
        return items

    raw = _live_get_by_env('PRICELINE_RAPIDAPI_HOST', path='/cars/search', params={'city': 'Seattle'})
    if not raw:
        return []
    items: List[Dict[str, Any]] = []
    for c_any in raw.get('cars', []):
        c: Dict[str, Any] = c_any  # type: ignore
        items.append({'source': 'priceline', 'city': raw.get('city'), 'price_per_day': c.get('price_per_day')})
    return items


def fetch_tripadvisor_restaurants(mock: bool = True) -> List[Dict[str, Any]]:
    if mock:
        raw = _read_cached('tripadvisor_restaurants_304554')
        if not raw:
            return []
        return [{'source': 'tripadvisor', 'id': raw.get('restaurant_id'), 'name': raw.get('name')}]

    raw = _live_get_by_env('TRIPADVISOR_RAPIDAPI_HOST', path='/restaurants/list')
    if not raw:
        return []
    return [{'source': 'tripadvisor', 'id': raw.get('restaurant_id'), 'name': raw.get('name')}]


def save_prices_json(prices: List[Dict[str, str]], filename: str) -> None:
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(prices, f, ensure_ascii=False, indent=2)


def main(argv: Optional[List[str]] = None) -> List[Dict[str, str]]:
    parser = argparse.ArgumentParser()
    parser.add_argument('--live', action='store_true', help='Run live (non-mock) fetches')
    args = parser.parse_args(argv)
    mock = not args.live

    all_prices: List[Dict[str, str]] = []
    all_prices += fetch_booking_prices(mock=mock)
    all_prices += fetch_booking_attractions(mock=mock)
    all_prices += fetch_priceline_cars(mock=mock)
    all_prices += fetch_tripadvisor_restaurants(mock=mock)

    # Persist a JSON snapshot for ETL review
    save_prices_json(all_prices, os.path.join(os.path.dirname(__file__), '..', 'competitor_prices.json'))
    return all_prices


if __name__ == "__main__":
    results = main()
    print(f"Fetched {len(results)} competitor items")
