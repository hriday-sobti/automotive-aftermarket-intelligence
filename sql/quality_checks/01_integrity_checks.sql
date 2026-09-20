-- SQL data integrity and mathematical reconciliation assertions.

-- Check 1: Zero orphan SKUs in sales
SELECT 
    'Orphan SKUs in FACT_SALES' AS test_name,
    COUNT(*) AS failure_count
FROM fact_sales s
LEFT JOIN dim_product p ON s.sku_id = p.sku_id
WHERE p.sku_id IS NULL;

-- Check 2: Revenue equals quantity * net unit price
SELECT 
    'Revenue Mismatch (>0.05 tolerance)' AS test_name,
    COUNT(*) AS failure_count
FROM fact_sales
WHERE ABS(revenue - ROUND(quantity * net_unit_price, 2)) > 0.05;

-- Check 3: Gross profit equals revenue - cost
SELECT 
    'Gross Profit Mismatch (>0.05 tolerance)' AS test_name,
    COUNT(*) AS failure_count
FROM fact_sales
WHERE ABS(gross_profit - ROUND(revenue - cost, 2)) > 0.05;

-- Check 4: Inventory stock balance equation
SELECT 
    'Inventory Equation Mismatch' AS test_name,
    COUNT(*) AS failure_count
FROM fact_inventory
WHERE closing_stock != (opening_stock + receipts - units_sold);

-- Check 5: Non-negative closing inventory
SELECT 
    'Negative Closing Stock' AS test_name,
    COUNT(*) AS failure_count
FROM fact_inventory
WHERE closing_stock < 0;

-- Check 6: All transaction dates exist in the calendar dimension
SELECT 
    'Missing Dates in Sales vs Calendar' AS test_name,
    COUNT(*) AS failure_count
FROM fact_sales s
LEFT JOIN dim_date d ON s.date = d.date
WHERE d.date IS NULL;
