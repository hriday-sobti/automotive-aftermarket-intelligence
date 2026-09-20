# Composite stockout risk scoring model.

from typing import Dict
import numpy as np
import pandas as pd


def compute_stockout_risk_model(
    sales_df: pd.DataFrame,
    inventory_df: pd.DataFrame,
    products_df: pd.DataFrame,
    distributors_df: pd.DataFrame,
    config: Dict
) -> pd.DataFrame:
    """Calculates a composite stockout risk score (0-100) per distributor-SKU combination

    by combining coverage days, sales pressure, lead times, volatility, and stockout history.
    """
    weights = config["inventory_risk"]["weights"]
    thresholds = config["inventory_risk"]["thresholds"]

    # 1. Latest Stock Position
    latest_dates = inventory_df.groupby(["distributor_id", "sku_id"])["date"].max().reset_index()
    latest_inv = inventory_df.merge(latest_dates, on=["distributor_id", "sku_id", "date"])

    # 2. Historical Stockout Frequency
    hist_stockouts = (
        inventory_df.groupby(["distributor_id", "sku_id"])["stockout_flag"]
        .agg(total_observations="count", stockout_count="sum")
        .reset_index()
    )
    hist_stockouts["stockout_rate"] = hist_stockouts["stockout_count"] / hist_stockouts["total_observations"]

    # 3. Demand Velocity & Volatility over trailing 90 days
    max_date = pd.to_datetime(sales_df["date"]).max()
    cutoff_date = (max_date - pd.Timedelta(days=90)).strftime("%Y-%m-%d")
    recent_sales = sales_df[sales_df["date"] >= cutoff_date]

    daily_sales = (
        recent_sales.groupby(["distributor_id", "sku_id", "date"])["quantity"]
        .sum()
        .reset_index()
    )

    demand_stats = (
        daily_sales.groupby(["distributor_id", "sku_id"])["quantity"]
        .agg(
            mean_daily_sales="mean",
            std_daily_sales="std",
            total_recent_sales="sum"
        )
        .reset_index()
    )
    demand_stats["std_daily_sales"] = demand_stats["std_daily_sales"].fillna(0.0)
    demand_stats["daily_sales_velocity"] = np.round(demand_stats["total_recent_sales"] / 90.0, 2)
    demand_stats["cv_demand"] = np.where(
        demand_stats["mean_daily_sales"] > 0,
        demand_stats["std_daily_sales"] / demand_stats["mean_daily_sales"],
        0.0
    )

    # Merge components
    m = latest_inv.merge(demand_stats, on=["distributor_id", "sku_id"], how="left")
    m = m.merge(hist_stockouts, on=["distributor_id", "sku_id"], how="left")
    m = m.merge(products_df[["sku_id", "product_name", "product_category", "standard_lead_time_days"]], on="sku_id", how="left")

    m["daily_sales_velocity"] = m["daily_sales_velocity"].fillna(0.1)
    m["mean_daily_sales"] = m["mean_daily_sales"].fillna(0.1)
    m["std_daily_sales"] = m["std_daily_sales"].fillna(0.0)
    m["cv_demand"] = m["cv_demand"].fillna(0.0)
    m["stockout_rate"] = m["stockout_rate"].fillna(0.0)

    # Days of Inventory (DOI)
    m["days_of_inventory"] = np.round(m["closing_stock"] / m["daily_sales_velocity"], 1)

    # 4. Normalized Component Scores (0 to 100)
    # Inventory Coverage Risk: high when DOI is less than 1.5x lead time
    coverage_ratio = m["days_of_inventory"] / (m["lead_time_days"] * 1.5)
    score_coverage = np.clip((1.0 - coverage_ratio) * 100.0, 0.0, 100.0)

    # Demand Pressure Risk: ratio of lead-time sales to stock on hand
    demand_ratio = (m["daily_sales_velocity"] * m["lead_time_days"]) / np.maximum(m["closing_stock"], 1)
    score_demand = np.clip(demand_ratio * 35.0, 0.0, 100.0)

    # Lead Time Exposure: scaled to 45-day max lead time
    score_lead_time = np.clip((m["lead_time_days"] / 45.0) * 100.0, 0.0, 100.0)

    # Volatility Risk: coefficient of variation scaled
    score_volatility = np.clip(m["cv_demand"] * 50.0, 0.0, 100.0)

    # Historical Stockout Rate
    score_hist_stockout = np.clip(m["stockout_rate"] * 250.0, 0.0, 100.0)

    m["score_coverage"] = np.round(score_coverage, 1)
    m["score_demand"] = np.round(score_demand, 1)
    m["score_lead_time"] = np.round(score_lead_time, 1)
    m["score_volatility"] = np.round(score_volatility, 1)
    m["score_hist_stockout"] = np.round(score_hist_stockout, 1)

    composite = (
        weights["inventory_coverage"] * score_coverage +
        weights["demand_pressure"] * score_demand +
        weights["lead_time_exposure"] * score_lead_time +
        weights["demand_volatility"] * score_volatility +
        weights["stockout_history"] * score_hist_stockout
    )
    m["stockout_risk_score"] = np.round(composite, 1)

    def classify_risk(score: float) -> str:
        if score >= thresholds["high"]:
            return "Critical"
        elif score >= thresholds["watch"]:
            return "High Risk"
        elif score >= thresholds["low"]:
            return "Watch"
        return "Low Risk"

    m["risk_category"] = m["stockout_risk_score"].apply(classify_risk)

    def get_primary_driver(row) -> str:
        drivers = {
            "Low Inventory Coverage": row["score_coverage"] * weights["inventory_coverage"],
            "High Demand Velocity": row["score_demand"] * weights["demand_pressure"],
            "Extended Supplier Lead Time": row["score_lead_time"] * weights["lead_time_exposure"],
            "High Demand Volatility": row["score_volatility"] * weights["demand_volatility"],
            "Recurring Stockout History": row["score_hist_stockout"] * weights["stockout_history"]
        }
        return max(drivers, key=drivers.get)

    m["primary_risk_driver"] = m.apply(get_primary_driver, axis=1)

    def get_recommendation(cat: str) -> str:
        if cat == "Critical":
            return "Emergency Expedited Reorder & Priority Logistics"
        elif cat == "High Risk":
            return "Accelerate Replenishment Review"
        elif cat == "Watch":
            return "Monitor Sell-Through & Queue Standard Batch"
        return "Adequate Inventory Buffer"

    m["recommended_action"] = m["risk_category"].apply(get_recommendation)

    return m[[
        "distributor_id", "sku_id", "product_name", "product_category", "closing_stock",
        "days_of_inventory", "daily_sales_velocity", "lead_time_days", "cv_demand",
        "stockout_risk_score", "risk_category", "primary_risk_driver", "recommended_action"
    ]].sort_values(by="stockout_risk_score", ascending=False).reset_index(drop=True)
