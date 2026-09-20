"""Data cleaning and feature engineering pipeline for Aftermarket Platform.

Enriches raw and validated facts with analytical attributes:
- Temporal features (Year-Month, Week-of-Year, Quarter, Day-of-Week)
- Sales margin percentages: gross_margin_pct = (gross_profit / revenue) * 100
- Unit metrics: unit_cost, unit_revenue
- Pareto cumulative contribution ranking per SKU
- Rolling 30-day velocity indicators
"""

from typing import Dict
import numpy as np
import pandas as pd


def clean_and_engineer_sales(sales_df: pd.DataFrame, products_df: pd.DataFrame) -> pd.DataFrame:
    """Enrich sales fact table with analytical attributes."""
    df = sales_df.copy()

    # Ensure consistent datetime types
    df["date"] = pd.to_datetime(df["date"])
    df["year"] = df["date"].dt.year
    df["month"] = df["date"].dt.month
    df["year_month"] = df["date"].dt.strftime("%Y-%m")
    df["quarter"] = "Q" + df["date"].dt.quarter.astype(str)
    df["week_of_year"] = df["date"].dt.isocalendar().week.astype(int)

    # Margin percentage
    df["gross_margin_pct"] = np.where(
        df["revenue"] > 0,
        np.round((df["gross_profit"] / df["revenue"]) * 100.0, 2),
        0.0
    )

    # Unit price metrics
    df["unit_cost"] = np.where(
        df["quantity"] > 0,
        np.round(df["cost"] / df["quantity"], 2),
        0.0
    )

    # Re-convert date to ISO string for standard storage
    df["date"] = df["date"].dt.strftime("%Y-%m-%d")

    return df


def calculate_sku_pareto(sales_df: pd.DataFrame) -> pd.DataFrame:
    """Calculate 80/20 Pareto revenue concentration across all SKUs."""
    sku_agg = (
        sales_df.groupby("sku_id")
        .agg(
            total_revenue=("revenue", "sum"),
            total_units=("quantity", "sum"),
            total_gross_profit=("gross_profit", "sum")
        )
        .reset_index()
    )

    sku_agg = sku_agg.sort_values(by="total_revenue", ascending=False).reset_index(drop=True)
    sku_agg["cum_revenue"] = sku_agg["total_revenue"].cumsum()
    total_rev = sku_agg["total_revenue"].sum()
    sku_agg["cum_revenue_pct"] = np.round((sku_agg["cum_revenue"] / total_rev) * 100.0, 2)

    # Assign Pareto Tier: A = Top 80% revenue, B = Next 15% (80-95%), C = Bottom 5%
    sku_agg["pareto_class"] = np.where(
        sku_agg["cum_revenue_pct"] <= 80.0, "Class A (Top 80% Rev)",
        np.where(sku_agg["cum_revenue_pct"] <= 95.0, "Class B (Next 15% Rev)", "Class C (Bottom 5% Rev)")
    )

    return sku_agg
