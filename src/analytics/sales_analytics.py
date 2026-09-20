# Commercial sales calculations and distributor performance metrics.

from typing import Dict
import numpy as np
import pandas as pd


def compute_executive_kpis(sales_df: pd.DataFrame) -> Dict[str, float]:
    """Roll up high-level revenue, units, margin, and annual growth."""
    total_rev = float(sales_df["revenue"].sum())
    total_cost = float(sales_df["cost"].sum())
    total_units = int(sales_df["quantity"].sum())
    total_gp = float(sales_df["gross_profit"].sum())
    gm_pct = (total_gp / total_rev * 100.0) if total_rev > 0 else 0.0

    # Year-over-year: 2025 vs 2024
    rev_2024 = float(sales_df[sales_df["year"] == 2024]["revenue"].sum())
    rev_2025 = float(sales_df[sales_df["year"] == 2025]["revenue"].sum())
    yoy_growth = ((rev_2025 - rev_2024) / rev_2024 * 100.0) if rev_2024 > 0 else 0.0

    return {
        "total_revenue": round(total_rev, 2),
        "total_units": total_units,
        "total_cost": round(total_cost, 2),
        "total_gross_profit": round(total_gp, 2),
        "gross_margin_pct": round(gm_pct, 2),
        "revenue_2024": round(rev_2024, 2),
        "revenue_2025": round(rev_2025, 2),
        "yoy_revenue_growth_pct": round(yoy_growth, 2),
        "active_skus": int(sales_df["sku_id"].nunique()),
        "active_distributors": int(sales_df["distributor_id"].nunique())
    }


def compute_category_intelligence(sales_df: pd.DataFrame, products_df: pd.DataFrame) -> pd.DataFrame:
    """Group sales and margins by product line to see category mix."""
    merged = sales_df.merge(products_df[["sku_id", "product_category"]], on="sku_id")
    total_rev = merged["revenue"].sum()

    cat_perf = (
        merged.groupby("product_category")
        .agg(
            revenue=("revenue", "sum"),
            units=("quantity", "sum"),
            gross_profit=("gross_profit", "sum")
        )
        .reset_index()
    )
    cat_perf["gross_margin_pct"] = np.round((cat_perf["gross_profit"] / cat_perf["revenue"]) * 100.0, 2)
    cat_perf["revenue_share_pct"] = np.round((cat_perf["revenue"] / total_rev) * 100.0, 2)
    return cat_perf.sort_values(by="revenue", ascending=False).reset_index(drop=True)


def compute_distributor_growth(sales_df: pd.DataFrame, distributors_df: pd.DataFrame) -> pd.DataFrame:
    """Track distributor growth year-over-year and compare against annual targets."""
    yearly = (
        sales_df.groupby(["distributor_id", "year"])
        .agg(
            revenue=("revenue", "sum"),
            gross_profit=("gross_profit", "sum"),
            units=("quantity", "sum")
        )
        .reset_index()
    )

    pivoted = yearly.pivot(index="distributor_id", columns="year", values=["revenue", "gross_profit", "units"]).reset_index()
    pivoted.columns = [f"{c[0]}_{c[1]}" if c[1] else c[0] for c in pivoted.columns]

    merged = pivoted.merge(distributors_df, on="distributor_id")
    merged["yoy_revenue_growth_pct"] = np.round(
        ((merged["revenue_2025"] - merged["revenue_2024"]) / merged["revenue_2024"]) * 100.0, 2
    )
    merged["margin_pct_2025"] = np.round(
        (merged["gross_profit_2025"] / merged["revenue_2025"]) * 100.0, 2
    )
    merged["target_attainment_pct"] = np.round(
        (merged["revenue_2025"] / merged["annual_sales_target_inr"]) * 100.0, 2
    )

    return merged.sort_values(by="revenue_2025", ascending=False).reset_index(drop=True)
