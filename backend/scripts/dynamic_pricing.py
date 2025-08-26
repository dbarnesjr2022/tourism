

from __future__ import annotations

from dataclasses import dataclass
from importlib.util import find_spec
from typing import Callable, Final, Protocol, Sequence, Tuple, cast

import numpy as np
from numpy.typing import NDArray
import pandas as pd

# ---------- Types ----------
FeatureMatrix = NDArray[np.float64]
TargetVector = NDArray[np.float64]

class OptimizeResultLike(Protocol):
    x: list[float]
    fun: float

class RegressorLike(Protocol):
    def fit(self, X: FeatureMatrix, y: TargetVector) -> RegressorLike: ...
    def predict(self, X: FeatureMatrix) -> NDArray[np.float64]: ...

# ---------- Optional skopt (single entrypoint wrapper) ----------
SKOPT_AVAILABLE: Final[bool] = find_spec("skopt") is not None
if SKOPT_AVAILABLE:
    from skopt import gp_minimize as _skopt_gp_minimize  # type: ignore[reportMissingImports]
else:
    _skopt_gp_minimize = None  # type: ignore[assignment]

@dataclass
class _FallbackRes:
    x: list[float]
    fun: float

def gp_minimize_compat(
    func: Callable[[list[float]], float],
    dimensions: Sequence[Tuple[float, float]],
    *,
    n_calls: int = 25,
    random_state: int | None = None,
) -> OptimizeResultLike:
    if _skopt_gp_minimize is not None:
        res = _skopt_gp_minimize(func, dimensions=list(dimensions), n_calls=n_calls, random_state=random_state)
        return cast(OptimizeResultLike, res)
    low, high = dimensions[0]
    xs = np.linspace(float(low), float(high), num=n_calls, dtype=float)
    best_x = float(xs[0])
    best_fun = float(func([best_x]))
    for p in xs[1:]:
        v = float(func([float(p)]))
        if v < best_fun:
            best_x, best_fun = float(p), v
    return _FallbackRes(x=[best_x], fun=best_fun)

def prepare_dataframe(
    df_prices: pd.DataFrame,
    df_features: pd.DataFrame,
    *,
    key: str = "listing_id",
    price_col: str = "price",
    target_col: str = "demand",
    extra_feature_cols: Sequence[str] = ("seasonality", "competitor_price", "weekday"),
) -> tuple[FeatureMatrix, TargetVector, list[str]]:
    merged = pd.merge(df_prices, df_features, how="inner", on=key)
    for col in (price_col, target_col, *extra_feature_cols):
        if col in merged.columns:
            merged[col] = pd.to_numeric(merged[col], errors="coerce")
    merged = merged.fillna(0.0)
    feature_cols: list[str] = [c for c in (price_col, *extra_feature_cols) if c in merged.columns]
    if price_col not in feature_cols and price_col in merged.columns:
        feature_cols.insert(0, price_col)
    if target_col not in merged.columns:
        raise ValueError(f"Expected '{target_col}' column for target.")
    X: FeatureMatrix = merged[feature_cols].to_numpy(dtype=np.float64)
    y: TargetVector = merged[target_col].to_numpy(dtype=np.float64)
    return X, y, feature_cols

def fit_model(X: FeatureMatrix, y: TargetVector) -> RegressorLike:
    from sklearn.linear_model import LinearRegression
    model = LinearRegression()
    model.fit(X, y)
    return cast(RegressorLike, model)

def predict_demand(model: RegressorLike, row2d: NDArray[np.float64]) -> float:
    pred = model.predict(row2d)
    return float(pred[0])

def make_objective(
    model: RegressorLike,
    base_features: NDArray[np.float64],
    price_col_idx: int,
) -> Callable[[list[float]], float]:
    def objective(params: list[float]) -> float:
        price: float = float(params[0])
        row = base_features.copy()
        row[price_col_idx] = price
        row2d: NDArray[np.float64] = row.reshape(1, -1)
        demand = predict_demand(model, row2d)
        revenue = price * max(demand, 0.0)
        return -revenue
    return objective

def optimize_price(
    objective: Callable[[list[float]], float],
    low: float,
    high: float,
    *,
    calls: int = 30,
    seed: int | None = 1337,
) -> tuple[float, float]:
    res = gp_minimize_compat(objective, dimensions=[(low, high)], n_calls=calls, random_state=seed)
    return float(res.x[0]), float(res.fun)

def main() -> None:
    df_prices = pd.DataFrame(
        {"listing_id": [1, 1, 1, 1, 1], "price": [80, 90, 100, 110, 120], "demand": [50, 45, 40, 32, 25]}
    )
    df_feat = pd.DataFrame(
        {"listing_id": [1, 1, 1, 1, 1], "seasonality": [1.0, 1.1, 0.9, 1.0, 1.05], "weekday": [1, 2, 3, 4, 5], "competitor_price": [95, 95, 105, 110, 115]}
    )
    X, y, cols = prepare_dataframe(df_prices, df_feat)
    model = fit_model(X, y)
    base: NDArray[np.float64] = np.mean(X, axis=0)
    try:
        price_col_idx = cols.index("price")
    except ValueError:
        raise RuntimeError("Feature 'price' not found in prepared feature columns.")
    objective = make_objective(model, base, price_col_idx)
    best_price, best_neg_revenue = optimize_price(objective, low=50.0, high=150.0)
    print({"skopt_used": SKOPT_AVAILABLE, "best_price": best_price, "estimated_revenue": -best_neg_revenue})

if __name__ == "__main__":
    main()
