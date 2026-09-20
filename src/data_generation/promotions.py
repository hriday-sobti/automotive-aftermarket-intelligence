"""Trade marketing campaign and promotion generator for Automotive Aftermarket.

Simulates structured B2B commercial campaigns:
- Seasonal pre-stocking deals (Monsoon Safety Braking, Summer Chilling AC)
- Volume rebate tiers
- Margin vs volume trade-offs (Some promotions highly accretive, others margin dilutive)
- Controlled targeting by Region and Product Category
"""

from typing import Dict, List
import numpy as np
import pandas as pd


def generate_promotions(
    products_df: pd.DataFrame,
    regions_df: pd.DataFrame,
    seed: int = 42
) -> pd.DataFrame:
    """Generate calendar of trade marketing campaigns across the 24-month horizon."""
    rng = np.random.default_rng(seed)

    campaign_blueprints = [
        {
            "name": "Monsoon Safety Braking Campaign 2024",
            "type": "Seasonal Pre-Stocking",
            "start": "2024-06-15",
            "end": "2024-08-15",
            "category": "Braking Systems",
            "discount_pct": 0.10,
            "budget": 450000.0,
            "target_region": "REG-02", # West (heavy rainfall)
            "expected_uplift": 0.28,
            "objective": "Pre-monsoon inventory build & volume leadership"
        },
        {
            "name": "Cooling Systems Summer Rush 2024",
            "type": "Seasonal Performance Deal",
            "start": "2024-03-01",
            "end": "2024-05-15",
            "category": "Thermal & Cooling",
            "discount_pct": 0.08,
            "budget": 380000.0,
            "target_region": "REG-01", # North (intense heat)
            "expected_uplift": 0.22,
            "objective": "Distributor stock build ahead of peak AC failure season"
        },
        {
            "name": "Festive Service Filtration Blitz 2024",
            "type": "Volume Rebate Scheme",
            "start": "2024-09-15",
            "end": "2024-11-05",
            "category": "Filtration",
            "discount_pct": 0.12,
            "budget": 520000.0,
            "target_region": "REG-03", # South
            "expected_uplift": 0.35,
            "objective": "Capture workshop pre-festival vehicle servicing surge"
        },
        {
            "name": "Electrical & Ignition Winter Readiness 2024",
            "type": "Trade Stocking Deal",
            "start": "2024-11-15",
            "end": "2025-01-15",
            "category": "Electrical & Ignition",
            "discount_pct": 0.07,
            "budget": 300000.0,
            "target_region": "REG-01",
            "expected_uplift": 0.18,
            "objective": "Spark plug and battery starter pre-winter push"
        },
        {
            "name": "Commercial Heavy-Duty Suspension Drive 2024",
            "type": "Fleet Channel Rebate",
            "start": "2024-08-01",
            "end": "2024-09-30",
            "category": "Chassis & Steering",
            "discount_pct": 0.14,
            "budget": 420000.0,
            "target_region": "REG-04", # East
            "expected_uplift": 0.12, # Weak response / margin dilutive candidate
            "objective": "Expand fleet garage penetration in eastern logistics corridors"
        },
        {
            "name": "Monsoon Safety Braking Campaign 2025",
            "type": "Seasonal Pre-Stocking",
            "start": "2025-06-15",
            "end": "2025-08-15",
            "category": "Braking Systems",
            "discount_pct": 0.12,
            "budget": 500000.0,
            "target_region": "REG-02",
            "expected_uplift": 0.32,
            "objective": "Defend braking market share against aggressive tier-2 competitors"
        },
        {
            "name": "Cooling Systems Summer Rush 2025",
            "type": "Seasonal Performance Deal",
            "start": "2025-03-01",
            "end": "2025-05-15",
            "category": "Thermal & Cooling",
            "discount_pct": 0.08,
            "budget": 410000.0,
            "target_region": "REG-01",
            "expected_uplift": 0.25,
            "objective": "Sustain distributor fill rates on radiators and water pumps"
        },
        {
            "name": "Festive Service Filtration Blitz 2025",
            "type": "Volume Rebate Scheme",
            "start": "2025-09-15",
            "end": "2025-11-05",
            "category": "Filtration",
            "discount_pct": 0.15,
            "budget": 600000.0,
            "target_region": "REG-03",
            "expected_uplift": 0.30, # Heavy discount compressing margins
            "objective": "Aggressive volume push to hit annual distributor targets"
        },
        {
            "name": "All-India Fast-Moving Spares Incentive Q1-2024",
            "type": "National Trade Rebate",
            "start": "2024-01-15",
            "end": "2024-02-28",
            "category": "Filtration",
            "discount_pct": 0.06,
            "budget": 350000.0,
            "target_region": "ALL",
            "expected_uplift": 0.15,
            "objective": "Kickstart distributor ordering post-inventory audit"
        },
        {
            "name": "All-India Fast-Moving Spares Incentive Q1-2025",
            "type": "National Trade Rebate",
            "start": "2025-01-15",
            "end": "2025-02-28",
            "category": "Filtration",
            "discount_pct": 0.06,
            "budget": 380000.0,
            "target_region": "ALL",
            "expected_uplift": 0.16,
            "objective": "Replicate Q1 volume activation"
        },
        {
            "name": "Steering & Suspension Spring Overhaul 2024",
            "type": "Channel Rebate",
            "start": "2024-04-01",
            "end": "2024-05-31",
            "category": "Chassis & Steering",
            "discount_pct": 0.09,
            "budget": 280000.0,
            "target_region": "REG-03",
            "expected_uplift": 0.20,
            "objective": "Drive premium shock absorber adoption in urban garages"
        },
        {
            "name": "Steering & Suspension Spring Overhaul 2025",
            "type": "Channel Rebate",
            "start": "2025-04-01",
            "end": "2025-05-31",
            "category": "Chassis & Steering",
            "discount_pct": 0.09,
            "budget": 310000.0,
            "target_region": "REG-03",
            "expected_uplift": 0.21,
            "objective": "Deepen regional penetration with suspension kits"
        },
        {
            "name": "Braking Platinum Tier Loyalty Scheme 2024",
            "type": "Distributor Loyalty Bonus",
            "start": "2024-10-01",
            "end": "2024-12-15",
            "category": "Braking Systems",
            "discount_pct": 0.05,
            "budget": 400000.0,
            "target_region": "ALL",
            "expected_uplift": 0.14,
            "objective": "Reward high-compliance platinum wholesale distributors"
        },
        {
            "name": "Braking Platinum Tier Loyalty Scheme 2025",
            "type": "Distributor Loyalty Bonus",
            "start": "2025-10-01",
            "end": "2025-12-15",
            "category": "Braking Systems",
            "discount_pct": 0.05,
            "budget": 440000.0,
            "target_region": "ALL",
            "expected_uplift": 0.15,
            "objective": "Annual loyalty rebate program"
        },
        {
            "name": "Electrical Sensor Expansion Drive 2024",
            "type": "New Product Push",
            "start": "2024-07-01",
            "end": "2024-08-31",
            "category": "Electrical & Ignition",
            "discount_pct": 0.15,
            "budget": 350000.0,
            "target_region": "REG-04",
            "expected_uplift": 0.08, # Weak response / negative ROI
            "objective": "Introduce complex MAF sensors to secondary markets"
        },
        {
            "name": "Thermal Heatwave Emergency Stocking 2025",
            "type": "Flash Trade Stocking",
            "start": "2025-05-01",
            "end": "2025-06-15",
            "category": "Thermal & Cooling",
            "discount_pct": 0.10,
            "budget": 320000.0,
            "target_region": "REG-02",
            "expected_uplift": 0.28,
            "objective": "Expedite radiator deliveries during peak western summer"
        }
    ]

    promotions = []
    for i, bp in enumerate(campaign_blueprints, start=1):
        promotions.append({
            "promotion_id": f"PRM-{i:03d}",
            "campaign_name": bp["name"],
            "campaign_type": bp["type"],
            "start_date": bp["start"],
            "end_date": bp["end"],
            "target_category": bp["category"],
            "target_region": bp["target_region"],
            "discount_pct": bp["discount_pct"],
            "budget_inr": bp["budget"],
            "expected_uplift_pct": bp["expected_uplift"],
            "campaign_objective": bp["objective"]
        })

    return pd.DataFrame(promotions)
