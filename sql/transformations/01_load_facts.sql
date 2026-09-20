-- ============================================================================
-- SQL Transformations: Staging to Star-Schema Fact & Dimension Pipelines
-- ============================================================================

-- Transform Staged Sales into FACT_SALES with temporal derivations and checks
INSERT OR REPLACE INTO fact_sales (
    transaction_id,
    line_item_id,
    date,
    distributor_id,
    workshop_id,
    region_id,
    sku_id,
    quantity,
    cost_price,
    list_price,
    discount_pct,
    net_unit_price,
    revenue,
    cost,
    gross_profit,
    promotion_id,
    year,
    month,
    year_month,
    quarter,
    week_of_year,
    gross_margin_pct,
    unit_cost
)
SELECT
    s.transaction_id,
    s.line_item_id,
    s.date,
    s.distributor_id,
    s.workshop_id,
    s.region_id,
    s.sku_id,
    s.quantity,
    s.cost_price,
    s.list_price,
    s.discount_pct,
    s.net_unit_price,
    s.revenue,
    s.cost,
    s.gross_profit,
    s.promotion_id,
    CAST(SUBSTR(s.date, 1, 4) AS INTEGER) AS year,
    CAST(SUBSTR(s.date, 6, 2) AS INTEGER) AS month,
    SUBSTR(s.date, 1, 7) AS year_month,
    'Q' || (((CAST(SUBSTR(s.date, 6, 2) AS INTEGER) - 1) / 3) + 1) AS quarter,
    d.week_of_year,
    ROUND((s.gross_profit / NULLIF(s.revenue, 0)) * 100.0, 2) AS gross_margin_pct,
    ROUND(s.cost / NULLIF(s.quantity, 0), 2) AS unit_cost
FROM stg_raw_sales s
JOIN dim_date d ON s.date = d.date;

-- Transform Staged Inventory into FACT_INVENTORY
INSERT OR REPLACE INTO fact_inventory (
    date,
    distributor_id,
    sku_id,
    opening_stock,
    receipts,
    units_sold,
    closing_stock,
    lead_time_days,
    stockout_flag
)
SELECT
    date,
    distributor_id,
    sku_id,
    opening_stock,
    receipts,
    units_sold,
    closing_stock,
    lead_time_days,
    stockout_flag
FROM stg_raw_inventory;
