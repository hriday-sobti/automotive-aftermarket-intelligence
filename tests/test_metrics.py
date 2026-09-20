"""Comprehensive unit tests for commercial sales intelligence and promotion uplift metrics."""

import pytest
import numpy as np
import pandas as pd

from src.analytics.sales_analytics import (
    compute_executive_kpis,
    compute_category_intelligence,
    compute_distributor_growth
)
from src.cleaning.cleaning_pipeline import clean_and_engineer_sales, calculate_sku_pareto
from src.promotions.promotion_analytics import evaluate_promotions


def test_executive_kpis_normal_flow():
    sales = pd.DataFrame([
        {"year": 2024, "revenue": 1000.0, "cost": 600.0, "gross_profit": 400.0, "quantity": 10, "sku_id": "S1", "distributor_id": "D1"},
        {"year": 2025, "revenue": 1500.0, "cost": 900.0, "gross_profit": 600.0, "quantity": 15, "sku_id": "S2", "distributor_id": "D2"}
    ])
    kpis = compute_executive_kpis(sales)
    assert kpis["total_revenue"] == 2500.0
    assert kpis["total_cost"] == 1500.0
    assert kpis["total_gross_profit"] == 1000.0
    assert kpis["gross_margin_pct"] == 40.0
    assert kpis["yoy_revenue_growth_pct"] == 50.0
    assert kpis["active_skus"] == 2
    assert kpis["active_distributors"] == 2


def test_executive_kpis_zero_prior_year():
    sales = pd.DataFrame([
        {"year": 2025, "revenue": 1000.0, "cost": 600.0, "gross_profit": 400.0, "quantity": 10, "sku_id": "S1", "distributor_id": "D1"}
    ])
    kpis = compute_executive_kpis(sales)
    assert kpis["yoy_revenue_growth_pct"] == 0.0


def test_executive_kpis_negative_growth():
    sales = pd.DataFrame([
        {"year": 2024, "revenue": 2000.0, "cost": 1200.0, "gross_profit": 800.0, "quantity": 20, "sku_id": "S1", "distributor_id": "D1"},
        {"year": 2025, "revenue": 1000.0, "cost": 600.0, "gross_profit": 400.0, "quantity": 10, "sku_id": "S1", "distributor_id": "D1"}
    ])
    kpis = compute_executive_kpis(sales)
    assert kpis["yoy_revenue_growth_pct"] == -50.0


def test_clean_and_engineer_sales_attributes():
    sales = pd.DataFrame([{
        "date": "2024-06-15",
        "sku_id": "S1",
        "quantity": 10,
        "cost": 600.0,
        "revenue": 1000.0,
        "gross_profit": 400.0
    }])
    prods = pd.DataFrame({"sku_id": ["S1"]})
    cleaned = clean_and_engineer_sales(sales, prods)
    assert cleaned.iloc[0]["year"] == 2024
    assert cleaned.iloc[0]["month"] == 6
    assert cleaned.iloc[0]["year_month"] == "2024-06"
    assert cleaned.iloc[0]["quarter"] == "Q2"
    assert cleaned.iloc[0]["gross_margin_pct"] == 40.0
    assert cleaned.iloc[0]["unit_cost"] == 60.0


def test_pareto_tier_assignment_boundaries():
    # 10 SKUs with Pareto distribution
    data = []
    # 2 SKUs with 80% revenue
    data.append({"sku_id": "S1", "revenue": 50000.0, "quantity": 500, "gross_profit": 20000.0})
    data.append({"sku_id": "S2", "revenue": 30000.0, "quantity": 300, "gross_profit": 12000.0})
    # 3 SKUs with next 15% revenue
    data.append({"sku_id": "S3", "revenue": 8000.0, "quantity": 80, "gross_profit": 3200.0})
    data.append({"sku_id": "S4", "revenue": 4000.0, "quantity": 40, "gross_profit": 1600.0})
    data.append({"sku_id": "S5", "revenue": 3000.0, "quantity": 30, "gross_profit": 1200.0})
    # 5 SKUs with remaining 5%
    for i in range(6, 11):
        data.append({"sku_id": f"S{i}", "revenue": 1000.0, "quantity": 10, "gross_profit": 400.0})

    pareto = calculate_sku_pareto(pd.DataFrame(data))
    assert set(pareto["pareto_class"].unique()) == {"Class A (Top 80% Rev)", "Class B (Next 15% Rev)", "Class C (Bottom 5% Rev)"}
    assert pareto[pareto["sku_id"] == "S1"]["pareto_class"].iloc[0] == "Class A (Top 80% Rev)"
    assert pareto[pareto["sku_id"] == "S10"]["pareto_class"].iloc[0] == "Class C (Bottom 5% Rev)"


def test_category_intelligence_aggregations():
    sales = pd.DataFrame([
        {"sku_id": "S1", "revenue": 1000.0, "gross_profit": 400.0, "quantity": 10},
        {"sku_id": "S2", "revenue": 2000.0, "gross_profit": 900.0, "quantity": 20}
    ])
    prods = pd.DataFrame([
        {"sku_id": "S1", "product_category": "Braking Systems"},
        {"sku_id": "S2", "product_category": "Filtration"}
    ])
    res = compute_category_intelligence(sales, prods)
    assert len(res) == 2
    assert res.iloc[0]["product_category"] == "Filtration"
    assert res.iloc[0]["revenue_share_pct"] == round((2000.0 / 3000.0) * 100, 2)


def test_distributor_growth_attainment():
    sales = pd.DataFrame([
        {"distributor_id": "D1", "year": 2024, "revenue": 100000.0, "gross_profit": 35000.0, "quantity": 1000},
        {"distributor_id": "D1", "year": 2025, "revenue": 120000.0, "gross_profit": 42000.0, "quantity": 1200}
    ])
    dists = pd.DataFrame([{
        "distributor_id": "D1",
        "distributor_name": "Dist 1",
        "region_id": "R1",
        "distributor_tier": "Tier 1 Platinum",
        "credit_term_days": 45,
        "annual_sales_target_inr": 150000.0
    }])
    res = compute_distributor_growth(sales, dists)
    assert res.iloc[0]["yoy_revenue_growth_pct"] == 20.0
    assert res.iloc[0]["target_attainment_pct"] == 80.0


def test_promotion_evaluation_value_accretive():
    dates_base = pd.date_range("2024-05-01", periods=30, freq="D").strftime("%Y-%m-%d").tolist()
    base_rows = [
        {"date": d, "sku_id": "S1", "region_id": "R1", "quantity": 10, "list_price": 100.0, "net_unit_price": 95.0, "revenue": 950.0, "gross_profit": 450.0, "promotion_id": "NONE"}
        for d in dates_base
    ]
    dates_promo = pd.date_range("2024-06-01", periods=30, freq="D").strftime("%Y-%m-%d").tolist()
    promo_rows = [
        {"date": d, "sku_id": "S1", "region_id": "R1", "quantity": 25, "list_price": 100.0, "net_unit_price": 92.0, "revenue": 2300.0, "gross_profit": 1100.0, "promotion_id": "P1"}
        for d in dates_promo
    ]
    sales = pd.DataFrame(base_rows + promo_rows)
    promos = pd.DataFrame([{
        "promotion_id": "P1",
        "campaign_name": "Test Promo",
        "campaign_type": "Seasonal",
        "target_category": "Braking Systems",
        "target_region": "R1",
        "start_date": "2024-06-01",
        "end_date": "2024-06-30",
        "discount_pct": 0.08,
        "budget_inr": 2000.0
    }])
    prods = pd.DataFrame([{"sku_id": "S1", "product_category": "Braking Systems"}])

    eval_df = evaluate_promotions(sales, promos, prods)
    assert len(eval_df) == 1
    assert eval_df.iloc[0]["promotion_id"] == "P1"
    assert eval_df.iloc[0]["incremental_units"] > 0
    assert eval_df.iloc[0]["incremental_gross_profit_inr"] > 0
    assert eval_df.iloc[0]["promotion_effectiveness_index"] > 0
