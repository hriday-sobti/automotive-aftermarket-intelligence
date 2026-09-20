# Out-of-sample demand forecasting and holdout model evaluation.

from typing import Dict, Tuple
import numpy as np
import pandas as pd
from statsmodels.tsa.holtwinters import SimpleExpSmoothing


def evaluate_forecasting_models(
    demand_df: pd.DataFrame,
    split_date: str = "2025-09-01"
) -> Tuple[pd.DataFrame, Dict[str, float]]:
    """Fits Naive, 4-Week Moving Average, and Simple Exponential Smoothing models on training data,

    then evaluates predictions on a 17-week holdout period to measure out-of-sample accuracy.
    """
    df = demand_df.copy()
    df["week_start_date"] = pd.to_datetime(df["week_start_date"])

    train_df = df[df["week_start_date"] < pd.to_datetime(split_date)]
    test_df = df[df["week_start_date"] >= pd.to_datetime(split_date)]

    # Weekly aggregate demand per SKU
    train_agg = train_df.groupby(["sku_id", "week_start_date"])["estimated_latent_demand"].sum().reset_index()
    test_agg = test_df.groupby(["sku_id", "week_start_date"])["estimated_latent_demand"].sum().reset_index()

    sku_list = train_agg["sku_id"].unique()

    model_errors = {
        "naive": {"mae": [], "rmse": [], "mape": []},
        "sma_4": {"mae": [], "rmse": [], "mape": []},
        "exp_smooth": {"mae": [], "rmse": [], "mape": []}
    }

    forecast_records = []

    for sku in sku_list:
        sku_train = train_agg[train_agg["sku_id"] == sku].sort_values("week_start_date")
        sku_test = test_agg[test_agg["sku_id"] == sku].sort_values("week_start_date")

        if len(sku_train) < 8 or len(sku_test) == 0:
            continue

        train_series = sku_train["estimated_latent_demand"].values
        test_actuals = sku_test["estimated_latent_demand"].values
        test_dates = sku_test["week_start_date"].tolist()
        horizon = len(test_actuals)

        # 1. Naive persistence: project last observed value forward
        pred_naive = np.full(horizon, train_series[-1])

        # 2. 4-Week Simple Moving Average of trailing training weeks
        pred_sma = np.full(horizon, np.mean(train_series[-4:]))

        # 3. Simple Exponential Smoothing
        try:
            ses_model = SimpleExpSmoothing(train_series).fit(smoothing_level=0.3, optimized=False)
            pred_ses = ses_model.forecast(horizon)
        except Exception:
            pred_ses = pred_sma

        # Calculate error metrics across models
        for name, pred in [("naive", pred_naive), ("sma_4", pred_sma), ("exp_smooth", pred_ses)]:
            mae = np.mean(np.abs(test_actuals - pred))
            rmse = np.sqrt(np.mean((test_actuals - pred) ** 2))
            mape = np.mean(np.abs((test_actuals - pred) / np.maximum(test_actuals, 1.0))) * 100.0

            model_errors[name]["mae"].append(mae)
            model_errors[name]["rmse"].append(rmse)
            model_errors[name]["mape"].append(mape)

        for d_str, act, p_n, p_sma, p_ses in zip(test_dates, test_actuals, pred_naive, pred_sma, pred_ses):
            forecast_records.append({
                "sku_id": sku,
                "week_start_date": d_str.strftime("%Y-%m-%d"),
                "actual_demand": round(act, 1),
                "forecast_naive": round(p_n, 1),
                "forecast_sma4": round(p_sma, 1),
                "forecast_exp_smooth": round(p_ses, 1)
            })

    # Summary table across models
    summary = {}
    for m_name, errs in model_errors.items():
        summary[m_name] = {
            "MAE": round(float(np.mean(errs["mae"])), 2),
            "RMSE": round(float(np.mean(errs["rmse"])), 2),
            "MAPE_pct": round(float(np.mean(errs["mape"])), 2)
        }

    return pd.DataFrame(forecast_records), summary
