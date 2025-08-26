"""
Script to run MVP demand forecasting using Facebook Prophet.

- Loads historical bookings data from JSON (output of ETL pipeline).
- Trains Prophet model and forecasts future demand.
- Outputs forecast as JSON for dashboard/ETL use.
"""
from typing import List, Dict
import pandas as pd
from prophet import Prophet
import json

DATA_PATH = "historical_bookings.json"
FORECAST_OUTPUT = "demand_forecast.json"


def load_bookings(path: str) -> List[Dict[str, str]]:
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def prepare_df(bookings: List[Dict[str, str]]) -> pd.DataFrame:
    # Expect bookings to have 'date' and 'count' fields
    df = pd.DataFrame(bookings)
    df = df.rename(columns={"date": "ds", "count": "y"})
    df["ds"] = pd.to_datetime(df["ds"])
    df["y"] = pd.to_numeric(df["y"], errors="coerce").fillna(0)
    return df[["ds", "y"]]


def forecast_demand(df: pd.DataFrame, periods: int = 30) -> List[Dict[str, str]]:
    model = Prophet()
    model.fit(df)
    future = model.make_future_dataframe(periods=periods)
    forecast = model.predict(future)
    # Return only the forecasted dates and demand
    results = [
        {"date": str(row["ds"].date()), "demand": str(int(row["yhat"]))}
        for _, row in forecast.iterrows()
    ]
    return results


def save_forecast_json(forecast: List[Dict[str, str]], filename: str) -> None:
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(forecast, f, ensure_ascii=False, indent=2)


def main():
    bookings = load_bookings(DATA_PATH)
    if not bookings:
        print("No bookings data found.")
        return
    df = prepare_df(bookings)
    forecast = forecast_demand(df, periods=30)
    save_forecast_json(forecast, FORECAST_OUTPUT)
    print(f"Saved forecast to {FORECAST_OUTPUT}")


if __name__ == "__main__":
    main()
