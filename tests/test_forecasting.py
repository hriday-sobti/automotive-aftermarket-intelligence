# Unit tests for demand forecasting models, holdout evaluation splits, and error metrics.

import pytest
import numpy as np
import pandas as pd
from src.forecasting.forecast_engine import evaluate_forecasting_models


def make_synthetic_demand_series(n_weeks=104, base=100.0, trend=0.05, noise=5.0):
    dates = pd.date_range(start="2024-01-01", periods=n_weeks, freq="W-MON")
    records = []
    for idx, d in enumerate(dates):
        val = base * (1.0 + trend * (idx / 52.0)) + np.random.normal(0, noise)
        records.append({
            "week_start_date": d.strftime("%Y-%m-%d"),
            "sku_id": "SKU-TEST-01",
            "region_id": "REG-01",
            "vehicle_segment": "SEG-PV",
            "product_category": "Braking Systems",
            "seasonal_index": 1.0,
            "trend_factor": 1.0,
            "estimated_latent_demand": max(1.0, round(val, 1))
        })
    return pd.DataFrame(records)


def test_forecast_returns_expected_models():
    df = make_synthetic_demand_series(104)
    forecast_df, summary = evaluate_forecasting_models(df, split_date="2025-09-01")

    assert "naive" in summary
    assert "sma_4" in summary
    assert "exp_smooth" in summary
    for m in ["naive", "sma_4", "exp_smooth"]:
        assert summary[m]["MAE"] >= 0.0
        assert summary[m]["RMSE"] >= 0.0
        assert summary[m]["MAPE_pct"] >= 0.0


def test_forecast_holdout_dates_strictly_future():
    df = make_synthetic_demand_series(104)
    split_date = "2025-09-01"
    forecast_df, _ = evaluate_forecasting_models(df, split_date=split_date)

    assert (pd.to_datetime(forecast_df["week_start_date"]) >= pd.to_datetime(split_date)).all()


def test_forecast_metrics_error_ordering_on_flat_series():
    # If series is completely flat with zero noise, all models should have zero error
    dates = pd.date_range(start="2024-01-01", periods=104, freq="W-MON")
    records = [{
        "week_start_date": d.strftime("%Y-%m-%d"),
        "sku_id": "SKU-FLAT",
        "region_id": "REG-01",
        "vehicle_segment": "SEG-PV",
        "product_category": "Braking Systems",
        "seasonal_index": 1.0,
        "trend_factor": 1.0,
        "estimated_latent_demand": 100.0
    } for d in dates]
    df = pd.DataFrame(records)
    forecast_df, summary = evaluate_forecasting_models(df, split_date="2025-09-01")

    assert summary["naive"]["MAE"] == 0.0
    assert summary["sma_4"]["MAE"] == 0.0
    assert summary["exp_smooth"]["MAE"] == 0.0


@pytest.mark.parametrize("split_date", ["2025-06-01", "2025-08-01", "2025-10-01"])
def test_forecast_split_date_responsiveness(split_date):
    df = make_synthetic_demand_series(104)
    forecast_df, _ = evaluate_forecasting_models(df, split_date=split_date)
    assert forecast_df["week_start_date"].min() >= split_date


def test_forecast_multiple_skus():
    df1 = make_synthetic_demand_series(104)
    df2 = make_synthetic_demand_series(104)
    df2["sku_id"] = "SKU-TEST-02"
    combined = pd.concat([df1, df2], ignore_index=True)

    forecast_df, summary = evaluate_forecasting_models(combined, split_date="2025-09-01")
    assert set(forecast_df["sku_id"].unique()) == {"SKU-TEST-01", "SKU-TEST-02"}
