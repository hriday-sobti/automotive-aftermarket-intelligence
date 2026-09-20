-- ============================================================================
-- Automotive Aftermarket Sales & Trade Marketing Intelligence Platform
-- DDL Schema Definition (PostgreSQL & SQLite compatible ANSI SQL)
-- ============================================================================

-- Drop tables if re-initializing
DROP TABLE IF EXISTS fact_promotion_performance;
DROP TABLE IF EXISTS fact_inventory;
DROP TABLE IF EXISTS fact_demand;
DROP TABLE IF EXISTS fact_sales;
DROP TABLE IF EXISTS dim_sku_pareto;
DROP TABLE IF EXISTS dim_promotion;
DROP TABLE IF EXISTS dim_workshop;
DROP TABLE IF EXISTS dim_distributor;
DROP TABLE IF EXISTS dim_product;
DROP TABLE IF EXISTS dim_vehicle_segment;
DROP TABLE IF EXISTS dim_region;
DROP TABLE IF EXISTS dim_date;

-- 1. DIM_DATE
CREATE TABLE dim_date (
    date VARCHAR(10) PRIMARY KEY,
    year INTEGER NOT NULL,
    quarter VARCHAR(2) NOT NULL,
    year_quarter VARCHAR(7) NOT NULL,
    month INTEGER NOT NULL,
    month_name VARCHAR(20) NOT NULL,
    year_month VARCHAR(7) NOT NULL,
    week_of_year INTEGER NOT NULL,
    day_of_month INTEGER NOT NULL,
    day_of_week INTEGER NOT NULL,
    day_name VARCHAR(15) NOT NULL,
    is_weekend INTEGER NOT NULL
);

-- 2. DIM_REGION
CREATE TABLE dim_region (
    region_id VARCHAR(10) PRIMARY KEY,
    region_name VARCHAR(50) NOT NULL,
    state_cluster VARCHAR(100) NOT NULL,
    market_tier VARCHAR(20) NOT NULL,
    parc_size_multiplier NUMERIC(4, 2) NOT NULL
);

-- 3. DIM_VEHICLE_SEGMENT
CREATE TABLE dim_vehicle_segment (
    segment_id VARCHAR(10) PRIMARY KEY,
    segment_name VARCHAR(50) NOT NULL,
    powertrain VARCHAR(30) NOT NULL,
    avg_annual_mileage_km INTEGER NOT NULL,
    maintenance_intensity NUMERIC(4, 2) NOT NULL
);

-- 4. DIM_PRODUCT
CREATE TABLE dim_product (
    sku_id VARCHAR(20) PRIMARY KEY,
    product_name VARCHAR(100) NOT NULL,
    product_category VARCHAR(50) NOT NULL,
    subcategory VARCHAR(50) NOT NULL,
    brand_tier VARCHAR(50) NOT NULL,
    vehicle_segment VARCHAR(10) NOT NULL,
    cost_price NUMERIC(10, 2) NOT NULL,
    list_price NUMERIC(10, 2) NOT NULL,
    standard_lead_time_days INTEGER NOT NULL,
    velocity_profile VARCHAR(20) NOT NULL,
    product_status VARCHAR(20) NOT NULL,
    FOREIGN KEY (vehicle_segment) REFERENCES dim_vehicle_segment(segment_id)
);

-- 5. DIM_DISTRIBUTOR
CREATE TABLE dim_distributor (
    distributor_id VARCHAR(10) PRIMARY KEY,
    distributor_name VARCHAR(100) NOT NULL,
    region_id VARCHAR(10) NOT NULL,
    distributor_tier VARCHAR(30) NOT NULL,
    credit_term_days INTEGER NOT NULL,
    annual_sales_target_inr NUMERIC(12, 2) NOT NULL,
    FOREIGN KEY (region_id) REFERENCES dim_region(region_id)
);

-- 6. DIM_WORKSHOP
CREATE TABLE dim_workshop (
    workshop_id VARCHAR(10) PRIMARY KEY,
    workshop_name VARCHAR(100) NOT NULL,
    region_id VARCHAR(10) NOT NULL,
    workshop_type VARCHAR(50) NOT NULL,
    monthly_demand_factor NUMERIC(4, 2) NOT NULL,
    FOREIGN KEY (region_id) REFERENCES dim_region(region_id)
);

-- 7. DIM_PROMOTION
CREATE TABLE dim_promotion (
    promotion_id VARCHAR(10) PRIMARY KEY,
    campaign_name VARCHAR(100) NOT NULL,
    campaign_type VARCHAR(50) NOT NULL,
    start_date VARCHAR(10) NOT NULL,
    end_date VARCHAR(10) NOT NULL,
    target_category VARCHAR(50) NOT NULL,
    target_region VARCHAR(10) NOT NULL,
    discount_pct NUMERIC(5, 4) NOT NULL,
    budget_inr NUMERIC(10, 2) NOT NULL,
    expected_uplift_pct NUMERIC(5, 4) NOT NULL,
    campaign_objective TEXT NOT NULL
);

-- 8. DIM_SKU_PARETO
CREATE TABLE dim_sku_pareto (
    sku_id VARCHAR(20) PRIMARY KEY,
    total_revenue NUMERIC(12, 2) NOT NULL,
    total_units INTEGER NOT NULL,
    total_gross_profit NUMERIC(12, 2) NOT NULL,
    cum_revenue NUMERIC(12, 2) NOT NULL,
    cum_revenue_pct NUMERIC(5, 2) NOT NULL,
    pareto_class VARCHAR(30) NOT NULL,
    FOREIGN KEY (sku_id) REFERENCES dim_product(sku_id)
);

-- 9. FACT_SALES (Grain: One row per transaction line item)
CREATE TABLE fact_sales (
    transaction_id VARCHAR(20) NOT NULL,
    line_item_id VARCHAR(25) PRIMARY KEY,
    date VARCHAR(10) NOT NULL,
    distributor_id VARCHAR(10) NOT NULL,
    workshop_id VARCHAR(10) NOT NULL,
    region_id VARCHAR(10) NOT NULL,
    sku_id VARCHAR(20) NOT NULL,
    quantity INTEGER NOT NULL,
    cost_price NUMERIC(10, 2) NOT NULL,
    list_price NUMERIC(10, 2) NOT NULL,
    discount_pct NUMERIC(5, 4) NOT NULL,
    net_unit_price NUMERIC(10, 2) NOT NULL,
    revenue NUMERIC(12, 2) NOT NULL,
    cost NUMERIC(12, 2) NOT NULL,
    gross_profit NUMERIC(12, 2) NOT NULL,
    promotion_id VARCHAR(10) NOT NULL,
    year INTEGER NOT NULL,
    month INTEGER NOT NULL,
    year_month VARCHAR(7) NOT NULL,
    quarter VARCHAR(2) NOT NULL,
    week_of_year INTEGER NOT NULL,
    gross_margin_pct NUMERIC(5, 2) NOT NULL,
    unit_cost NUMERIC(10, 2) NOT NULL,
    FOREIGN KEY (date) REFERENCES dim_date(date),
    FOREIGN KEY (distributor_id) REFERENCES dim_distributor(distributor_id),
    FOREIGN KEY (workshop_id) REFERENCES dim_workshop(workshop_id),
    FOREIGN KEY (region_id) REFERENCES dim_region(region_id),
    FOREIGN KEY (sku_id) REFERENCES dim_product(sku_id)
);

-- 10. FACT_INVENTORY (Grain: One row per SKU × Distributor × Observation Date)
CREATE TABLE fact_inventory (
    date VARCHAR(10) NOT NULL,
    distributor_id VARCHAR(10) NOT NULL,
    sku_id VARCHAR(20) NOT NULL,
    opening_stock INTEGER NOT NULL,
    receipts INTEGER NOT NULL,
    units_sold INTEGER NOT NULL,
    closing_stock INTEGER NOT NULL,
    lead_time_days INTEGER NOT NULL,
    stockout_flag INTEGER NOT NULL,
    PRIMARY KEY (date, distributor_id, sku_id),
    FOREIGN KEY (date) REFERENCES dim_date(date),
    FOREIGN KEY (distributor_id) REFERENCES dim_distributor(distributor_id),
    FOREIGN KEY (sku_id) REFERENCES dim_product(sku_id)
);

-- 11. FACT_DEMAND (Grain: One row per SKU × Region × Week)
CREATE TABLE fact_demand (
    week_start_date VARCHAR(10) NOT NULL,
    sku_id VARCHAR(20) NOT NULL,
    region_id VARCHAR(10) NOT NULL,
    vehicle_segment VARCHAR(10) NOT NULL,
    product_category VARCHAR(50) NOT NULL,
    seasonal_index NUMERIC(4, 2) NOT NULL,
    trend_factor NUMERIC(5, 3) NOT NULL,
    estimated_latent_demand NUMERIC(8, 1) NOT NULL,
    PRIMARY KEY (week_start_date, sku_id, region_id),
    FOREIGN KEY (sku_id) REFERENCES dim_product(sku_id),
    FOREIGN KEY (region_id) REFERENCES dim_region(region_id)
);

-- Performance Indexes
CREATE INDEX idx_sales_date ON fact_sales(date);
CREATE INDEX idx_sales_sku ON fact_sales(sku_id);
CREATE INDEX idx_sales_dist ON fact_sales(distributor_id);
CREATE INDEX idx_sales_reg ON fact_sales(region_id);
CREATE INDEX idx_sales_promo ON fact_sales(promotion_id);

CREATE INDEX idx_inv_date_sku ON fact_inventory(date, sku_id);
CREATE INDEX idx_inv_dist ON fact_inventory(distributor_id);
