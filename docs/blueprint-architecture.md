# Technical Blueprint & Engineering Decisions

This document describes the engineering decisions, data model, and analytical formulas used across the platform.

---

## 1. Design Principles

1. **Deterministic & Reproducible:**
   Every dataset, transaction, and demand curve is generated using a fixed random seed (`RANDOM_SEED = 42`). Running `python scripts/run_pipeline.py` reproduces the entire database, analytical models, and outputs from scratch in ~40 seconds.
2. **Defensible Business Mathematics:**
   Formulas for safety stock, reorder points, composite risk scoring, and promotional uplift follow established industrial supply-chain and commercial accounting principles.
3. **Traceable Lineage:**
   Every figure shown in the dashboard or reports is directly traceable:
   $$\text{Report KPI} \longleftrightarrow \text{SQL View} \longleftrightarrow \text{FACT Table} \longleftrightarrow \text{Raw Generator Logic}$$

---

## 2. End-to-End Pipeline Flow

```text
[Synthetic Generator (Python)]
       │
       ▼
[Raw Data Tables (88,659 sales lines, 314,934 inventory snapshots)]
       │
       ▼
[Validation Engine (Pre-flight math, PK/FK, mass balance)]
       │
       ▼
[Feature Engineering (Pareto ranking, margin %, unit metrics)]
       │
       ▼
[Relational Database (PostgreSQL DDL & SQLite Embedded Engine)]
       │
       ▼
[SQL Analytical Views (Window functions, CTEs, YoY comparisons)]
       │
       ▼
┌───────────────────────┬─────────────────────────┬─────────────────────────┬─────────────────────────┐
│ Sales Intelligence   │ Inventory Sizing & Risk │ Trade Marketing ROI     │ Demand Forecasting      │
│ - Category Mix        │ - DOI & Velocity        │ - Rolling Baseline      │ - Holdout Backtesting   │
│ - Pareto 80/20 Curves │ - Composite Risk Score  │ - Incremental GP        │ - Exponential Smoothing │
│ - Distributor Growth  │ - Safety Stock & ROP    │ - Promotion PEI Index   │ - Reorder Quantities    │
└───────────────────────┴─────────────────────────┴─────────────────────────┴─────────────────────────┘
       │                                                                                 │
       ▼                                                                                 ▼
[Power BI Semantic Models & 4 Pages]                                         [Manager Decision Simulator]
       │                                                                                 │
       ▼                                                                                 ▼
[Excel Scenario Model (.xlsx)]                                               [Executive Insights Report]
```

---

## 3. Dimensional Star-Schema Design

### Grains & Keys

| Table | Type | Row Grain | Primary Key | Key Foreign Keys |
| :--- | :--- | :--- | :--- | :--- |
| **`DIM_DATE`** | Dimension | Calendar day | `date` | — |
| **`DIM_REGION`** | Dimension | Regional sales territory | `region_id` | — |
| **`DIM_VEHICLE_SEGMENT`** | Dimension | Vehicle category | `segment_id` | — |
| **`DIM_PRODUCT`** | Dimension | Part SKU | `sku_id` | `vehicle_segment` |
| **`DIM_DISTRIBUTOR`** | Dimension | Wholesale distributor account | `distributor_id` | `region_id` |
| **`DIM_WORKSHOP`** | Dimension | Garage customer account | `workshop_id` | `region_id` |
| **`DIM_PROMOTION`** | Dimension | Trade marketing campaign | `promotion_id` | — |
| **`DIM_SKU_PARETO`** | Dimension | SKU revenue tier | `sku_id` | `sku_id` |
| **`FACT_SALES`** | Fact | Sales transaction line item | `line_item_id` | `date`, `distributor_id`, `workshop_id`, `region_id`, `sku_id`, `promotion_id` |
| **`FACT_INVENTORY`** | Fact | SKU × Distributor × Date snapshot | `(date, distributor_id, sku_id)` | `date`, `distributor_id`, `sku_id` |
| **`FACT_DEMAND`** | Fact | SKU × Region × Week observation | `(week_start_date, sku_id, region_id)` | `sku_id`, `region_id` |

---

## 4. Key Mathematical Formulations

### Sales Intelligence
- **Net Realized Price:** $\text{Net Unit Price} = \text{ROUND}(\text{List Price} \times (1.0 - \text{Discount Pct}), 2)$
- **Gross Revenue:** $\text{Revenue} = \text{Quantity} \times \text{Net Unit Price}$
- **Gross Profit:** $\text{Gross Profit} = \text{Revenue} - \text{Cost}$
- **Gross Margin %:** $\text{Gross Margin \%} = \left(\frac{\text{Gross Profit}}{\text{Revenue}}\right) \times 100$

### Inventory Sizing & Risk
- **Days of Inventory (DOI):** $\text{DOI} = \frac{\text{Current Closing Stock}}{\text{Daily Sales Velocity}}$
- **Safety Stock ($SS$):**
  $$SS = \lceil Z \times \sigma_D \times \sqrt{L} \rceil$$
  *Where $Z = 1.645$ (95% Cycle Service Level), $\sigma_D$ is 90-day daily demand std dev, and $L$ is lead time in days.*
- **Reorder Point ($ROP$):**
  $$\text{ROP} = (\bar{D} \times L) + SS$$
- **Recommended Order Quantity ($ROQ$):**
  $$\text{ROQ} = \max\left(0, \lceil \text{ROP} + (\bar{D} \times 30) - \text{Current Stock} \rceil\right)$$
- **Composite Stockout Risk Score ($0 - 100$):**
  Linear combination of Coverage Risk (35%), Demand Pressure (25%), Lead Time (20%), Demand Volatility CV (10%), and Stockout Frequency (10%).

### Trade Promotion Economics
- **Rolling Non-Promoted Baseline:** Median daily run-rate during non-promoted periods (`promotion_id = 'NONE'`) in the same category and region, projected over campaign duration.
- **Incremental Gross Profit:**
  $$\text{Incremental GP} = \text{Promoted GP} - \text{Baseline GP}$$
- **Promotion Effectiveness Index (PEI):**
  $$\text{PEI} = \frac{\text{Incremental GP}}{\text{Trade Discount Cost} + \text{Campaign Fixed Budget}}$$
