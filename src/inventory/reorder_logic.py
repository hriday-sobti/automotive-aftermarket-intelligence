"""Inventory safety stock, reorder point, and recommended purchase order logic.

Rigorous mathematical formulation:
1. Safety Stock (SS):
   SS = Z * sigma_D * sqrt(L)
   where Z = 1.645 (95% Cycle Service Level), sigma_D is daily demand standard deviation, L is lead time in days.
2. Reorder Point (ROP):
   ROP = (D_avg * L) + SS
   where D_avg is average daily demand rate.
3. Recommended Order Quantity (ROQ):
   ROQ = max(0, ceil(ROP - Current_Stock + Forward_Demand_Buffer))
"""

from typing import Dict
import numpy as np
import pandas as pd


def compute_reorder_parameters(
    sales_df: pd.DataFrame,
    inventory_df: pd.DataFrame,
    products_df: pd.DataFrame,
    service_level_z: float = 1.645
) -> pd.DataFrame:
    """Compute mathematically defensible inventory replenishment thresholds."""
    # Current stock position
    latest_dates = inventory_df.groupby(["distributor_id", "sku_id"])["date"].max().reset_index()
    latest_inv = inventory_df.merge(latest_dates, on=["distributor_id", "sku_id", "date"])

    # Historical 90-day daily demand distribution
    max_date = pd.to_datetime(sales_df["date"]).max()
    cutoff_date = (max_date - pd.Timedelta(days=90)).strftime("%Y-%m-%d")
    recent = sales_df[sales_df["date"] >= cutoff_date]

    daily = (
        recent.groupby(["distributor_id", "sku_id", "date"])["quantity"]
        .sum()
        .reset_index()
    )

    stats = (
        daily.groupby(["distributor_id", "sku_id"])["quantity"]
        .agg(
            d_avg="mean",
            d_std="std",
            total_90d="sum"
        )
        .reset_index()
    )
    stats["d_std"] = stats["d_std"].fillna(0.0)

    merged = latest_inv.merge(stats, on=["distributor_id", "sku_id"], how="left")
    merged = merged.merge(products_df[["sku_id", "product_name", "product_category", "standard_lead_time_days"]], on="sku_id", how="left")

    merged["d_avg"] = merged["d_avg"].fillna(0.1)
    merged["d_std"] = merged["d_std"].fillna(0.05)

    # 1. Safety Stock
    # SS = Z * sigma_D * sqrt(L)
    merged["safety_stock"] = np.ceil(
        service_level_z * merged["d_std"] * np.sqrt(merged["lead_time_days"])
    ).astype(int)

    # 2. Reorder Point
    # ROP = (D_avg * L) + SS
    merged["lead_time_demand"] = np.ceil(merged["d_avg"] * merged["lead_time_days"]).astype(int)
    merged["reorder_point"] = merged["lead_time_demand"] + merged["safety_stock"]

    # 3. Recommended Order Quantity
    # Standard replenishment batch covers 30 days of expected demand
    cycle_stock_target = np.ceil(merged["d_avg"] * 30.0).astype(int)
    order_deficit = (merged["reorder_point"] + cycle_stock_target) - merged["closing_stock"]
    merged["recommended_order_qty"] = np.maximum(0, order_deficit).astype(int)

    # 4. Reorder Urgency
    def get_urgency(row) -> str:
        if row["closing_stock"] <= row["safety_stock"]:
            return "Urgent (Below Safety Stock)"
        elif row["closing_stock"] <= row["reorder_point"]:
            return "Reorder Triggered (Below ROP)"
        return "Normal"

    merged["reorder_status"] = merged.apply(get_urgency, axis=1)

    return merged[[
        "distributor_id", "sku_id", "product_name", "product_category", "closing_stock",
        "lead_time_days", "d_avg", "d_std", "safety_stock", "reorder_point",
        "recommended_order_qty", "reorder_status"
    ]].sort_values(by=["reorder_status", "recommended_order_qty"], ascending=[True, False]).reset_index(drop=True)
