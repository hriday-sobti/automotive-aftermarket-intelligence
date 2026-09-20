# Decision simulator for reviewing distributor and SKU commercial health.

import os
import sys
from typing import Dict, Any
import pandas as pd

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))


class ManagerDecisionSimulator:
    """Provides a quick diagnostic view of any distributor-SKU combination."""

    def __init__(self, processed_dir: str = "data/processed"):
        self.processed_dir = processed_dir
        self.sales_df = pd.read_csv(os.path.join(processed_dir, "fact_sales.csv"))
        self.products_df = pd.read_csv(os.path.join(processed_dir, "dim_product.csv"))
        self.distributors_df = pd.read_csv(os.path.join(processed_dir, "dim_distributor.csv"))
        self.regions_df = pd.read_csv(os.path.join(processed_dir, "dim_region.csv"))
        self.inventory_df = pd.read_csv(os.path.join(processed_dir, "fact_inventory.csv"))

    def query_sku_distributor(self, distributor_id: str, sku_id: str) -> Dict[str, Any]:
        """Looks up sales, inventory coverage, risk level, and suggested actions."""
        prod = self.products_df[self.products_df["sku_id"] == sku_id].iloc[0]
        dist = self.distributors_df[self.distributors_df["distributor_id"] == distributor_id].iloc[0]
        reg = self.regions_df[self.regions_df["region_id"] == dist["region_id"]].iloc[0]

        # Filter sales for this distributor + SKU
        d_sales = self.sales_df[
            (self.sales_df["distributor_id"] == distributor_id) &
            (self.sales_df["sku_id"] == sku_id)
        ]

        sales_2024 = d_sales[d_sales["year"] == 2024]
        sales_2025 = d_sales[d_sales["year"] == 2025]

        rev_2024 = float(sales_2024["revenue"].sum())
        rev_2025 = float(sales_2025["revenue"].sum())
        gp_2025 = float(sales_2025["gross_profit"].sum())
        units_2025 = int(sales_2025["quantity"].sum())
        margin_pct = (gp_2025 / rev_2025 * 100.0) if rev_2025 > 0 else 0.0
        yoy_growth = ((rev_2025 - rev_2024) / rev_2024 * 100.0) if rev_2024 > 0 else 0.0

        # Latest stock position
        d_inv = self.inventory_df[
            (self.inventory_df["distributor_id"] == distributor_id) &
            (self.inventory_df["sku_id"] == sku_id)
        ].sort_values("date")

        current_stock = int(d_inv.iloc[-1]["closing_stock"]) if not d_inv.empty else 0
        lead_time = int(prod["standard_lead_time_days"])

        # Daily sales velocity (run-rate over the year)
        daily_velocity = units_2025 / 365.0
        doi = round(current_stock / daily_velocity, 1) if daily_velocity > 0 else 999.0

        # Simple operational risk categorization based on coverage vs lead time
        coverage_ratio = doi / max(1, lead_time * 1.5)
        if coverage_ratio < 0.7:
            risk_cat = "Critical"
            rec_action = "Initiate emergency expedited replenishment"
            driver = "Critically low inventory coverage vs lead time"
        elif coverage_ratio < 1.0:
            risk_cat = "High Risk"
            rec_action = "Place standard replenishment purchase order"
            driver = "Stock below target safety stock buffer"
        elif coverage_ratio < 1.8:
            risk_cat = "Watch"
            rec_action = "Monitor weekly sell-through rates"
            driver = "Normal operational consumption"
        else:
            risk_cat = "Low Risk"
            rec_action = "Maintain current replenishment cadence"
            driver = "Ample buffer stock"

        return {
            "distributor_id": distributor_id,
            "distributor_name": dist["distributor_name"],
            "region": reg["region_name"],
            "sku_id": sku_id,
            "product_name": prod["product_name"],
            "product_category": prod["product_category"],
            "velocity_profile": prod["velocity_profile"],
            "current_stock": current_stock,
            "days_of_inventory": doi,
            "daily_velocity_units": round(daily_velocity, 2),
            "revenue_2025_inr": round(rev_2025, 2),
            "gross_margin_pct_2025": round(margin_pct, 2),
            "yoy_revenue_growth_pct": round(yoy_growth, 2),
            "lead_time_days": lead_time,
            "stockout_risk_category": risk_cat,
            "primary_driver": driver,
            "recommended_action": rec_action
        }
