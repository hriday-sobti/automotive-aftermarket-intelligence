# Unit tests for the opportunity matrix classification and decision simulator lookups.

import pytest
import pandas as pd
from src.analytics.opportunity_matrix import compute_sku_opportunity_matrix
from src.analytics.decision_simulator import ManagerDecisionSimulator


@pytest.fixture
def opp_matrix_test_data():
    sales = pd.DataFrame([
        # SKU 1: High Sales, High Growth
        {"sku_id": "SKU-1", "year": 2024, "revenue": 100000.0, "gross_profit": 40000.0, "quantity": 1000},
        {"sku_id": "SKU-1", "year": 2025, "revenue": 150000.0, "gross_profit": 60000.0, "quantity": 1500},
        # SKU 2: High Sales, Low Growth
        {"sku_id": "SKU-2", "year": 2024, "revenue": 200000.0, "gross_profit": 70000.0, "quantity": 2000},
        {"sku_id": "SKU-2", "year": 2025, "revenue": 205000.0, "gross_profit": 72000.0, "quantity": 2050},
        # SKU 3: Low Sales, High Growth
        {"sku_id": "SKU-3", "year": 2024, "revenue": 10000.0, "gross_profit": 3500.0, "quantity": 100},
        {"sku_id": "SKU-3", "year": 2025, "revenue": 30000.0, "gross_profit": 10500.0, "quantity": 300},
        # SKU 4: Low Sales, Low Growth
        {"sku_id": "SKU-4", "year": 2024, "revenue": 15000.0, "gross_profit": 5000.0, "quantity": 150},
        {"sku_id": "SKU-4", "year": 2025, "revenue": 12000.0, "gross_profit": 4000.0, "quantity": 120},
    ])
    products = pd.DataFrame([
        {"sku_id": "SKU-1", "product_name": "Pad 1", "product_category": "Braking Systems", "velocity_profile": "Fast Moving"},
        {"sku_id": "SKU-2", "product_name": "Pad 2", "product_category": "Braking Systems", "velocity_profile": "Fast Moving"},
        {"sku_id": "SKU-3", "product_name": "Filter 1", "product_category": "Filtration", "velocity_profile": "Medium Moving"},
        {"sku_id": "SKU-4", "product_name": "Strut 1", "product_category": "Chassis & Steering", "velocity_profile": "Slow Moving"},
    ])
    return sales, products


def test_opportunity_matrix_quadrant_segmentation(opp_matrix_test_data):
    sales, products = opp_matrix_test_data
    matrix = compute_sku_opportunity_matrix(sales, products)

    assert len(matrix) == 4
    quads = set(matrix["opportunity_quadrant"].unique())
    assert "High Sales / High Growth (Core Champions)" in quads
    assert "High Sales / Low Growth (Cash Cows)" in quads
    assert "Low Sales / High Growth (Emerging Stars)" in quads
    assert "Low Sales / Low Growth (Under Review)" in quads


def test_opportunity_matrix_recommendations(opp_matrix_test_data):
    sales, products = opp_matrix_test_data
    matrix = compute_sku_opportunity_matrix(sales, products)

    for _, row in matrix.iterrows():
        assert row["strategic_recommendation"] != ""
        if "Core Champions" in row["opportunity_quadrant"]:
            assert "Protect stock" in row["strategic_recommendation"]
        elif "Under Review" in row["opportunity_quadrant"]:
            assert "Audit catalog" in row["strategic_recommendation"]


def test_manager_decision_simulator_real_data():
    sim = ManagerDecisionSimulator()
    res = sim.query_sku_distributor("DIST-01", "SKU-BRA-0012")

    expected_keys = {
        "distributor_id", "distributor_name", "region", "sku_id", "product_name",
        "product_category", "velocity_profile", "current_stock", "days_of_inventory",
        "daily_velocity_units", "revenue_2025_inr", "gross_margin_pct_2025",
        "yoy_revenue_growth_pct", "lead_time_days", "stockout_risk_category",
        "primary_driver", "recommended_action"
    }
    assert set(res.keys()) == expected_keys
    assert res["distributor_id"] == "DIST-01"
    assert res["sku_id"] == "SKU-BRA-0012"
    assert res["current_stock"] >= 0
    assert res["revenue_2025_inr"] >= 0
    assert res["stockout_risk_category"] in {"Low Risk", "Watch", "High Risk", "Critical"}


@pytest.mark.parametrize("dist_id,sku_id", [
    ("DIST-01", "SKU-BRA-0002"),
    ("DIST-02", "SKU-FIL-0011"),
    ("DIST-03", "SKU-ELE-0008"),
    ("DIST-04", "SKU-CHA-0001"),
    ("DIST-05", "SKU-THE-0004"),
])
def test_manager_simulator_multiple_lookups(dist_id, sku_id):
    sim = ManagerDecisionSimulator()
    res = sim.query_sku_distributor(dist_id, sku_id)
    assert res["distributor_id"] == dist_id
    assert res["sku_id"] == sku_id
    assert res["product_name"] != ""
