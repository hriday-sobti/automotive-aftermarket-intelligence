"""Synthetic demand and seasonality generator for Automotive Aftermarket.

Models latent market demand incorporating:
- Category-specific seasonality (Monsoon wiper/brake surges, summer cooling spikes, festival pre-stocking)
- Regional vehicle parc weightings
- Vehicle segment usage intensity
- Realistic macroeconomic trend growth (e.g. 6-8% annual expansion)
- Controlled stochastic noise
"""

from typing import Dict
import numpy as np
import pandas as pd


def get_seasonal_factor(month: int, category: str) -> float:
    """Calculate realistic automotive seasonality index by calendar month and product line.

    Business Rationale:
    - Braking: Peaks in Q3 (July-September monsoon season in India) due to wet-road wear and pre-festival servicing.
    - Filtration: High continuous demand with peaks during annual servicing months (March fiscal year-end, Oct-Nov Diwali).
    - Thermal & Cooling: Strong peak in Q1-Q2 (April-June) ahead of and during peak summer temperatures.
    - Electrical: Peaks in winter (Dec-Jan) due to cold battery/starter stress, and post-monsoon harness corrosion.
    - Chassis: Post-monsoon road degradation causes spikes in suspension demand (Sept-Nov).
    """
    seasonality_map = {
        "Braking Systems": {1: 0.92, 2: 0.95, 3: 1.05, 4: 0.98, 5: 1.00, 6: 1.08, 7: 1.22, 8: 1.25, 9: 1.18, 10: 1.15, 11: 0.96, 12: 0.90},
        "Filtration": {1: 0.96, 2: 0.98, 3: 1.15, 4: 1.02, 5: 1.00, 6: 1.02, 7: 1.04, 8: 1.05, 9: 1.10, 10: 1.20, 11: 1.02, 12: 0.94},
        "Thermal & Cooling": {1: 0.82, 2: 0.88, 3: 1.12, 4: 1.35, 5: 1.40, 6: 1.25, 7: 0.95, 8: 0.85, 9: 0.88, 10: 0.92, 11: 0.80, 12: 0.78},
        "Electrical & Ignition": {1: 1.15, 2: 1.05, 3: 1.00, 4: 0.95, 5: 0.92, 6: 0.90, 7: 0.98, 8: 1.02, 9: 1.05, 10: 1.12, 11: 1.10, 12: 1.18},
        "Chassis & Steering": {1: 0.94, 2: 0.96, 3: 1.04, 4: 0.98, 5: 0.96, 6: 0.98, 7: 1.05, 8: 1.12, 9: 1.24, 10: 1.20, 11: 1.02, 12: 0.95}
    }
    return seasonality_map.get(category, {}).get(month, 1.0)


def generate_demand_profiles(
    products_df: pd.DataFrame,
    regions_df: pd.DataFrame,
    start_date: str = "2024-01-01",
    end_date: str = "2025-12-31",
    seed: int = 42
) -> pd.DataFrame:
    """Generate weekly latent market demand across SKU × Region combinations.

    Returns:
        DataFrame representing weekly market demand observations.
    """
    rng = np.random.default_rng(seed)
    weeks = pd.date_range(start=start_date, end=end_date, freq="W-MON")

    records = []
    # Pre-map regional multipliers
    reg_multipliers = dict(zip(regions_df["region_id"], regions_df["parc_size_multiplier"]))

    for _, prod in products_df.iterrows():
        sku_id = prod["sku_id"]
        cat = prod["product_category"]
        segment = prod["vehicle_segment"]
        velocity = prod["velocity_profile"]

        # Base weekly volume depending on velocity classification
        if velocity == "Fast Moving":
            base_vol = rng.uniform(80.0, 240.0)
        elif velocity == "Medium Moving":
            base_vol = rng.uniform(25.0, 80.0)
        else:
            base_vol = rng.uniform(5.0, 25.0)

        for week_idx, w_date in enumerate(weeks):
            m = w_date.month
            seasonal = get_seasonal_factor(m, cat)
            # 7% annual trend growth
            trend = 1.0 + (0.07 * (week_idx / 52.0))

            for reg_id, reg_mult in reg_multipliers.items():
                noise = rng.normal(1.0, 0.08)
                latent_demand = float(np.round(base_vol * reg_mult * seasonal * trend * noise, 1))
                latent_demand = max(1.0, latent_demand)

                records.append({
                    "week_start_date": w_date.strftime("%Y-%m-%d"),
                    "sku_id": sku_id,
                    "region_id": reg_id,
                    "vehicle_segment": segment,
                    "product_category": cat,
                    "seasonal_index": seasonal,
                    "trend_factor": round(trend, 3),
                    "estimated_latent_demand": latent_demand
                })

    return pd.DataFrame(records)
