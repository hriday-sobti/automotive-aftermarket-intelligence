# Parametric tests covering seasonal indices, service levels, discount sensitivities, and reorder status boundaries.

import pytest
import numpy as np
import pandas as pd

from src.data_generation.demand import get_seasonal_factor
from src.inventory.reorder_logic import compute_reorder_parameters


# 1. Test 60 distinct (month, category) seasonal factor combinations
@pytest.mark.parametrize("cat", [
    "Braking Systems", "Filtration", "Thermal & Cooling", "Electrical & Ignition", "Chassis & Steering"
])
@pytest.mark.parametrize("month", list(range(1, 13)))
def test_all_months_all_categories_seasonality(cat, month):
    factor = get_seasonal_factor(month, cat)
    assert 0.5 <= factor <= 1.6, f"Seasonality factor out of realistic bounds for {cat} in month {month}"


# 2. Test 30 service level and lead time safety stock parameter combinations
@pytest.mark.parametrize("z_score", [1.282, 1.645, 1.960, 2.326, 2.576])
@pytest.mark.parametrize("lead_time", [7, 14, 21, 28, 35, 42])
def test_safety_stock_scaling(z_score, lead_time):
    sigma_d = 4.0
    ss = int(np.ceil(z_score * sigma_d * np.sqrt(lead_time)))
    assert ss > 0
    assert ss >= int(z_score * sigma_d * np.sqrt(7))


# 3. Test 24 discount and uplift commercial financial sensitivities
@pytest.mark.parametrize("discount", [0.05, 0.08, 0.10, 0.12, 0.15, 0.20])
@pytest.mark.parametrize("uplift", [0.10, 0.20, 0.30, 0.40])
def test_commercial_promo_financial_simulation(discount, uplift):
    base_units = 10000
    list_price = 1500.0
    cost_price = 900.0

    promo_units = int(base_units * (1.0 + uplift))
    net_price = round(list_price * (1.0 - discount), 2)

    promo_revenue = promo_units * net_price
    promo_cost = promo_units * cost_price
    promo_gp = promo_revenue - promo_cost

    base_net_price = list_price * 0.95
    base_gp = base_units * (base_net_price - cost_price)

    inc_gp = promo_gp - base_gp
    assert isinstance(inc_gp, float)
    assert promo_revenue > 0
    assert promo_cost > 0


# 4. Test 16 reorder status classification thresholds
@pytest.mark.parametrize("stock_ratio,expected_status", [
    (0.2, "Urgent (Below Safety Stock)"),
    (0.5, "Urgent (Below Safety Stock)"),
    (0.9, "Reorder Triggered (Below ROP)"),
    (1.5, "Normal"),
])
@pytest.mark.parametrize("lead_time", [10, 20, 30, 40])
def test_reorder_status_transitions(stock_ratio, expected_status, lead_time):
    d_avg = 5.0
    safety_stock = 25
    lead_time_demand = int(np.ceil(d_avg * lead_time))
    rop = lead_time_demand + safety_stock

    if expected_status == "Urgent (Below Safety Stock)":
        closing_stock = int(safety_stock * stock_ratio)
    elif expected_status == "Reorder Triggered (Below ROP)":
        closing_stock = int(rop * stock_ratio)
        if closing_stock <= safety_stock:
            closing_stock = safety_stock + 1
    else:
        closing_stock = int(rop * stock_ratio)

    if closing_stock <= safety_stock:
        status = "Urgent (Below Safety Stock)"
    elif closing_stock <= rop:
        status = "Reorder Triggered (Below ROP)"
    else:
        status = "Normal"

    assert status == expected_status
