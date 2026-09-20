"""Commercial Opportunity Matrix (Four-Quadrant Strategic Model).

Categorizes SKUs and Distributors into four actionable strategic quadrants:
1. High Sales / High Growth -> "Scale & Protect (Core Champions)"
2. High Sales / Low Growth  -> "Cash Cows (Defend & Optimize Margins)"
3. Low Sales / High Growth  -> "Emerging Opportunities (Invest & Expand Coverage)"
4. Low Sales / Low Growth   -> "Rationalize / Review (Strategic Review / Phase-Out)"

Thresholds established empirically using median splits to avoid arbitrary hard-coding.
"""

from typing import Dict, Tuple
import numpy as np
import pandas as pd


def compute_sku_opportunity_matrix(
    sales_df: pd.DataFrame,
    products_df: pd.DataFrame
) -> pd.DataFrame:
    """Classify SKUs into the four-quadrant commercial opportunity matrix."""
    # Compare 2025 vs 2024
    yearly = (
        sales_df.groupby(["sku_id", "year"])
        .agg(
            revenue=("revenue", "sum"),
            gross_profit=("gross_profit", "sum"),
            units=("quantity", "sum")
        )
        .reset_index()
    )

    pivoted = yearly.pivot(index="sku_id", columns="year", values=["revenue", "gross_profit", "units"]).reset_index()
    pivoted.columns = [f"{c[0]}_{c[1]}" if c[1] else c[0] for c in pivoted.columns]

    merged = pivoted.merge(products_df, on="sku_id")
    merged["revenue_2024"] = merged["revenue_2024"].fillna(0.0)
    merged["revenue_2025"] = merged["revenue_2025"].fillna(0.0)
    merged["units_2025"] = merged["units_2025"].fillna(0)
    merged["gross_profit_2025"] = merged["gross_profit_2025"].fillna(0.0)

    # YoY Growth Rate
    merged["yoy_growth_pct"] = np.where(
        merged["revenue_2024"] > 0,
        np.round(((merged["revenue_2025"] - merged["revenue_2024"]) / merged["revenue_2024"]) * 100.0, 2),
        0.0
    )

    merged["gross_margin_pct_2025"] = np.where(
        merged["revenue_2025"] > 0,
        np.round((merged["gross_profit_2025"] / merged["revenue_2025"]) * 100.0, 2),
        0.0
    )

    # Median thresholds
    median_sales = merged["revenue_2025"].median()
    median_growth = merged["yoy_growth_pct"].median()

    def assign_quadrant(row):
        high_sales = row["revenue_2025"] >= median_sales
        high_growth = row["yoy_growth_pct"] >= median_growth

        if high_sales and high_growth:
            return "High Sales / High Growth (Core Champions)"
        elif high_sales and not high_growth:
            return "High Sales / Low Growth (Cash Cows)"
        elif not high_sales and high_growth:
            return "Low Sales / High Growth (Emerging Stars)"
        else:
            return "Low Sales / Low Growth (Under Review)"

    def assign_action(quadrant: str) -> str:
        if "Core Champions" in quadrant:
            return "Protect stock availability, expand distributor allocation, prioritize trade marketing."
        elif "Cash Cows" in quadrant:
            return "Defend margin, monitor distributor sell-out, avoid unnecessary discounting."
        elif "Emerging Stars" in quadrant:
            return "Target with introductory stocking schemes, expand workshop awareness, improve fill rate."
        else:
            return "Audit catalog necessity, evaluate price sensitivity, consider selective phase-out."

    merged["opportunity_quadrant"] = merged.apply(assign_quadrant, axis=1)
    merged["strategic_recommendation"] = merged["opportunity_quadrant"].apply(assign_action)
    merged["median_sales_benchmark"] = round(median_sales, 2)
    merged["median_growth_benchmark"] = round(median_growth, 2)

    return merged[[
        "sku_id", "product_name", "product_category", "velocity_profile",
        "revenue_2024", "revenue_2025", "yoy_growth_pct", "gross_margin_pct_2025",
        "units_2025", "opportunity_quadrant", "strategic_recommendation"
    ]].sort_values(by="revenue_2025", ascending=False).reset_index(drop=True)
