-- ============================================================================
-- SQL Staging Tables: Raw CSV Data Loading Buffer Layer
-- ============================================================================

DROP TABLE IF EXISTS stg_raw_sales;
CREATE TABLE stg_raw_sales (
    transaction_id VARCHAR(50),
    line_item_id VARCHAR(50),
    date VARCHAR(20),
    distributor_id VARCHAR(20),
    workshop_id VARCHAR(20),
    region_id VARCHAR(20),
    sku_id VARCHAR(50),
    quantity INTEGER,
    cost_price NUMERIC(10,2),
    list_price NUMERIC(10,2),
    discount_pct NUMERIC(5,4),
    net_unit_price NUMERIC(10,2),
    revenue NUMERIC(12,2),
    cost NUMERIC(12,2),
    gross_profit NUMERIC(12,2),
    promotion_id VARCHAR(20)
);

DROP TABLE IF EXISTS stg_raw_inventory;
CREATE TABLE stg_raw_inventory (
    date VARCHAR(20),
    distributor_id VARCHAR(20),
    sku_id VARCHAR(50),
    opening_stock INTEGER,
    receipts INTEGER,
    units_sold INTEGER,
    closing_stock INTEGER,
    lead_time_days INTEGER,
    stockout_flag INTEGER
);
