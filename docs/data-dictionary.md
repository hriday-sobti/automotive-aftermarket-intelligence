# Data Dictionary: Automotive Aftermarket Intelligence Platform

*Dataset Classification: Synthetic / Project-Generated Data*

## 1. Dimensional Tables

### `DIM_DATE`
Calendar dimension table covering the 24-month analysis window (2024-01-01 to 2025-12-31).
- **Grain:** One row per calendar day (731 rows).
- **Columns:**
  - `date` (VARCHAR(10), Primary Key): ISO format date `YYYY-MM-DD`.
  - `year` (INTEGER): Calendar year (2024, 2025).
  - `quarter` (VARCHAR(2)): Calendar quarter (`Q1`, `Q2`, `Q3`, `Q4`).
  - `year_quarter` (VARCHAR(7)): Year and quarter identifier (`2024-Q1`).
  - `month` (INTEGER): Month number (1 - 12).
  - `month_name` (VARCHAR(20)): Full month name (`January` - `December`).
  - `year_month` (VARCHAR(7)): Year-Month string (`2024-01`).
  - `week_of_year` (INTEGER): ISO week number (1 - 53).
  - `day_of_month` (INTEGER): Day of month (1 - 31).
  - `day_of_week` (INTEGER): Day of week index (1 = Monday, 7 = Sunday).
  - `day_name` (VARCHAR(15)): Day name (`Monday` - `Sunday`).
  - `is_weekend` (INTEGER): Flag (1 = Weekend, 0 = Weekday).

### `DIM_REGION`
Geographic sales territories for distribution logistics.
- **Grain:** One row per regional market (4 rows).
- **Columns:**
  - `region_id` (VARCHAR(10), Primary Key): Territory code (`REG-01` to `REG-04`).
  - `region_name` (VARCHAR(50)): Operational territory (`North Region`, `West Region`, etc.).
  - `state_cluster` (VARCHAR(100)): Contiguous state coverage.
  - `market_tier` (VARCHAR(20)): Tier 1 vs Tier 2 maturity.
  - `parc_size_multiplier` (NUMERIC(4,2)): Relative registered vehicle parc density.

### `DIM_PRODUCT`
Master catalog of aftermarket automotive SKUs.
- **Grain:** One row per SKU (150 rows).
- **Columns:**
  - `sku_id` (VARCHAR(20), Primary Key): Unique part code (e.g. `SKU-BRA-0012`).
  - `product_name` (VARCHAR(100)): Commercial description.
  - `product_category` (VARCHAR(50)): Automotive system (`Braking Systems`, `Filtration`, `Electrical & Ignition`, `Chassis & Steering`, `Thermal & Cooling`).
  - `subcategory` (VARCHAR(50)): Specific component family (e.g. `Brake Pads Front`, `Oil Filter Spin-On`).
  - `brand_tier` (VARCHAR(50)): Specification level (`Premium OE Specification`, `Standard Aftermarket OE Quality`, `Commercial Heavy-Duty`).
  - `vehicle_segment` (VARCHAR(10), Foreign Key): Compatible segment (`SEG-PV`, `SEG-LCV`, `SEG-HCV`, `SEG-2W`).
  - `cost_price` (NUMERIC(10,2)): Manufacturer wholesale base cost in INR (₹).
  - `list_price` (NUMERIC(10,2)): Standard catalog wholesale list price in INR (₹).
  - `standard_lead_time_days` (INTEGER): Supplier replenishment transit window in days (7 to 45).
  - `velocity_profile` (VARCHAR(20)): Inherent demand speed (`Fast Moving`, `Medium Moving`, `Slow Moving`).
  - `product_status` (VARCHAR(20)): Lifecycle status (`Active`, `Phase-Out`).

### `DIM_DISTRIBUTOR`
Authorized regional wholesale distributor partners.
- **Grain:** One row per distributor (20 rows).
- **Columns:**
  - `distributor_id` (VARCHAR(10), Primary Key): Partner code (`DIST-01` to `DIST-20`).
  - `distributor_name` (VARCHAR(100)): Commercial legal entity name.
  - `region_id` (VARCHAR(10), Foreign Key): Operating region.
  - `distributor_tier` (VARCHAR(30)): Classification (`Tier 1 Platinum`, `Tier 2 Gold`, `Tier 3 Silver`).
  - `credit_term_days` (INTEGER): Payment terms (15, 30, 45 days).
  - `annual_sales_target_inr` (NUMERIC(12,2)): Annual contractual quota in INR (₹).

### `DIM_WORKSHOP`
Customer service centers, fleet depots, and multi-brand garages.
- **Grain:** One row per workshop (120 rows).
- **Columns:**
  - `workshop_id` (VARCHAR(10), Primary Key): Garage code (`WS-001` to `WS-120`).
  - `workshop_name` (VARCHAR(100)): Workshop name.
  - `region_id` (VARCHAR(10), Foreign Key): Garage location region.
  - `workshop_type` (VARCHAR(50)): Classification (`Multi-Brand Independent Garage`, `Authorized Chain Franchise`, etc.).
  - `monthly_demand_factor` (NUMERIC(4,2)): Normalized repair volume index.

### `DIM_PROMOTION`
Trade marketing campaign master calendar.
- **Grain:** One row per promotional campaign (16 rows).
- **Columns:**
  - `promotion_id` (VARCHAR(10), Primary Key): Campaign code (`PRM-001` to `PRM-016`).
  - `campaign_name` (VARCHAR(100)): Marketing initiative title.
  - `campaign_type` (VARCHAR(50)): Promotional structure (`Seasonal Pre-Stocking`, `Volume Rebate Scheme`, etc.).
  - `start_date` (VARCHAR(10)): Promotional launch date (`YYYY-MM-DD`).
  - `end_date` (VARCHAR(10)): Promotional expiration date (`YYYY-MM-DD`).
  - `target_category` (VARCHAR(50)): Promoted product line.
  - `target_region` (VARCHAR(10)): Territory eligibility (`REG-01` to `REG-04`, or `ALL`).
  - `discount_pct` (NUMERIC(5,4)): Trade discount percentage concession (e.g. 0.10 for 10%).
  - `budget_inr` (NUMERIC(10,2)): Fixed campaign collateral and administration spend in INR (₹).
  - `expected_uplift_pct` (NUMERIC(5,4)): Modeled volume target.
  - `campaign_objective` (TEXT): Strategic business goal.

---

## 2. Fact Tables

### `FACT_SALES`
Wholesale transaction line items fulfilled from distributors to workshops.
- **Grain:** One row per sales transaction line item (88,659 rows).
- **Columns:**
  - `transaction_id` (VARCHAR(20)): Wholesale purchase order number (e.g. `TRX-100001`).
  - `line_item_id` (VARCHAR(25), Primary Key): Unique line item code (e.g. `TRX-100001-L1`).
  - `date` (VARCHAR(10), Foreign Key): Transaction date.
  - `distributor_id` (VARCHAR(10), Foreign Key): Fulfilling distributor.
  - `workshop_id` (VARCHAR(10), Foreign Key): Purchasing workshop customer.
  - `region_id` (VARCHAR(10), Foreign Key): Regional territory.
  - `sku_id` (VARCHAR(20), Foreign Key): Product code.
  - `quantity` (INTEGER): Number of physical units purchased.
  - `cost_price` (NUMERIC(10,2)): Base unit cost in INR (₹).
  - `list_price` (NUMERIC(10,2)): Catalog wholesale unit list price in INR (₹).
  - `discount_pct` (NUMERIC(5,4)): Total combined trade discount applied (0.0 to 0.35).
  - `net_unit_price` (NUMERIC(10,2)): Realized unit invoice price = `ROUND(list_price * (1 - discount_pct), 2)`.
  - `revenue` (NUMERIC(12,2)): Net sales value = `ROUND(quantity * net_unit_price, 2)`.
  - `cost` (NUMERIC(12,2)): Total cost of goods sold = `ROUND(quantity * cost_price, 2)`.
  - `gross_profit` (NUMERIC(12,2)): Realized dollar profit = `ROUND(revenue - cost, 2)`.
  - `promotion_id` (VARCHAR(10)): Tagged trade marketing campaign or `NONE`.
  - `gross_margin_pct` (NUMERIC(5,2)): Realized gross margin % = `ROUND((gross_profit / revenue) * 100, 2)`.

### `FACT_INVENTORY`
Wholesale warehouse stock snapshots and replenishment flows.
- **Grain:** One row per SKU × Distributor × Observation Date (314,934 rows).
- **Columns:**
  - `date` (VARCHAR(10), Composite PK): Observation date.
  - `distributor_id` (VARCHAR(10), Composite PK): Distributor warehouse.
  - `sku_id` (VARCHAR(20), Composite PK): Product code.
  - `opening_stock` (INTEGER): Beginning available physical inventory.
  - `receipts` (INTEGER): Supplier shipment arrivals delivered today.
  - `units_sold` (INTEGER): Physical units fulfilled out of stock today.
  - `closing_stock` (INTEGER): Ending inventory = `opening_stock + receipts - units_sold`.
  - `lead_time_days` (INTEGER): Supplier lead time in transit.
  - `stockout_flag` (INTEGER): Binary indicator (1 if closing stock is 0 and unmet demand occurred; 0 otherwise).

### `FACT_DEMAND`
Latent market demand observations across regional vehicle fleets.
- **Grain:** One row per SKU × Region × Week (63,000 rows).
- **Columns:**
  - `week_start_date` (VARCHAR(10), Composite PK): Starting Monday date.
  - `sku_id` (VARCHAR(20), Composite PK): Product code.
  - `region_id` (VARCHAR(10), Composite PK): Regional market.
  - `vehicle_segment` (VARCHAR(10)): Target vehicle segment.
  - `product_category` (VARCHAR(50)): Product line.
  - `seasonal_index` (NUMERIC(4,2)): Monthly seasonal index factor.
  - `trend_factor` (NUMERIC(5,3)): Annual macroeconomic expansion multiplier.
  - `estimated_latent_demand` (NUMERIC(8,1)): Estimated weekly consumer repair demand in units.
