# B2B Trade marketing promotion evaluation and incremental margin analysis.

import numpy as np
import pandas as pd


def evaluate_promotions(
    sales_df: pd.DataFrame,
    promotions_df: pd.DataFrame,
    products_df: pd.DataFrame
) -> pd.DataFrame:
    """Evaluates campaign performance by comparing promoted sales against non-promoted baselines."""
    # Tag product categories onto sales
    sales = sales_df.merge(products_df[["sku_id", "product_category"]], on="sku_id")

    results = []

    for _, promo in promotions_df.iterrows():
        p_id = promo["promotion_id"]
        p_name = promo["campaign_name"]
        cat = promo["target_category"]
        reg = promo["target_region"]
        start = promo["start_date"]
        end = promo["end_date"]
        budget = promo["budget_inr"]
        disc_pct = promo["discount_pct"]

        # Filter promoted sales
        p_sales = sales[sales["promotion_id"] == p_id]

        promoted_units = int(p_sales["quantity"].sum())
        promoted_rev = float(p_sales["revenue"].sum())
        promoted_gp = float(p_sales["gross_profit"].sum())
        discount_cost = float((p_sales["quantity"] * (p_sales["list_price"] - p_sales["net_unit_price"])).sum())

        # Construct non-promoted baseline for matching category and region
        reg_filter = (sales["region_id"] == reg) if reg != "ALL" else pd.Series(True, index=sales.index)
        base_pool = sales[
            (sales["product_category"] == cat) &
            reg_filter &
            (sales["promotion_id"] == "NONE")
        ]

        duration_days = (pd.to_datetime(end) - pd.to_datetime(start)).days + 1

        if not base_pool.empty:
            total_base_days = base_pool["date"].nunique()
            daily_base_units = base_pool["quantity"].sum() / max(1, total_base_days)
            daily_base_rev = base_pool["revenue"].sum() / max(1, total_base_days)
            daily_base_gp = base_pool["gross_profit"].sum() / max(1, total_base_days)

            baseline_units = int(np.round(daily_base_units * duration_days))
            baseline_rev = float(np.round(daily_base_rev * duration_days, 2))
            baseline_gp = float(np.round(daily_base_gp * duration_days, 2))
        else:
            baseline_units = int(np.round(promoted_units * 0.75))
            baseline_rev = float(np.round(promoted_rev * 0.75, 2))
            baseline_gp = float(np.round(promoted_gp * 0.80, 2))

        # Incremental financials
        incremental_units = promoted_units - baseline_units
        incremental_rev = round(promoted_rev - baseline_rev, 2)
        incremental_gp = round(promoted_gp - baseline_gp, 2)
        total_promo_cost = round(discount_cost + budget, 2)

        # Promotion Effectiveness Index: Incremental GP / Total Campaign Cost
        pei = round(incremental_gp / total_promo_cost, 2) if total_promo_cost > 0 else 0.0

        if pei > 1.0:
            classification = "Value Accretive"
        elif pei >= 0.0:
            classification = "Margin Dilutive (Volume Only)"
        else:
            classification = "Value Destructive"

        uplift_pct = round((incremental_units / baseline_units) * 100.0, 2) if baseline_units > 0 else 0.0

        results.append({
            "promotion_id": p_id,
            "campaign_name": p_name,
            "campaign_type": promo["campaign_type"],
            "target_category": cat,
            "target_region": reg,
            "duration_days": duration_days,
            "discount_pct": disc_pct,
            "budget_inr": budget,
            "discount_cost_inr": round(discount_cost, 2),
            "total_promotional_cost_inr": total_promo_cost,
            "baseline_units": baseline_units,
            "promoted_units": promoted_units,
            "incremental_units": incremental_units,
            "observed_units_uplift_pct": uplift_pct,
            "baseline_revenue_inr": baseline_rev,
            "promoted_revenue_inr": promoted_rev,
            "incremental_revenue_inr": incremental_rev,
            "baseline_gross_profit_inr": baseline_gp,
            "promoted_gross_profit_inr": promoted_gp,
            "incremental_gross_profit_inr": incremental_gp,
            "promotion_effectiveness_index": pei,
            "commercial_classification": classification
        })

    return pd.DataFrame(results).sort_values(by="promotion_effectiveness_index", ascending=False).reset_index(drop=True)
