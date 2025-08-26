"""
Script to ingest historical bookings (CSV/API).

- Loads booking data from CSV files or an API endpoint.
- Prepares data for ETL and storage in PostgreSQL or other DB.
"""
import csv
import json
from typing import List, Dict

# Example CSV file path
CSV_PATH = "historical_bookings.csv"
# Example API endpoint (replace with real one)
API_URL = "https://api.example.com/bookings"


def ingest_from_csv(path: str) -> List[Dict[str, str]]:
    bookings: List[Dict[str, str]] = []
    try:
        with open(path, newline='', encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                bookings.append(dict(row))
    except Exception as e:
        print(f"CSV ingest failed: {e}")
    return bookings

def ingest_from_api(url: str) -> List[Dict[str, str]]:
    # TODO: Implement real API call
    print(f"Fetching bookings from API: {url}")
    return []

def save_bookings_json(bookings: List[Dict[str, str]], filename: str) -> None:
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(bookings, f, ensure_ascii=False, indent=2)

def main():
    # Try CSV first
    bookings = ingest_from_csv(CSV_PATH)
    # If CSV fails or is empty, try API
    if not bookings:
        bookings = ingest_from_api(API_URL)
    save_bookings_json(bookings, "historical_bookings.json")
    # TODO: Add logic to store in PostgreSQL or other DB

if __name__ == "__main__":
    main()
