# Analytical Architecture & Project Blueprint

## 1. Architectural Philosophy
The Automotive Aftermarket Sales & Trade Marketing Intelligence Platform is engineered as a deterministic, decoupled, and audit-traceable analytics pipeline. It adheres strictly to modern analytics engineering principles:
1. **No Data Fabrication:** Synthetic data is labeled explicitly, generated with controlled stochastic properties, and seeded (`RANDOM_SEED = 42`).
2. **Defensible Business Logic:** Formulations for safety stock, composite risk, baseline estimation, and promotion effectiveness follow recognized industrial supply chain and financial accounting standards.
3. **Traceability:** Every metric reported in the final executive dashboard can be traced back to dimensional SQL views, processed fact tables, validation logs, and generation source logic.

```text
[Synthetic Domain Generator] 
       │
       ▼
[Raw Data Tables (24 Months, ~100k+ Sales Records)]
       │
       ▼
[Validation Engine (Pre-flight checks, rejection logs, anomaly auditing)]
       │
       ▼
[Cleaning & Feature Engineering]
       │
       ▼
[Relational Database / Dimensional Star Schema (DDL, Staging, Fact/Dim)]
       │
       ▼
[SQL Analytical Layer (CTEs, Window Functions, Views, Aggregations)]
       │
       ▼
┌───────────────────────┬─────────────────────────┬─────────────────────────┬─────────────────────────┐
│ Sales Intelligence   │ Inventory & Stockout    │ Promotion Effectiveness │ Demand Forecasting      │
│ - Mix & Pareto        │ - Days of Inventory     │ - Baseline Modeling     │ - Moving Avg & Exp Smooth│
│ - Regional Growth     │ - Composite Risk Score  │ - Incremental Margin    │ - Holdout Validation    │
│ - Margin Variance     │ - Replenishment Priority│ - Promo ROI/Viability   │ - Operational Reorder   │
└───────────────────────┴─────────────────────────┴─────────────────────────┴─────────────────────────┘
       │                                                                                 │
       ▼                                                                                 ▼
[Power BI Analytical Models & DAX Semantic Spec]                             [Manager Decision Simulator]
       │                                                                                 │
       ▼                                                                                 ▼
[Excel Commercial Scenario Model (.xlsx)]                                    [Executive Business Insights]
```

## 2. Dimensional Star Schema Architecture
To maintain consistent grains across all queries and BI visuals:

### Core Dimensions
- `DIM_DATE`: Date grain (Day level: `date`, `year`, `quarter`, `month`, `month_name`, `week`, `day_of_week`, `is_weekend`).
- `DIM_PRODUCT`: SKU grain (`sku_id`, `product_name`, `product_category`, `subcategory`, `brand_tier`, `vehicle_segment`, `cost_price`, `list_price`, `product_status`).
- `DIM_DISTRIBUTOR`: Distributor grain (`distributor_id`, `distributor_name`, `region_id`, `distributor_tier`, `credit_term_days`, `sales_target_inr`).
- `DIM_WORKSHOP`: Workshop customer grain (`workshop_id`, `workshop_name`, `region_id`, `workshop_type`, `monthly_demand_factor`).
- `DIM_REGION`: Geography grain (`region_id`, `region_name`, `state`, `market_tier`, `parc_size_multiplier`).
- `DIM_PROMOTION`: Campaign grain (`promotion_id`, `campaign_name`, `campaign_type`, `start_date`, `end_date`, `target_category`, `target_region`, `discount_pct`, `budget_inr`, `campaign_objective`).
- `DIM_VEHICLE_SEGMENT`: Vehicle classification (`segment_id`, `segment_name`, `typical_replacement_cycle_months`).

### Core Facts
- `FACT_SALES`: Grain: *One row per sales line-item transaction event*.
  - `transaction_id`, `line_item_id`, `date`, `distributor_id`, `workshop_id`, `sku_id`, `quantity`, `list_price`, `discount_pct`, `net_unit_price`, `revenue`, `cost`, `gross_profit`, `promotion_id`.
- `FACT_INVENTORY`: Grain: *One row per SKU × Distributor × Date observation*.
  - `date`, `distributor_id`, `sku_id`, `opening_stock`, `receipts`, `units_sold`, `closing_stock`, `lead_time_days`, `stockout_flag`.
- `FACT_DEMAND`: Grain: *One row per SKU × Region × Week observation*.
  - `week_start_date`, `sku_id`, `region_id`, `vehicle_segment`, `estimated_latent_demand`, `observed_sales_demand`, `lost_sales_units`, `seasonal_index`.
- `FACT_PROMOTION_PERFORMANCE`: Grain: *One row per Promotion × SKU × Region evaluation*.
  - `promotion_id`, `sku_id`, `region_id`, `baseline_units`, `promoted_units`, `incremental_units`, `baseline_gross_profit`, `promoted_gross_profit`, `incremental_gross_profit`, `discount_cost`, `promotional_spend`, `promotion_effectiveness`.

## 3. Analytical Formulation Summary

### A. Sales Performance Intelligence
- **Gross Profit:** $\text{Gross Profit} = \text{Revenue} - \text{Cost}$
- **Gross Margin %:** $\text{Gross Margin} = \frac{\text{Gross Profit}}{\text{Revenue}} \times 100$
- **Sales Velocity:** $\text{Daily Sales Velocity} = \frac{\sum \text{Units Sold in Window}}{\text{Days in Window}}$
- **YoY Growth:** $\text{YoY Growth} = \frac{\text{Revenue}_{t} - \text{Revenue}_{t-12}}{\text{Revenue}_{t-12}} \times 100$

### B. Inventory & Composite Stockout Risk Model
- **Days of Inventory (DOI):** $\text{DOI} = \frac{\text{Current Stock}}{\text{Average Daily Demand}}$
- **Safety Stock ($SS$):**
  $$SS = Z \times \sigma_{D} \times \sqrt{L}$$
  *Where $Z = 1.645$ (95% Service Level), $\sigma_D$ is daily demand standard deviation, and $L$ is supplier lead time in days.*
- **Reorder Point ($ROP$):**
  $$ROP = (\bar{D} \times L) + SS$$
- **Composite Stockout Risk Score ($0 - 100$):**
  Normalized linear combination of:
  1. *Inventory Coverage Risk (35%):* Inverse bounded sigmoid of DOI vs Lead Time.
  2. *Demand Velocity & Pressure (25%):* Ratio of forward forecast demand to current stock.
  3. *Lead Time Exposure (20%):* Normalized supplier lead time relative to category max.
  4. *Demand Volatility (10%):* Coefficient of variation ($CV = \frac{\sigma}{\mu}$) of daily sales.
  5. *Historical Stockout Penalty (10%):* Frequency of recent zero-stock events.
  - *Risk Classification:* Low Risk ($<30$), Watch ($30-55$), High Risk ($55-75$), Critical ($>75$).

### C. Trade Promotion Effectiveness
- **De-seasonalized Rolling Baseline:**
  Median weekly sales over 8 non-promoted prior weeks adjusted for category seasonal indices.
- **Incremental Volume:** $\text{Incremental Units} = \text{Promoted Units} - \text{Baseline Units}$
- **Discount Concession Cost:** $\text{Discount Cost} = \text{Promoted Units} \times (\text{List Price} - \text{Net Unit Price})$
- **Incremental Gross Profit:**
  $$\text{Incremental Gross Profit} = \text{Promoted Gross Profit} - \text{Baseline Gross Profit}$$
- **Promotion Effectiveness Index ($PEI$):**
  $$PEI = \frac{\text{Incremental Gross Profit}}{\text{Discount Cost} + \text{Allocated Campaign Budget}}$$
  - $PEI > 1.0$: Commercially accretive (generated net profit above all costs).
  - $0.0 \le PEI \le 1.0$: Margin dilutive (generated volume but destroyed net dollar profit).
  - $PEI < 0.0$: Value destructive (promoted sales generated less gross profit than baseline).

### D. Forecasting & Operational Decisions
- Compares:
  1. Naive Baseline (Last Period)
  2. 4-Week & 8-Week Rolling Averages
  3. Holt-Winters / Exponential Smoothing with Additive Seasonality
- Metrics: Mean Absolute Error (MAE), Root Mean Squared Error (RMSE), Mean Absolute Percentage Error (MAPE).
- Connects predictions to operational purchase orders:
  $$\text{Recommended Order Qty} = \max(0, ROP - \text{Current Stock} + \text{Forecasted Demand over Horizon})$$
