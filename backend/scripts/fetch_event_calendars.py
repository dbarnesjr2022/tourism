"""
Script to fetch Orlando/Kissimmee event calendars.

- Supports both API and web scraping approaches.
- Stores results as JSON or CSV for further ETL processing.
"""
import requests
from bs4 import BeautifulSoup
import json
import csv

# Example: API endpoint (replace with real one if available)
ORLANDO_API_URL = "https://api.orlando.com/events"
KISSIMMEE_API_URL = "https://api.experiencekissimmee.com/events"

# Example: Web page URLs (replace with real ones)
ORLANDO_EVENTS_PAGE = "https://www.visitorlando.com/events/"
KISSIMMEE_EVENTS_PAGE = "https://www.experiencekissimmee.com/events"


from typing import Any, List

def fetch_events_api(url: str) -> Any:
    """Fetch events from an API endpoint."""
    try:
        response = requests.get(url)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        print(f"API fetch failed for {url}: {e}")
        return []

def fetch_events_web(url: str) -> List[dict[str, str]]:
    """Scrape events from a web page."""
    try:
        response = requests.get(url)
        soup = BeautifulSoup(response.text, "html.parser")
        # TODO: Update selectors for actual event data
        events: List[dict[str, str]] = []
        for event in soup.select(".event-card"):  # type: ignore
            title_tag = event.select_one(".event-title")  # type: ignore
            date_tag = event.select_one(".event-date")  # type: ignore
            title = title_tag.get_text(strip=True) if title_tag else ""
            date = date_tag.get_text(strip=True) if date_tag else ""
            events.append({"title": title, "date": date})
        return events
    except Exception as e:
        print(f"Web scrape failed for {url}: {e}")
        return []

def save_events_json(events: List[dict[str, str]], filename: str) -> None:
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(events, f, ensure_ascii=False, indent=2)

def save_events_csv(events: List[dict[str, str]], filename: str) -> None:
    if not events:
        return
    keys = events[0].keys()
    with open(filename, "w", newline='', encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(keys))
        writer.writeheader()
        writer.writerows(events)

def main():
    # Try API first
    orlando_events = fetch_events_api(ORLANDO_API_URL)
    kissimmee_events = fetch_events_api(KISSIMMEE_API_URL)

    # If API fails, try web scraping
    if not orlando_events:
        orlando_events = fetch_events_web(ORLANDO_EVENTS_PAGE)
    if not kissimmee_events:
        kissimmee_events = fetch_events_web(KISSIMMEE_EVENTS_PAGE)

    # Save results
    save_events_json(orlando_events, "orlando_events.json")
    save_events_json(kissimmee_events, "kissimmee_events.json")
    save_events_csv(orlando_events, "orlando_events.csv")
    save_events_csv(kissimmee_events, "kissimmee_events.csv")

if __name__ == "__main__":
    main()
