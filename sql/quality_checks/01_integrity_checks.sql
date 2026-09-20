-- ============================================================================
-- Automotive Aftermarket Sales & Trade Marketing Intelligence Platform
-- SQL Quality & Integrity Verification Suite
-- ============================================================================

-- Check 1: Verify Zero Orphan SKUs in Sales
SELECT 
    'Orphan SKUs in FACT_SALES' AS test_name,
    COUNT(*) AS failure_count
FROM fact_sales s
LEFT JOIN dim_product p ON s.sku_id = p.sku_id
WHERE p.sku_id IS NULL;

-- Check 2: Verify Revenue Reconciliation in Sales
SELECT 
    'Revenue Mismatch (>0.05 tolerance)' AS test_name,
    COUNT(*) AS failure_count
FROM fact_sales
WHERE ABS(revenue - ROUND(quantity * net_unit_price, 2)) > 0.05;

-- Check 3: Verify Gross Profit Reconciliation
SELECT 
    'Gross Profit Mismatch (>0.05 tolerance)' AS test_name,
    COUNT(*) AS failure_count
FROM fact_sales
WHERE ABS(gross_profit - ROUND(revenue - cost, 2)) > 0.05;

-- Check 4: Verify Inventory Stock Balance Equation
SELECT 
    'Inventory Equation Mismatch' AS test_name,
    COUNT(*) AS failure_count
FROM fact_inventory
WHERE closing_stock != (opening_stock + receipts - units_sold);

-- Check 5: Verify Non-Negative Closing Inventory
SELECT 
    'Negative Closing Stock' AS test_name,
    COUNT(*) AS failure_count
FROM fact_inventory
WHERE closing_stock < 0;

-- Check 6: Verify Date Dimension Consistency
SELECT 
    'Missing Dates in Sales vs Calendar' AS test_name,
    COUNT(*) AS failure_count
FROM fact_sales s
LEFT JOIN dim_date d ON s.date = d.date
WHERE d.date IS NULL;
