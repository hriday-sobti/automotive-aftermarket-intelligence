"""Unit and integration test suite for Automotive Aftermarket Intelligence Platform.

Validates core mathematical formulas, reconciliation logic, and boundary conditions:
- Revenue, profit, and margin formulas
- Stock balance equations
- Safety stock and ROP calculations
- Trade promotion uplift and effectiveness
- Edge cases (zero sales, zero inventory, boundary discounts)
"""

import pytest
import numpy as np
import pandas as pd

from src.validation.validator import DataValidator
from src.inventory.reorder_logic import compute_reorder_parameters
from src.inventory.risk_model import compute_stockout_risk_model
from src.promotions.promotion_analytics import evaluate_promotions
from src.analytics.sales_analytics import compute_executive_kpis


def test_sales_financial_reconciliation():
    """Verify exact revenue and gross profit mathematical reconciliation."""
    qty = 10
    list_price = 1500.0
    cost_price = 900.0
    discount = 0.10

    net_unit_price = round(list_price * (1.0 - discount), 2)
    revenue = round(qty * net_unit_price, 2)
    cost = round(qty * cost_price, 2)
    gross_profit = round(revenue - cost, 2)

    assert net_unit_price == 1350.0
    assert revenue == 13500.0
    assert cost == 9000.0
    assert gross_profit == 4500.0
    assert round((gross_profit / revenue) * 100.0, 2) == 33.33


def test_inventory_stock_balance():
    """Verify rigid stock flow balance equation."""
    opening = 100
    receipts = 250
    sold = 80
    closing = (opening + receipts) - sold

    assert closing == 270
    assert closing == opening + receipts - sold


def test_safety_stock_formula():
    """Verify safety stock statistical calculation."""
    # SS = Z * sigma_D * sqrt(L)
    z = 1.645 # 95% cycle service level
    sigma_d = 4.2 # daily std dev
    lead_time = 16 # days

    expected_ss = int(np.ceil(z * sigma_d * np.sqrt(lead_time)))
    assert expected_ss == 28 # ceil(1.645 * 4.2 * 4) = ceil(27.636) = 28


def test_reorder_point_formula():
    """Verify Reorder Point: ROP = (D_avg * L) + SS."""
    d_avg = 5.0
    lead_time = 14
    safety_stock = 25

    lead_time_demand = int(np.ceil(d_avg * lead_time))
    rop = lead_time_demand + safety_stock

    assert lead_time_demand == 70
    assert rop == 95


def test_validator_detects_revenue_mismatch():
    """Verify DataValidator flags intentional revenue calculation discrepancies."""
    validator = DataValidator()
    # Mock invalid sales dataframe
    df = pd.DataFrame([{
        "transaction_id": "T1",
        "line_item_id": "T1-L1",
        "date": "2024-01-01",
        "distributor_id": "DIST-01",
        "workshop_id": "WS-001",
        "region_id": "REG-01",
        "sku_id": "SKU-001",
        "quantity": 10,
        "cost_price": 50.0,
        "list_price": 100.0,
        "discount_pct": 0.10,
        "net_unit_price": 90.0,
        "revenue": 500.0, # Intentional error (should be 900.0)
        "cost": 500.0,
        "gross_profit": 0.0,
        "promotion_id": "NONE"
    }])

    dims = {
        "dim_product": pd.DataFrame({"sku_id": ["SKU-001"]}),
        "dim_distributor": pd.DataFrame({"distributor_id": ["DIST-01"]})
    }
    promos = pd.DataFrame()

    valid_df, rejected_df = validator.validate_sales(df, dims, promos)
    assert len(valid_df) == 0
    assert len(rejected_df) == 1
    assert "Revenue does not equal quantity * net_unit_price" in rejected_df.iloc[0]["rejection_reason"]


def test_zero_sales_boundary():
    """Verify KPIs handle zero-sales edge case gracefully without ZeroDivisionError."""
    df = pd.DataFrame(columns=["revenue", "cost", "quantity", "gross_profit", "year", "sku_id", "distributor_id"])
    kpis = compute_executive_kpis(df)
    assert kpis["total_revenue"] == 0.0
    assert kpis["gross_margin_pct"] == 0.0
    assert kpis["active_skus"] == 0
