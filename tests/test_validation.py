"""Comprehensive unit tests for data validation, assertions, and reject logging."""

import pytest
import pandas as pd
from src.validation.validator import DataValidator


@pytest.fixture
def clean_test_data():
    dims = {
        "dim_region": pd.DataFrame({"region_id": ["REG-01", "REG-02"]}),
        "dim_vehicle_segment": pd.DataFrame({"segment_id": ["SEG-01"]}),
        "dim_product": pd.DataFrame({"sku_id": ["SKU-01", "SKU-02"]}),
        "dim_distributor": pd.DataFrame({"distributor_id": ["DIST-01"]}),
        "dim_workshop": pd.DataFrame({"workshop_id": ["WS-01"]}),
        "dim_date": pd.DataFrame({"date": ["2024-01-01", "2024-01-02"]})
    }
    sales = pd.DataFrame([{
        "transaction_id": "T1",
        "line_item_id": "T1-L1",
        "date": "2024-01-01",
        "distributor_id": "DIST-01",
        "workshop_id": "WS-01",
        "region_id": "REG-01",
        "sku_id": "SKU-01",
        "quantity": 10,
        "cost_price": 50.0,
        "list_price": 100.0,
        "discount_pct": 0.10,
        "net_unit_price": 90.0,
        "revenue": 900.0,
        "cost": 500.0,
        "gross_profit": 400.0,
        "promotion_id": "NONE"
    }])
    inventory = pd.DataFrame([{
        "date": "2024-01-01",
        "distributor_id": "DIST-01",
        "sku_id": "SKU-01",
        "opening_stock": 100,
        "receipts": 50,
        "units_sold": 20,
        "closing_stock": 130,
        "lead_time_days": 15,
        "stockout_flag": 0
    }])
    return dims, sales, inventory


def test_validator_passes_clean_data(clean_test_data):
    dims, sales, inventory = clean_test_data
    v = DataValidator()
    assert v.validate_dimensions(dims)
    valid_sales, rejected_sales = v.validate_sales(sales, dims, pd.DataFrame())
    assert len(valid_sales) == 1
    assert len(rejected_sales) == 0
    assert v.validate_inventory(inventory)


def test_validator_detects_null_pk(clean_test_data):
    dims, _, _ = clean_test_data
    dims["dim_product"] = pd.DataFrame({"sku_id": ["SKU-01", None]})
    v = DataValidator()
    assert not v.validate_dimensions(dims)


def test_validator_detects_duplicate_pk(clean_test_data):
    dims, _, _ = clean_test_data
    dims["dim_region"] = pd.DataFrame({"region_id": ["REG-01", "REG-01"]})
    v = DataValidator()
    assert not v.validate_dimensions(dims)


def test_validator_rejects_negative_quantity(clean_test_data):
    dims, sales, _ = clean_test_data
    sales.loc[0, "quantity"] = -5
    v = DataValidator()
    valid, rej = v.validate_sales(sales, dims, pd.DataFrame())
    assert len(valid) == 0
    assert "Non-positive quantity" in rej.iloc[0]["rejection_reason"]


def test_validator_rejects_zero_quantity(clean_test_data):
    dims, sales, _ = clean_test_data
    sales.loc[0, "quantity"] = 0
    v = DataValidator()
    valid, rej = v.validate_sales(sales, dims, pd.DataFrame())
    assert len(valid) == 0
    assert "Non-positive quantity" in rej.iloc[0]["rejection_reason"]


def test_validator_rejects_negative_discount(clean_test_data):
    dims, sales, _ = clean_test_data
    sales.loc[0, "discount_pct"] = -0.05
    v = DataValidator()
    valid, rej = v.validate_sales(sales, dims, pd.DataFrame())
    assert len(valid) == 0
    assert "Discount percentage out of bounds" in rej.iloc[0]["rejection_reason"]


def test_validator_rejects_excessive_discount(clean_test_data):
    dims, sales, _ = clean_test_data
    sales.loc[0, "discount_pct"] = 0.60 # > 0.50
    v = DataValidator()
    valid, rej = v.validate_sales(sales, dims, pd.DataFrame())
    assert len(valid) == 0
    assert "Discount percentage out of bounds" in rej.iloc[0]["rejection_reason"]


def test_validator_rejects_revenue_mismatch(clean_test_data):
    dims, sales, _ = clean_test_data
    sales.loc[0, "revenue"] = 950.0 # Expected 900.0 (10 * 90.0)
    v = DataValidator()
    valid, rej = v.validate_sales(sales, dims, pd.DataFrame())
    assert len(valid) == 0
    assert "Revenue does not equal quantity * net_unit_price" in rej.iloc[0]["rejection_reason"]


def test_validator_allows_minor_rounding_tolerance(clean_test_data):
    dims, sales, _ = clean_test_data
    # 0.02 deviation is within 0.05 tolerance
    sales.loc[0, "revenue"] = 900.02
    sales.loc[0, "gross_profit"] = 400.02
    v = DataValidator()
    valid, rej = v.validate_sales(sales, dims, pd.DataFrame())
    assert len(valid) == 1
    assert len(rej) == 0


def test_validator_rejects_gross_profit_mismatch(clean_test_data):
    dims, sales, _ = clean_test_data
    sales.loc[0, "gross_profit"] = 350.0 # Expected 400.0 (900 - 500)
    v = DataValidator()
    valid, rej = v.validate_sales(sales, dims, pd.DataFrame())
    assert len(valid) == 0
    assert "Gross profit does not equal revenue - cost" in rej.iloc[0]["rejection_reason"]


def test_validator_rejects_orphan_sku(clean_test_data):
    dims, sales, _ = clean_test_data
    sales.loc[0, "sku_id"] = "NON-EXISTENT-SKU"
    v = DataValidator()
    valid, rej = v.validate_sales(sales, dims, pd.DataFrame())
    assert len(valid) == 0
    assert "Orphan SKU foreign key" in rej.iloc[0]["rejection_reason"]


def test_validator_rejects_orphan_distributor(clean_test_data):
    dims, sales, _ = clean_test_data
    sales.loc[0, "distributor_id"] = "DIST-999"
    v = DataValidator()
    valid, rej = v.validate_sales(sales, dims, pd.DataFrame())
    assert len(valid) == 0
    assert "Orphan Distributor foreign key" in rej.iloc[0]["rejection_reason"]


def test_validator_rejects_inventory_balance_mismatch(clean_test_data):
    _, _, inventory = clean_test_data
    # 100 + 50 - 20 = 130, set to 140
    inventory.loc[0, "closing_stock"] = 140
    v = DataValidator()
    assert not v.validate_inventory(inventory)


def test_validator_rejects_negative_closing_inventory(clean_test_data):
    _, _, inventory = clean_test_data
    # Sold more than opening + receipts
    inventory.loc[0, "units_sold"] = 200
    inventory.loc[0, "closing_stock"] = -50
    v = DataValidator()
    assert not v.validate_inventory(inventory)


def test_validation_summary_report_generation(clean_test_data):
    dims, sales, inventory = clean_test_data
    v = DataValidator()
    v.validate_dimensions(dims)
    v.validate_sales(sales, dims, pd.DataFrame())
    v.validate_inventory(inventory)
    report = v.get_summary_report()
    assert not report.empty
    assert "status" in report.columns
    assert (report["status"] == "PASS").all()
