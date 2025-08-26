"""
Persona Clustering Script for Tourism SaaS Platform

- Loads user/persona data from CSV or JSON
- Runs K-Means and DBSCAN clustering
- Outputs cluster assignments and summary statistics
- Designed for integration with dashboard and ML pipeline
"""
import pandas as pd
import numpy as np
from sklearn.cluster import KMeans, DBSCAN
from sklearn.preprocessing import StandardScaler
import json

DATA_PATH = "personas_data.json"  # Change to your actual data source
OUTPUT_PATH = "persona_clusters.json"


def load_data(path: str) -> pd.DataFrame:
    """Load persona/user data from JSON or CSV."""
    if path.endswith(".json"):
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        return pd.DataFrame(data)
    elif path.endswith(".csv"):
        return pd.read_csv(path)
    else:
        raise ValueError("Unsupported file format.")


def preprocess(df: pd.DataFrame) -> pd.DataFrame:
    """Select and scale numeric features for clustering."""
    # TODO: Adjust feature selection to your schema
    numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
    scaler = StandardScaler()
    scaled: np.ndarray = scaler.fit_transform(df[numeric_cols])
    df_scaled = pd.DataFrame(scaled, columns=numeric_cols)
    return df_scaled


def run_kmeans(X: pd.DataFrame, n_clusters: int = 4) -> np.ndarray:
    model = KMeans(n_clusters=n_clusters, random_state=42)
    labels: np.ndarray[np.int32] = model.fit_predict(X).astype(np.int32)
    return labels


def run_dbscan(X: pd.DataFrame, eps: float = 0.5, min_samples: int = 5) -> np.ndarray:
    model = DBSCAN(eps=eps, min_samples=min_samples)
    labels: np.ndarray[np.int32] = model.fit_predict(X).astype(np.int32)
    return labels


def main():
    df = load_data(DATA_PATH)
    X = preprocess(df)
    kmeans_labels = run_kmeans(X)
    dbscan_labels = run_dbscan(X)
    df["kmeans_cluster"] = kmeans_labels
    df["dbscan_cluster"] = dbscan_labels
    # Output cluster assignments and summary
    summary = {
        "kmeans": int(np.max(kmeans_labels) + 1),
        "dbscan_clusters": int(len(set(dbscan_labels)) - (1 if -1 in dbscan_labels else 0)),
        "noise_points": int(np.sum(dbscan_labels == -1)),
    }
    with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
        json.dump({"summary": summary, "data": df.to_dict(orient="records")}, f, ensure_ascii=False, indent=2)
    print(f"Saved persona clusters to {OUTPUT_PATH}")
    print("Summary:", summary)


if __name__ == "__main__":
    main()
