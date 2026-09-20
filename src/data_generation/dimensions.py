"""Dimension generator for Automotive Aftermarket Intelligence Platform.

Generates realistic master dimensions:
- Regions (North, West, South, East)
- Vehicle Segments (PV, LCV, HCV, 2W)
- Products / SKUs with realistic cost, list prices, and automotive categories
- Distributors with regional alignment and sales targets
- Workshops with customer types and demand factors
- Date Dimension spanning the entire simulation horizon
"""

from datetime import datetime
from typing import Dict
import numpy as np
import pandas as pd


def generate_regions() -> pd.DataFrame:
    """Generate geographic regions with market characteristics."""
    data = [
        {"region_id": "REG-01", "region_name": "North Region", "state_cluster": "Delhi NCR, Punjab, Haryana, UP", "market_tier": "Tier 1", "parc_size_multiplier": 1.25},
        {"region_id": "REG-02", "region_name": "West Region", "state_cluster": "Maharashtra, Gujarat, Goa", "market_tier": "Tier 1", "parc_size_multiplier": 1.35},
        {"region_id": "REG-03", "region_name": "South Region", "state_cluster": "Karnataka, Tamil Nadu, Telangana, Kerala", "market_tier": "Tier 1", "parc_size_multiplier": 1.30},
        {"region_id": "REG-04", "region_name": "East Region", "state_cluster": "West Bengal, Odisha, Bihar, Assam", "market_tier": "Tier 2", "parc_size_multiplier": 0.85},
    ]
    return pd.DataFrame(data)


def generate_vehicle_segments() -> pd.DataFrame:
    """Generate vehicle segment classifications and typical maintenance cycles."""
    data = [
        {"segment_id": "SEG-PV", "segment_name": "Passenger Vehicle (PV)", "powertrain": "ICE & Hybrid", "avg_annual_mileage_km": 12000, "maintenance_intensity": 1.0},
        {"segment_id": "SEG-LCV", "segment_name": "Light Commercial Vehicle (LCV)", "powertrain": "Diesel & CNG", "avg_annual_mileage_km": 35000, "maintenance_intensity": 1.8},
        {"segment_id": "SEG-HCV", "segment_name": "Heavy Commercial Vehicle (HCV)", "powertrain": "Heavy Diesel", "avg_annual_mileage_km": 75000, "maintenance_intensity": 2.4},
        {"segment_id": "SEG-2W", "segment_name": "Two-Wheeler (2W)", "powertrain": "Petrol & EV", "avg_annual_mileage_km": 8000, "maintenance_intensity": 0.7},
    ]
    return pd.DataFrame(data)


def generate_products(num_products: int = 150, seed: int = 42) -> pd.DataFrame:
    """Generate catalog of automotive aftermarket SKUs with realistic cost, margin, and category mix."""
    rng = np.random.default_rng(seed)

    categories = {
        "Braking Systems": {
            "subcategories": ["Brake Pads Front", "Brake Pads Rear", "Brake Discs / Rotors", "Brake Shoe Set", "Brake Master Cylinder", "Brake Fluid DOT4"],
            "cost_range": (350.0, 3200.0),
            "margin_range": (0.30, 0.48),
            "lead_time_days": (10, 25),
            "segments": ["SEG-PV", "SEG-LCV", "SEG-HCV", "SEG-2W"],
            "fast_moving": True,
        },
        "Filtration": {
            "subcategories": ["Oil Filter Spin-On", "Air Filter Element", "Fuel Filter Diesel", "Cabin Air Carbon Filter", "Hydraulic Filter"],
            "cost_range": (120.0, 1400.0),
            "margin_range": (0.35, 0.52),
            "lead_time_days": (7, 18),
            "segments": ["SEG-PV", "SEG-LCV", "SEG-HCV"],
            "fast_moving": True,
        },
        "Electrical & Ignition": {
            "subcategories": ["Spark Plug Iridium", "Glow Plug Set", "Alternator 12V", "Starter Motor 24V", "Ignition Coil Pack", "Automotive Sensor MAF"],
            "cost_range": (450.0, 9500.0),
            "margin_range": (0.28, 0.42),
            "lead_time_days": (15, 40),
            "segments": ["SEG-PV", "SEG-LCV", "SEG-HCV", "SEG-2W"],
            "fast_moving": False,
        },
        "Chassis & Steering": {
            "subcategories": ["Suspension Strut Front", "Shock Absorber Rear", "Tie Rod End Outer", "Ball Joint Lower", "Control Arm Bushing Kit"],
            "cost_range": (600.0, 5800.0),
            "margin_range": (0.26, 0.38),
            "lead_time_days": (20, 45),
            "segments": ["SEG-PV", "SEG-LCV", "SEG-HCV"],
            "fast_moving": False,
        },
        "Thermal & Cooling": {
            "subcategories": ["Engine Water Pump", "Engine Radiator Assembly", "Thermostat Valve", "Coolant Long Life 5L", "Electric Cooling Fan"],
            "cost_range": (400.0, 6500.0),
            "margin_range": (0.25, 0.40),
            "lead_time_days": (14, 35),
            "segments": ["SEG-PV", "SEG-LCV", "SEG-HCV"],
            "fast_moving": False,
        }
    }

    products = []
    category_keys = list(categories.keys())
    weights = [0.28, 0.28, 0.18, 0.14, 0.12]  # Braking & Filtration are higher volume

    for i in range(1, num_products + 1):
        cat_name = rng.choice(category_keys, p=weights)
        cat_meta = categories[cat_name]
        subcat = rng.choice(cat_meta["subcategories"])
        segment = rng.choice(cat_meta["segments"])

        cost = float(np.round(rng.uniform(cat_meta["cost_range"][0], cat_meta["cost_range"][1]), 2))
        target_margin = rng.uniform(cat_meta["margin_range"][0], cat_meta["margin_range"][1])
        list_price = float(np.round(cost / (1.0 - target_margin), 2))

        lead_time = int(rng.integers(cat_meta["lead_time_days"][0], cat_meta["lead_time_days"][1] + 1))
        is_fast = cat_meta["fast_moving"]
        
        # 80/20 Pareto velocity weight
        velocity_profile = "Fast Moving" if (is_fast and rng.random() > 0.25) else ("Medium Moving" if rng.random() > 0.4 else "Slow Moving")

        brand_tier = rng.choice(["Premium OE Specification", "Standard Aftermarket OE Quality", "Commercial Heavy-Duty"], p=[0.40, 0.45, 0.15])
        sku_id = f"SKU-{cat_name[:3].upper()}-{i:04d}"
        product_name = f"{subcat} ({brand_tier.split()[0]})"

        products.append({
            "sku_id": sku_id,
            "product_name": product_name,
            "product_category": cat_name,
            "subcategory": subcat,
            "brand_tier": brand_tier,
            "vehicle_segment": segment,
            "cost_price": cost,
            "list_price": list_price,
            "standard_lead_time_days": lead_time,
            "velocity_profile": velocity_profile,
            "product_status": "Active" if rng.random() > 0.05 else "Phase-Out"
        })

    return pd.DataFrame(products)


def generate_distributors(regions_df: pd.DataFrame, num_distributors: int = 20, seed: int = 42) -> pd.DataFrame:
    """Generate authorized aftermarket wholesale distributors across geographic regions."""
    rng = np.random.default_rng(seed)
    region_ids = regions_df["region_id"].tolist()

    distributor_names = [
        "Apex Auto Distributors", "Bharat Spares Logistics", "Continental Motor Parts",
        "Deccan Auto Wholesale", "Everest Component Traders", "Frontline Auto Supply",
        "Gateway Parts Hub", "Heritage Automotive Hub", "Imperial Auto Distributors",
        "Jupiter Mobility Components", "Kalyan Spare Parts Corp", "Laxmi Auto Enterprises",
        "Metro Automotive Agencies", "National Spares Corporation", "Omega Commercial Spares",
        "Premier Auto Logistics", "Radiant Automotive Supply", "Southern Spares Link",
        "Titan Motor Parts", "Universal Automotive Wholesalers"
    ]

    distributors = []
    for i in range(num_distributors):
        d_id = f"DIST-{i+1:02d}"
        name = distributor_names[i] if i < len(distributor_names) else f"Regional Spares Partner {i+1}"
        region_id = region_ids[i % len(region_ids)]
        tier = rng.choice(["Tier 1 Platinum", "Tier 2 Gold", "Tier 3 Silver"], p=[0.25, 0.50, 0.25])
        credit_terms = 45 if tier == "Tier 1 Platinum" else (30 if tier == "Tier 2 Gold" else 15)
        annual_target = 60000000.0 if tier == "Tier 1 Platinum" else (35000000.0 if tier == "Tier 2 Gold" else 18000000.0)

        distributors.append({
            "distributor_id": d_id,
            "distributor_name": name,
            "region_id": region_id,
            "distributor_tier": tier,
            "credit_term_days": credit_terms,
            "annual_sales_target_inr": annual_target
        })

    return pd.DataFrame(distributors)


def generate_workshops(regions_df: pd.DataFrame, num_workshops: int = 120, seed: int = 42) -> pd.DataFrame:
    """Generate customer workshops and garages purchasing through distributors."""
    rng = np.random.default_rng(seed)
    region_ids = regions_df["region_id"].tolist()

    workshop_types = ["Multi-Brand Independent Garage", "Authorized Chain Franchise", "Fleet Maintenance Depot", "Specialist Braking & Suspension Hub"]
    type_weights = [0.55, 0.20, 0.15, 0.10]

    workshops = []
    for i in range(1, num_workshops + 1):
        w_id = f"WS-{i:03d}"
        w_type = rng.choice(workshop_types, p=type_weights)
        region_id = rng.choice(region_ids)
        demand_factor = float(np.round(rng.normal(1.0, 0.25), 2))
        demand_factor = max(0.4, min(1.8, demand_factor))

        workshops.append({
            "workshop_id": w_id,
            "workshop_name": f"Prime Care Workshop #{i:03d} ({w_type[:12]})",
            "region_id": region_id,
            "workshop_type": w_type,
            "monthly_demand_factor": demand_factor
        })

    return pd.DataFrame(workshops)


def generate_date_dimension(start_date: str = "2024-01-01", end_date: str = "2025-12-31") -> pd.DataFrame:
    """Generate comprehensive calendar date dimension table."""
    dates = pd.date_range(start=start_date, end=end_date, freq="D")
    date_rows = []

    for d in dates:
        date_rows.append({
            "date": d.strftime("%Y-%m-%d"),
            "year": d.year,
            "quarter": f"Q{d.quarter}",
            "year_quarter": f"{d.year}-Q{d.quarter}",
            "month": d.month,
            "month_name": d.strftime("%B"),
            "year_month": d.strftime("%Y-%m"),
            "week_of_year": int(d.isocalendar().week),
            "day_of_month": d.day,
            "day_of_week": d.weekday() + 1,  # 1 = Monday, 7 = Sunday
            "day_name": d.strftime("%A"),
            "is_weekend": 1 if d.weekday() >= 5 else 0
        })

    return pd.DataFrame(date_rows)


def generate_all_dimensions(config: Dict) -> Dict[str, pd.DataFrame]:
    """Orchestrate generation of all dimensional entities."""
    seed = config["project"]["random_seed"]
    scale = config["scale"]
    timeline = config["timeline"]

    regions_df = generate_regions()
    vehicle_segments_df = generate_vehicle_segments()
    products_df = generate_products(num_products=scale["num_products"], seed=seed)
    distributors_df = generate_distributors(regions_df, num_distributors=scale["num_distributors"], seed=seed)
    workshops_df = generate_workshops(regions_df, num_workshops=scale["num_workshops"], seed=seed)
    date_df = generate_date_dimension(start_date=timeline["start_date"], end_date=timeline["end_date"])

    return {
        "dim_region": regions_df,
        "dim_vehicle_segment": vehicle_segments_df,
        "dim_product": products_df,
        "dim_distributor": distributors_df,
        "dim_workshop": workshops_df,
        "dim_date": date_df
    }
