"""
Script to fetch weather data for Orlando/Kissimmee via API.

- Uses a weather API (e.g., OpenWeatherMap, WeatherAPI).
- Stores results as JSON or CSV for further ETL processing.
"""
import requests
import json
import csv
from typing import List, Dict

# Example: OpenWeatherMap API endpoint and key (replace with your own)
API_KEY = "eea7d908c1ed788d45a284e1cb73f199"
BASE_URL = "https://api.openweathermap.org/data/2.5/weather"
LOCATIONS: List[Dict[str, float | str]] = [
    {"city": "Orlando", "lat": 28.5383, "lon": -81.3792},
    {"city": "Kissimmee", "lat": 28.2919, "lon": -81.4076},
]

def fetch_weather(lat: float, lon: float) -> Dict[str, str]:
    params: Dict[str, float | str] = {
        "lat": lat,
        "lon": lon,
        "appid": API_KEY,
        "units": "metric"
    }
    try:
        response = requests.get(BASE_URL, params=params)
        response.raise_for_status()
        data = response.json()
        return {
            "city": data.get("name", ""),
            "temp": str(data.get("main", {}).get("temp", "")),
            "weather": data.get("weather", [{}])[0].get("description", ""),
            "timestamp": str(data.get("dt", ""))
        }
    except Exception as e:
        print(f"Weather API fetch failed for {lat},{lon}: {e}")
        return {}

def save_weather_json(weather_data: List[Dict[str, str]], filename: str) -> None:
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(weather_data, f, ensure_ascii=False, indent=2)

def save_weather_csv(weather_data: List[Dict[str, str]], filename: str) -> None:
    if not weather_data:
        return
    keys = weather_data[0].keys()
    with open(filename, "w", newline='', encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(keys))
        writer.writeheader()
        writer.writerows(weather_data)

def main():
    weather_data: List[Dict[str, str]] = []
    for loc in LOCATIONS:
        result = fetch_weather(float(loc["lat"]), float(loc["lon"]))
        if result:
            weather_data.append(result)
    save_weather_json(weather_data, "weather_data.json")
    save_weather_csv(weather_data, "weather_data.csv")

if __name__ == "__main__":
    main()
