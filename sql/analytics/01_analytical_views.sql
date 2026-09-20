-- ============================================================================
-- Automotive Aftermarket Sales & Trade Marketing Intelligence Platform
-- SQL Analytical Layer: Core Views, Aggregations, Window Functions & CTEs
-- ============================================================================

-- 1. VIEW: Monthly Sales & YoY Growth Intelligence
-- Reconciles monthly sales volume, net revenue, gross margin %, and prior-year comparisons.
DROP VIEW IF EXISTS v_monthly_sales_performance;
CREATE VIEW v_monthly_sales_performance AS
WITH monthly_agg AS (
    SELECT 
        s.year,
        s.month,
        s.year_month,
        d.month_name,
        d.quarter,
        COUNT(DISTINCT s.transaction_id) AS total_orders,
        COUNT(s.line_item_id) AS total_line_items,
        SUM(s.quantity) AS total_units_sold,
        ROUND(SUM(s.revenue), 2) AS total_revenue,
        ROUND(SUM(s.cost), 2) AS total_cost,
        ROUND(SUM(s.gross_profit), 2) AS total_gross_profit,
        ROUND((SUM(s.gross_profit) / NULLIF(SUM(s.revenue), 0)) * 100.0, 2) AS gross_margin_pct
    FROM fact_sales s
    JOIN dim_date d ON s.date = d.date
    GROUP BY s.year, s.month, s.year_month, d.month_name, d.quarter
),
yoy_calc AS (
    SELECT 
        curr.*,
        LAG(curr.total_revenue, 12) OVER (ORDER BY curr.year_month) AS prior_year_revenue,
        LAG(curr.total_units_sold, 12) OVER (ORDER BY curr.year_month) AS prior_year_units
    FROM monthly_agg curr
)
SELECT 
    year,
    month,
    year_month,
    month_name,
    quarter,
    total_orders,
    total_line_items,
    total_units_sold,
    total_revenue,
    total_cost,
    total_gross_profit,
    gross_margin_pct,
    prior_year_revenue,
    prior_year_units,
    CASE 
        WHEN prior_year_revenue IS NOT NULL AND prior_year_revenue > 0 
        THEN ROUND(((total_revenue - prior_year_revenue) / prior_year_revenue) * 100.0, 2)
        ELSE NULL 
    END AS yoy_revenue_growth_pct,
    CASE 
        WHEN prior_year_units IS NOT NULL AND prior_year_units > 0 
        THEN ROUND(((total_units_sold - prior_year_units) / CAST(prior_year_units AS NUMERIC)) * 100.0, 2)
        ELSE NULL 
    END AS yoy_units_growth_pct
FROM yoy_calc;

-- 2. VIEW: Category & Regional Contribution Mix
DROP VIEW IF EXISTS v_category_regional_mix;
CREATE VIEW v_category_regional_mix AS
WITH category_reg_summary AS (
    SELECT 
        s.year,
        r.region_id,
        r.region_name,
        p.product_category,
        SUM(s.quantity) AS units_sold,
        ROUND(SUM(s.revenue), 2) AS net_revenue,
        ROUND(SUM(s.gross_profit), 2) AS gross_profit
    FROM fact_sales s
    JOIN dim_region r ON s.region_id = r.region_id
    JOIN dim_product p ON s.sku_id = p.sku_id
    GROUP BY s.year, r.region_id, r.region_name, p.product_category
),
totals AS (
    SELECT 
        year,
        region_id,
        SUM(net_revenue) AS regional_total_revenue
    FROM category_reg_summary
    GROUP BY year, region_id
)
SELECT 
    c.year,
    c.region_id,
    c.region_name,
    c.product_category,
    c.units_sold,
    c.net_revenue,
    c.gross_profit,
    ROUND((c.gross_profit / NULLIF(c.net_revenue, 0)) * 100.0, 2) AS gross_margin_pct,
    ROUND((c.net_revenue / NULLIF(t.regional_total_revenue, 0)) * 100.0, 2) AS category_revenue_share_pct
FROM category_reg_summary c
JOIN totals t ON c.year = t.year AND c.region_id = t.region_id;

-- 3. VIEW: Distributor Commercial Performance & Growth Ranking
DROP VIEW IF EXISTS v_distributor_performance_ranking;
CREATE VIEW v_distributor_performance_ranking AS
WITH dist_yearly AS (
    SELECT 
        d.distributor_id,
        d.distributor_name,
        d.distributor_tier,
        r.region_name,
        s.year,
        COUNT(DISTINCT s.transaction_id) AS total_orders,
        SUM(s.quantity) AS units_sold,
        ROUND(SUM(s.revenue), 2) AS revenue,
        ROUND(SUM(s.gross_profit), 2) AS gross_profit
    FROM fact_sales s
    JOIN dim_distributor d ON s.distributor_id = d.distributor_id
    JOIN dim_region r ON d.region_id = r.region_id
    GROUP BY d.distributor_id, d.distributor_name, d.distributor_tier, r.region_name, s.year
),
pivoted AS (
    SELECT 
        distributor_id,
        distributor_name,
        distributor_tier,
        region_name,
        MAX(CASE WHEN year = 2024 THEN revenue ELSE 0 END) AS rev_2024,
        MAX(CASE WHEN year = 2025 THEN revenue ELSE 0 END) AS rev_2025,
        MAX(CASE WHEN year = 2025 THEN gross_profit ELSE 0 END) AS gp_2025,
        MAX(CASE WHEN year = 2025 THEN units_sold ELSE 0 END) AS units_2025
    FROM dist_yearly
    GROUP BY distributor_id, distributor_name, distributor_tier, region_name
)
SELECT 
    distributor_id,
    distributor_name,
    distributor_tier,
    region_name,
    rev_2024,
    rev_2025,
    gp_2025,
    ROUND((gp_2025 / NULLIF(rev_2025, 0)) * 100.0, 2) AS margin_pct_2025,
    units_2025,
    ROUND(((rev_2025 - rev_2024) / NULLIF(rev_2024, 0)) * 100.0, 2) AS yoy_growth_pct,
    RANK() OVER (ORDER BY rev_2025 DESC) AS national_revenue_rank,
    DENSE_RANK() OVER (PARTITION BY region_name ORDER BY rev_2025 DESC) AS regional_revenue_rank
FROM pivoted;

-- 4. VIEW: Trade Promotion Effectiveness & Net Incremental Profit
DROP VIEW IF EXISTS v_trade_promotion_evaluation;
CREATE VIEW v_trade_promotion_evaluation AS
SELECT 
    p.promotion_id,
    p.campaign_name,
    p.campaign_type,
    p.target_category,
    p.target_region,
    p.discount_pct,
    p.budget_inr,
    COUNT(s.line_item_id) AS promoted_order_lines,
    SUM(s.quantity) AS total_promoted_units,
    ROUND(SUM(s.revenue), 2) AS total_promoted_revenue,
    ROUND(SUM(s.gross_profit), 2) AS total_promoted_gross_profit,
    ROUND(SUM(s.quantity * (s.list_price - s.net_unit_price)), 2) AS total_discount_concession,
    ROUND((SUM(s.gross_profit) / NULLIF(SUM(s.revenue), 0)) * 100.0, 2) AS promoted_margin_pct
FROM dim_promotion p
LEFT JOIN fact_sales s ON p.promotion_id = s.promotion_id
GROUP BY 
    p.promotion_id, p.campaign_name, p.campaign_type, p.target_category,
    p.target_region, p.discount_pct, p.budget_inr;

-- 5. VIEW: Inventory Turnover & Stockout Exposure Summary
DROP VIEW IF EXISTS v_inventory_stockout_summary;
CREATE VIEW v_inventory_stockout_summary AS
SELECT 
    i.distributor_id,
    d.distributor_name,
    p.product_category,
    p.velocity_profile,
    COUNT(*) AS total_inventory_snapshots,
    SUM(i.stockout_flag) AS total_stockout_events,
    ROUND((SUM(i.stockout_flag) * 100.0) / COUNT(*), 2) AS stockout_frequency_pct,
    ROUND(AVG(i.closing_stock), 1) AS avg_closing_stock,
    SUM(i.units_sold) AS total_units_distributed,
    ROUND(AVG(i.lead_time_days), 1) AS avg_lead_time_days
FROM fact_inventory i
JOIN dim_distributor d ON i.distributor_id = d.distributor_id
JOIN dim_product p ON i.sku_id = p.sku_id
GROUP BY i.distributor_id, d.distributor_name, p.product_category, p.velocity_profile;
