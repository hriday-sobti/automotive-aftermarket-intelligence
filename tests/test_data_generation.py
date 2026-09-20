# Unit tests for synthetic data generation and entity creation.

import pytest
import numpy as np
import pandas as pd

from src.data_generation.dimensions import (
    generate_regions,
    generate_vehicle_segments,
    generate_products,
    generate_distributors,
    generate_workshops,
    generate_date_dimension,
    generate_all_dimensions
)
from src.data_generation.demand import get_seasonal_factor, generate_demand_profiles
from src.data_generation.promotions import generate_promotions
from src.utils.config_utils import load_config


def test_regions_cardinality_and_columns():
    regions = generate_regions()
    assert len(regions) == 4
    expected_cols = {"region_id", "region_name", "state_cluster", "market_tier", "parc_size_multiplier"}
    assert set(regions.columns) == expected_cols


def test_regions_primary_key_uniqueness():
    regions = generate_regions()
    assert regions["region_id"].nunique() == 4
    assert regions["region_id"].isnull().sum() == 0


def test_regions_multiplier_positive():
    regions = generate_regions()
    assert (regions["parc_size_multiplier"] > 0).all()
    assert (regions["parc_size_multiplier"] <= 2.5).all()


def test_vehicle_segments_cardinality():
    segments = generate_vehicle_segments()
    assert len(segments) == 4
    assert segments["segment_id"].nunique() == 4


def test_vehicle_segments_mileage_positive():
    segments = generate_vehicle_segments()
    assert (segments["avg_annual_mileage_km"] > 0).all()
    assert (segments["maintenance_intensity"] > 0).all()


def test_products_generation_default_volume():
    products = generate_products(num_products=150, seed=42)
    assert len(products) == 150
    assert products["sku_id"].nunique() == 150


@pytest.mark.parametrize("n_prods", [10, 25, 50, 100, 200])
def test_products_configurable_scale(n_prods):
    products = generate_products(num_products=n_prods, seed=42)
    assert len(products) == n_prods
    assert products["sku_id"].nunique() == n_prods


def test_products_cost_and_list_price_relationship():
    products = generate_products(num_products=50, seed=42)
    assert (products["cost_price"] > 0).all()
    assert (products["list_price"] > products["cost_price"]).all()
    margins = (products["list_price"] - products["cost_price"]) / products["list_price"]
    assert (margins >= 0.20).all()
    assert (margins <= 0.60).all()


def test_products_lead_time_bounds():
    products = generate_products(num_products=50, seed=42)
    assert (products["standard_lead_time_days"] >= 7).all()
    assert (products["standard_lead_time_days"] <= 45).all()


def test_products_velocity_profile_values():
    products = generate_products(num_products=50, seed=42)
    valid_profiles = {"Fast Moving", "Medium Moving", "Slow Moving"}
    assert set(products["velocity_profile"].unique()).issubset(valid_profiles)


def test_products_category_values():
    products = generate_products(num_products=50, seed=42)
    valid_cats = {"Braking Systems", "Filtration", "Electrical & Ignition", "Chassis & Steering", "Thermal & Cooling"}
    assert set(products["product_category"].unique()).issubset(valid_cats)


def test_products_status_values():
    products = generate_products(num_products=50, seed=42)
    valid_status = {"Active", "Phase-Out"}
    assert set(products["product_status"].unique()).issubset(valid_status)


def test_distributors_generation():
    regions = generate_regions()
    distributors = generate_distributors(regions, num_distributors=20, seed=42)
    assert len(distributors) == 20
    assert distributors["distributor_id"].nunique() == 20
    assert set(distributors["region_id"]).issubset(set(regions["region_id"]))


def test_distributors_credit_terms():
    regions = generate_regions()
    distributors = generate_distributors(regions, num_distributors=20, seed=42)
    assert set(distributors["credit_term_days"].unique()).issubset({15, 30, 45})
    assert (distributors["annual_sales_target_inr"] > 0).all()


def test_workshops_generation():
    regions = generate_regions()
    workshops = generate_workshops(regions, num_workshops=120, seed=42)
    assert len(workshops) == 120
    assert workshops["workshop_id"].nunique() == 120
    assert set(workshops["region_id"]).issubset(set(regions["region_id"]))
    assert (workshops["monthly_demand_factor"] >= 0.4).all()
    assert (workshops["monthly_demand_factor"] <= 1.8).all()


def test_date_dimension_span():
    date_df = generate_date_dimension(start_date="2024-01-01", end_date="2025-12-31")
    assert len(date_df) == 731
    assert date_df["date"].min() == "2024-01-01"
    assert date_df["date"].max() == "2025-12-31"
    assert set(date_df["year"].unique()) == {2024, 2025}
    assert set(date_df["quarter"].unique()) == {"Q1", "Q2", "Q3", "Q4"}


@pytest.mark.parametrize("month,category,expected_min,expected_max", [
    (7, "Braking Systems", 1.15, 1.30),      # Monsoon peak
    (8, "Braking Systems", 1.15, 1.30),
    (5, "Thermal & Cooling", 1.25, 1.45),    # Summer cooling peak
    (1, "Electrical & Ignition", 1.05, 1.25),# Winter battery/starter peak
    (10, "Filtration", 1.10, 1.25),          # Festive service peak
])
def test_seasonal_factor_ranges(month, category, expected_min, expected_max):
    factor = get_seasonal_factor(month, category)
    assert expected_min <= factor <= expected_max


def test_seasonal_factor_unknown_category_fallback():
    assert get_seasonal_factor(6, "NonExistentCategory") == 1.0


def test_demand_profiles_structure():
    products = generate_products(num_products=10, seed=42)
    regions = generate_regions()
    demand = generate_demand_profiles(products, regions, start_date="2024-01-01", end_date="2024-03-31", seed=42)
    assert not demand.empty
    assert (demand["estimated_latent_demand"] > 0).all()
    assert set(demand["region_id"].unique()) == set(regions["region_id"])
    assert set(demand["sku_id"].unique()) == set(products["sku_id"])


def test_promotions_generation():
    products = generate_products(num_products=20, seed=42)
    regions = generate_regions()
    promotions = generate_promotions(products, regions, seed=42)
    assert len(promotions) == 16
    assert (promotions["discount_pct"] >= 0.05).all()
    assert (promotions["discount_pct"] <= 0.20).all()
    assert (promotions["budget_inr"] > 0).all()
    assert (promotions["start_date"] <= promotions["end_date"]).all()


def test_reproducibility_with_seed():
    p1 = generate_products(num_products=20, seed=99)
    p2 = generate_products(num_products=20, seed=99)
    pd.testing.assert_frame_equal(p1, p2)


def test_different_seed_different_products():
    p1 = generate_products(num_products=20, seed=1)
    p2 = generate_products(num_products=20, seed=2)
    assert not p1.equals(p2)
