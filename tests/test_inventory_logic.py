# Unit tests for inventory sizing, safety stock, ROP, and risk scoring.

import pytest
import numpy as np
import pandas as pd

from src.inventory.reorder_logic import compute_reorder_parameters
from src.inventory.risk_model import compute_stockout_risk_model
from src.utils.config_utils import load_config


@pytest.fixture
def inventory_test_env():
    config = load_config()
    dates = pd.date_range("2024-01-01", periods=90, freq="D").strftime("%Y-%m-%d").tolist()

    sales_rows = []
    for d in dates:
        sales_rows.append({
            "date": d,
            "distributor_id": "DIST-01",
            "sku_id": "SKU-01",
            "quantity": 10,
            "revenue": 1000.0,
            "gross_profit": 400.0
        })
    sales_df = pd.DataFrame(sales_rows)

    inv_rows = []
    curr = 150
    for d in dates:
        curr = max(0, curr - 10)
        inv_rows.append({
            "date": d,
            "distributor_id": "DIST-01",
            "sku_id": "SKU-01",
            "opening_stock": curr + 10,
            "receipts": 0,
            "units_sold": 10,
            "closing_stock": curr,
            "lead_time_days": 15,
            "stockout_flag": 1 if curr == 0 else 0
        })
    inv_df = pd.DataFrame(inv_rows)

    products_df = pd.DataFrame([{
        "sku_id": "SKU-01",
        "product_name": "Brake Pad Front",
        "product_category": "Braking Systems",
        "standard_lead_time_days": 15,
        "velocity_profile": "Fast Moving"
    }])
    distributors_df = pd.DataFrame([{
        "distributor_id": "DIST-01",
        "distributor_name": "Apex Dist",
        "region_id": "REG-01"
    }])

    return sales_df, inv_df, products_df, distributors_df, config


@pytest.mark.parametrize("z,sigma_d,lead_time,expected_min", [
    (1.645, 2.0, 10, 10),
    (1.645, 5.0, 16, 32),
    (1.960, 4.0, 25, 39),
    (2.326, 6.0, 36, 83),
])
def test_safety_stock_parameter_matrix(z, sigma_d, lead_time, expected_min):
    ss = int(np.ceil(z * sigma_d * np.sqrt(lead_time)))
    assert ss >= expected_min


@pytest.mark.parametrize("d_avg,lead_time,safety_stock,expected_rop", [
    (5.0, 10, 20, 70),
    (10.0, 15, 35, 185),
    (2.5, 20, 15, 65),
    (20.0, 30, 100, 700),
])
def test_reorder_point_parameter_matrix(d_avg, lead_time, safety_stock, expected_rop):
    lead_demand = int(np.ceil(d_avg * lead_time))
    rop = lead_demand + safety_stock
    assert rop == expected_rop


def test_reorder_parameters_function_output(inventory_test_env):
    sales_df, inv_df, prods_df, _, _ = inventory_test_env
    res = compute_reorder_parameters(sales_df, inv_df, prods_df, service_level_z=1.645)

    assert len(res) == 1
    row = res.iloc[0]
    assert row["sku_id"] == "SKU-01"
    assert row["safety_stock"] >= 0
    assert row["reorder_point"] >= row["safety_stock"]
    assert row["recommended_order_qty"] >= 0
    assert row["reorder_status"] in {"Normal", "Reorder Triggered (Below ROP)", "Urgent (Below Safety Stock)"}


def test_stockout_risk_model_scoring_bounds(inventory_test_env):
    sales_df, inv_df, prods_df, dists_df, config = inventory_test_env
    risk_df = compute_stockout_risk_model(sales_df, inv_df, prods_df, dists_df, config)

    assert len(risk_df) == 1
    row = risk_df.iloc[0]
    assert 0.0 <= row["stockout_risk_score"] <= 100.0
    assert row["risk_category"] in {"Low Risk", "Watch", "High Risk", "Critical"}
    assert row["primary_risk_driver"] != ""
    assert row["recommended_action"] != ""


def test_stockout_risk_critical_when_zero_stock(inventory_test_env):
    sales_df, inv_df, prods_df, dists_df, config = inventory_test_env
    # Force zero closing stock on latest snapshot
    inv_df.loc[inv_df.index[-1], "closing_stock"] = 0
    risk_df = compute_stockout_risk_model(sales_df, inv_df, prods_df, dists_df, config)
    # Coverage score should be maximum (100)
    assert risk_df.iloc[0]["closing_stock"] == 0
    assert risk_df.iloc[0]["days_of_inventory"] == 0.0


def test_stockout_risk_low_when_ample_inventory(inventory_test_env):
    sales_df, inv_df, prods_df, dists_df, config = inventory_test_env
    # Force high stock
    inv_df.loc[inv_df.index[-1], "closing_stock"] = 5000
    risk_df = compute_stockout_risk_model(sales_df, inv_df, prods_df, dists_df, config)
    assert risk_df.iloc[0]["days_of_inventory"] > 100.0
    assert risk_df.iloc[0]["risk_category"] in {"Low Risk", "Watch"}
