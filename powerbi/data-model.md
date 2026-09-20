# Power BI Semantic Model & Dashboard Specification

## 1. Dimensional Model Relationships (Star Schema)
In Power BI Desktop / Service, configure 1-to-many single-directional relationships from Dimension tables to Fact tables:

```text
[DIM_DATE] (1) ──────────< (*) [FACT_SALES] (Date)
[DIM_PRODUCT] (1) ───────< (*) [FACT_SALES] (sku_id)
[DIM_DISTRIBUTOR] (1) ───< (*) [FACT_SALES] (distributor_id)
[DIM_REGION] (1) ────────< (*) [FACT_SALES] (region_id)
[DIM_PROMOTION] (1) ─────< (*) [FACT_SALES] (promotion_id)

[DIM_PRODUCT] (1) ───────< (*) [FACT_INVENTORY] (sku_id)
[DIM_DISTRIBUTOR] (1) ───< (*) [FACT_INVENTORY] (distributor_id)
[DIM_DATE] (1) ──────────< (*) [FACT_INVENTORY] (date)

[DIM_PRODUCT] (1) ───────< (*) [FACT_DEMAND] (sku_id)
[DIM_REGION] (1) ────────< (*) [FACT_DEMAND] (region_id)
```

## 2. Core DAX Measure Calculations

### Sales & Profitability Measures
```dax
-- Total Net Sales Revenue
Total Revenue = SUM(fact_sales[revenue])

-- Total Units Sold
Total Units = SUM(fact_sales[quantity])

-- Total Product Cost
Total Cost = SUM(fact_sales[cost])

-- Total Gross Profit
Total Gross Profit = [Total Revenue] - [Total Cost]

-- Gross Margin Percentage
Gross Margin % = 
DIVIDE([Total Gross Profit], [Total Revenue], 0) * 100

-- Average Order Line Value
Average Line Value = 
DIVIDE([Total Revenue], COUNTROWS(fact_sales), 0)

-- Prior Year Revenue (Time Intelligence)
Prior Year Revenue = 
CALCULATE(
    [Total Revenue],
    SAMEPERIODLASTYEAR(dim_date[date])
)

-- YoY Revenue Growth %
YoY Revenue Growth % = 
VAR PriorRev = [Prior Year Revenue]
RETURN
IF(
    ISBLANK(PriorRev) || PriorRev = 0,
    BLANK(),
    DIVIDE([Total Revenue] - PriorRev, PriorRev, 0) * 100
)
```

### Inventory & Stockout Risk Measures
```dax
-- Current Stock on Hand (Latest Snapshot)
Current Stock on Hand = 
CALCULATE(
    SUM(fact_inventory[closing_stock]),
    LASTDATE(dim_date[date])
)

-- Stockout Incident Count
Total Stockouts = SUM(fact_inventory[stockout_flag])

-- Stockout Rate %
Stockout Frequency % = 
DIVIDE(
    [Total Stockouts],
    COUNTROWS(fact_inventory),
    0
) * 100

-- Daily Sales Run-Rate (Last 90 Days)
Daily Sales Run-Rate = 
CALCULATE(
    DIVIDE([Total Units], 90, 0),
    DATESINPERIOD(dim_date[date], MAX(dim_date[date]), -90, DAY)
)

-- Estimated Days of Inventory (DOI)
Days of Inventory = 
DIVIDE([Current Stock on Hand], [Daily Sales Run-Rate], BLANK())
```

### Trade Promotion Effectiveness Measures
```dax
-- Promoted Sales Revenue
Promoted Revenue = 
CALCULATE(
    [Total Revenue],
    fact_sales[promotion_id] <> "NONE"
)

-- Promoted Units Sold
Promoted Units = 
CALCULATE(
    [Total Units],
    fact_sales[promotion_id] <> "NONE"
)

-- Trade Discount Concession Cost
Total Discount Cost = 
SUMX(
    fact_sales,
    fact_sales[quantity] * (fact_sales[list_price] - fact_sales[net_unit_price])
)
```

---

## 3. Four-Page Dashboard Layout & Visual Specifications

### Page 1: Executive Sales Overview
- **Header:** Automotive Aftermarket Executive Commercial Performance (FY 2024 - 2025)
- **Top Card Strip:**
  - Net Revenue (`Total Revenue`) | Units Sold (`Total Units`) | Gross Margin % (`Gross Margin %`) | YoY Growth % (`YoY Revenue Growth %`) | Active SKUs (`DISTINCTCOUNT(sku_id)`)
- **Visual 1 (Area Chart):** Monthly Net Revenue & Gross Profit Trends (24 Months)
- **Visual 2 (Bar Chart):** Revenue & Margin by Product Category (Braking, Filtration, Electrical, Chassis, Thermal)
- **Visual 3 (Matrix / Table):** Distributor Commercial League Table (Tier, Region, 2025 Revenue, YoY Growth %, Target Attainment)
- **Visual 4 (Donut Chart):** Regional Sales Contribution % (North, West, South, East)

### Page 2: Inventory & Stockout Risk
- **Header:** Distributor Inventory Health, Availability & Composite Stockout Risk
- **Top Card Strip:**
  - Critical Stockout Alerts (`COUNTROWS(FILTER(RiskTable, Risk = "Critical"))`) | Avg Days of Inventory | Total Stockout Incidents | Avg Supplier Lead Time
- **Visual 1 (Risk Matrix Scatter):** Days of Inventory (X-Axis) vs. Daily Sales Velocity (Y-Axis) bubble-sized by Lead Time, colored by Risk Category.
- **Visual 2 (Primary Grid):**
  - Columns: SKU ID | Product Name | Distributor | Current Stock | DOI | Lead Time | Composite Risk Score | Risk Category | Actionable Recommendation
- **Visual 3 (Bar Chart):** Stockout Incidents by Product Category and Distributor Tier.

### Page 3: Trade Marketing & Promotion Effectiveness
- **Header:** B2B Trade Campaign Viability & Net Incremental Profitability
- **Top Card Strip:**
  - Total Promotional Spend | Incremental Revenue | Incremental Gross Profit | Overall Promotion Effectiveness Index (PEI)
- **Visual 1 (Waterfall / Bar):** Promotion Effectiveness Index (PEI) by Campaign (Value Accretive vs Margin Dilutive)
- **Visual 2 (Scatter Plot):** Discount % Concession vs. Observed Volume Uplift %
- **Visual 3 (Detailed Evaluation Table):**
  - Campaign Name | Target Category | Region | Discount % | Budget | Incremental Units | Incremental GP | PEI | Commercial Classification

### Page 4: Commercial Opportunity & Manager Decision Support
- **Header:** Four-Quadrant Strategic Commercial Matrix & Decision Diagnostics
- **Visual 1 (Four-Quadrant Scatter):**
  - X-Axis: 2025 Net Revenue (Log / Normalized scale)
  - Y-Axis: YoY Revenue Growth %
  - Quadrants: Core Champions, Cash Cows, Emerging Stars, Under Review
- **Visual 2 (Manager Decision Simulator Card):**
  - Slicers: Region -> Distributor -> Product Category -> SKU
  - Real-time Output Card:
    - Current Sales Run-Rate
    - Gross Margin %
    - Inventory Stock & Coverage Days
    - Forecast Demand (Next 8 Weeks)
    - Stockout Risk Classification
    - Recommended Strategic Action
