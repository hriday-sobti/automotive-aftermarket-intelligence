# Automotive Aftermarket Sales & Trade Marketing Intelligence Platform

[![Python 3.10+](https://img.shields.io/badge/Python-3.10%2B-blue.svg)](https://www.python.org/)
[![Database: SQLite & PostgreSQL](https://img.shields.io/badge/Database-SQLite%20%7C%20PostgreSQL-darkblue.svg)](https://www.sqlite.org/)
[![Tests: 229 Passing](https://img.shields.io/badge/Tests-229%20Passing-brightgreen.svg)](tests/)
[![Power BI Ready](https://img.shields.io/badge/BI-Power%20BI%20Ready-yellow.svg)](powerbi/)
[![Excel Scenario Model](https://img.shields.io/badge/Excel-Scenario%20Model-green.svg)](excel/)
[![Author: Hriday Singh Sobti](https://img.shields.io/badge/Author-Hriday%20Singh%20Sobti-navy.svg)](https://github.com/hriday-sobti)

A commercial analytics platform built to solve four core problems faced by automotive aftermarket parts distributors: product prioritization, stockout exposure, trade promotion profitability, and linking demand forecasting directly to purchase order triggers.

All transaction, inventory, and demand records were programmatically generated to mirror real-world automotive parts distribution dynamics (seasonal monsoon wear on brakes, summer cooling stress, wholesale trade discounts, and multi-tier supplier lead times) under a deterministic random seed (`RANDOM_SEED = 42`).

---

## The Business Questions

In wholesale automotive parts distribution, commercial teams constantly wrestle with four operational questions:

1. **Product & Channel Prioritization:** Which SKUs actually generate operating profit versus vanity volume? How concentrated is revenue across our catalog?
2. **Availability & Working Capital:** Which products are at immediate risk of stocking out during peak demand, and how should safety stock and reorder points be set so distributors don't tie up cash in slow-moving parts?
3. **Trade Marketing ROI:** Do volume rebates and wholesale invoice discounts actually generate incremental gross profit, or are they just subsidizing volume the distributor would have bought anyway?
4. **Actionable Forecasting:** How do we take a statistical time-series forecast and turn it into exact purchase order recommendations rather than leaving it as an isolated line chart?

---

## System Architecture

```text
Synthetic Domain Generator (Python)
       │
       ▼
Raw Transactional Tables (88,659 sales lines, 314,934 stock snapshots, 24 months)
       │
       ▼
Validation Engine (Pre-flight checks, zero foreign key orphans, exact financial reconciliation)
       │
       ▼
Dimensional Star Schema (PostgreSQL DDL & SQLite Embedded Engine)
       │
       ▼
SQL Analytical Layer (Window functions, CTEs, YoY performance views, integrity checks)
       │
       ▼
┌───────────────────────┬─────────────────────────┬─────────────────────────┬─────────────────────────┐
│ Sales Intelligence   │ Inventory & Stockout    │ Promotion Effectiveness │ Demand Forecasting      │
│ - 80/20 Pareto Mix    │ - Days of Inventory     │ - De-seasonalized Base  │ - Naive, SMA-4, SES     │
│ - YoY Revenue Growth  │ - Composite Risk Score  │ - Incremental Margin    │ - 17-Wk Holdout Backtest│
│ - Margin Variance     │ - Safety Stock & ROP    │ - Promotion ROI (PEI)   │ - Recommended Order Qty │
└───────────────────────┴─────────────────────────┴─────────────────────────┴─────────────────────────┘
       │                                                                                 │
       ▼                                                                                 ▼
Power BI Semantic Models & 4 Dashboard Layouts                               Manager Decision Simulator
       │                                                                                 │
       ▼                                                                                 ▼
Excel Commercial Scenario Model (.xlsx)                                      Executive Insights Briefing
```

---

## Visual Analytics & Dashboard Previews

The platform exports structured analytical tables and visualizations designed for executive decision-making:

| Category Revenue Contribution | Inventory Stockout Risk Matrix |
| :---: | :---: |
| ![Category Revenue](powerbi/screenshots/category_revenue.png) | ![Inventory Risk Matrix](powerbi/screenshots/inventory_risk_matrix.png) |
| **80/20 Pareto SKU Concentration** | **Trade Promotion Effectiveness Index** |
| ![Pareto Curve](powerbi/screenshots/pareto_curve.png) | ![Promotion Effectiveness](powerbi/screenshots/promotion_effectiveness.png) |

---

## Data Model & Schema Design

The database follows a dimensional star-schema architecture (`docs/data-model.md`):

### Dimensions
- **`DIM_DATE`**: 731 calendar days (2024-01-01 to 2025-12-31).
- **`DIM_PRODUCT`**: 150 SKUs across Braking, Filtration, Electrical, Chassis, and Thermal categories.
- **`DIM_DISTRIBUTOR`**: 20 regional wholesale distributor accounts across 3 commercial tiers.
- **`DIM_WORKSHOP`**: 120 garage and fleet service accounts.
- **`DIM_REGION`**: 4 geographic territories (North, West, South, East) with vehicle parc multipliers.
- **`DIM_PROMOTION`**: 16 trade campaigns with category and regional targeting rules.
- **`DIM_SKU_PARETO`**: SKU-level cumulative revenue ranking (Class A: 80%, Class B: 15%, Class C: 5%).

### Facts
- **`FACT_SALES`**: 88,659 lines. Reconciles: $\text{Gross Profit} = \text{Revenue} - \text{Cost} = (\text{Qty} \times \text{Net Price}) - (\text{Qty} \times \text{Cost Price})$.
- **`FACT_INVENTORY`**: 314,934 stock records. Mass balance: $\text{Closing} = \text{Opening} + \text{Receipts} - \text{Sold}$.
- **`FACT_DEMAND`**: 63,000 observations at SKU × Region × Week grain.

---

## Analytical Modules

### 1. Sales & Pareto Intelligence
- **Revenue Concentration:** Class A SKUs (top 29.3% of catalog) drive 80.0% of total revenue, dominated by Braking Systems and Filtration.
- **Top-Line Comparison:** FY 2024 generated ₹1,234.44M vs ₹1,198.59M in FY 2025 (-2.90% variance), reflecting distributor destocking after Q4-2024 promotional volume loading.

### 2. Inventory Risk & Dynamic Reorder Points
- **Days of Inventory (DOI):** $\text{DOI} = \frac{\text{Current Stock}}{\text{Average Daily Demand Rate}}$.
- **Composite Risk Score ($0 - 100$):** Weighted combination of coverage ratio (35%), demand velocity (25%), lead-time exposure (20%), demand volatility CV (10%), and historical stockouts (10%).
- **Safety Stock & ROP:**
  $$SS = \lceil 1.645 \times \sigma_D \times \sqrt{L} \rceil$$
  $$\text{ROP} = (\bar{D} \times L) + SS$$
  $$\text{Recommended Order Qty} = \max\left(0, \lceil \text{ROP} + (\bar{D} \times 30) - \text{Current Stock} \rceil\right)$$

### 3. Trade Promotion Effectiveness
- **De-seasonalized Rolling Baseline:** Compares promoted sales against non-promoted periods within matching categories and regions.
- **Promotion Effectiveness Index (PEI):**
  $$\text{PEI} = \frac{\text{Incremental Gross Profit}}{\text{Trade Discount Concession Cost} + \text{Campaign Fixed Budget}}$$
- **Finding:** Uncapped wholesale invoice discounts generated volume uplift (+12% to +32%) but diluted net dollar gross profit because distributors used the discounts on baseline volume they were already planning to buy.

### 4. Demand Forecasting
- Backtested on a 17-week holdout window (2025-09-01 to 2025-12-31) with zero future information leakage:
  - **Naive Model:** MAE 71.76 | RMSE 84.59 | MAPE 12.52%
  - **4-Week SMA:** MAE 69.91 | RMSE 82.65 | MAPE 12.17%
  - **Exponential Smoothing:** MAE 69.91 | RMSE 82.65 | MAPE 12.17%
- The optimal smoothing forecast automatically feeds into the reorder calculation to determine purchase quantities.

### 5. Four-Quadrant Commercial Opportunity Matrix
- **Core Champions (44 SKUs):** High Sales / High Growth $\rightarrow$ Prioritize warehouse allocation and protect fill rates.
- **Cash Cows (31 SKUs):** High Sales / Low Growth $\rightarrow$ Defend margins and stop discretionary trade discounting.
- **Emerging Stars (31 SKUs):** Low Sales / High Growth $\rightarrow$ Introduce stocking incentives to expand garage penetration.
- **Under Review (44 SKUs):** Low Sales / Low Growth $\rightarrow$ Evaluate catalog necessity and bundle with fast-movers.

---

## Interactive Decision-Support Tools

### 1. Manager Decision Simulator (`src/analytics/decision_simulator.py`)
A command-line/notebook diagnostic tool where selecting a Region, Distributor, Category, and SKU returns a complete commercial profile:
- 2025 revenue and realized gross margin %
- YoY revenue growth
- Days of inventory on hand
- Daily sales velocity
- Stockout risk classification and primary driver
- Prescriptive reorder recommendation

### 2. Excel Commercial Scenario Model (`excel/scenario_model/trade_promotion_scenario_model.xlsx`)
A financial modeling workbook built with native dynamic formulas:
- **Inputs (Yellow):** Baseline units, list price, COGS, base discount %, campaign budget, proposed promo discount %, expected uplift %.
- **Calculations (Slate):** Net selling price, revenue, COGS, gross profit, trade discount cost.
- **Outputs (Mint Green):** Net incremental profit, PEI ratio, margin dilution (bps), and commercial recommendation.
- **Sensitivity Matrix:** Live two-way sensitivity table evaluating net profit across 5 discount tiers (8% to 16%) against 6 volume uplift levels (15% to 40%).

### 3. Power BI Semantic Model (`powerbi/data-model.md`)
Full star-schema relationships and DAX measure formulations for four dashboard views:
1. Executive Sales Overview
2. Inventory Health & Stockout Watchlist
3. Trade Marketing & Promotional PEI
4. Four-Quadrant Commercial Opportunity Matrix

---

## Quick Start & Project Execution

### Setup
```bash
# Clone the repository
git clone https://github.com/hriday-sobti/automotive-aftermarket-intelligence.git
cd automotive-aftermarket-intelligence

# Install dependencies
pip install -r requirements.txt
```

### Run the Pipeline
To regenerate the data, rebuild the database, export analytical models, build pre-rendered notebooks, and run the test suite:
```bash
python scripts/run_pipeline.py
```

### Run Tests
```bash
python -m pytest tests/
```
Runs 229 automated unit and integration tests across data generation, financial reconciliation, inventory formulas, forecasting splits, and Excel dynamic formulas.

---

## Repository Structure

```text
automotive-aftermarket-intelligence/
├── README.md                                 # Project documentation and architecture
├── pyproject.toml                            # Build metadata and package configuration
├── requirements.txt                          # Pinned project dependencies
│
├── config/
│   └── project_config.yaml                   # Simulation parameters, weights, and thresholds
│
├── data/
│   ├── raw/                                  # Generated raw CSV tables
│   ├── interim/                              # Pre-flight data validation reports
│   ├── processed/                            # Cleaned star-schema tables & aftermarket.db
│   └── README.md
│
├── docs/
│   ├── domain-understanding.md               # Automotive aftermarket ecosystem and actors
│   ├── blueprint-architecture.md             # Technical architecture and design choices
│   ├── data-dictionary.md                    # Detailed table and column definitions
│   ├── data-model.md                         # Star schema diagrams, grains, and keys
│   ├── methodology.md                        # Analytical baseline and scoring methods
│   ├── analytical-definitions.md             # Mathematical formulas and business metrics
│   ├── assumptions.md                        # Project assumptions and known limitations
│   └── environment.md                        # Hardware, OS, and runtime specifications
│
├── notebooks/                                # Pre-rendered Jupyter notebooks with charts
│   ├── 01_data_generation_validation.ipynb
│   ├── 02_eda.ipynb
│   ├── 03_sales_analysis.ipynb
│   ├── 04_inventory_risk.ipynb
│   ├── 05_promotion_analysis.ipynb
│   └── 06_forecasting.ipynb
│
├── src/
│   ├── data_generation/                      # Dimensions, demand, sales, inventory simulation
│   ├── validation/                           # Pre-flight integrity rules and reject logger
│   ├── cleaning/                             # Feature engineering and Pareto classification
│   ├── analytics/                            # Sales intelligence, opportunity matrix, simulator
│   ├── inventory/                            # Stockout risk scoring and safety stock logic
│   ├── promotions/                           # Baseline construction and uplift modeling
│   ├── forecasting/                          # Holdout time-series forecasting benchmarks
│   └── utils/                                # Config loader and structured logging
│
├── sql/
│   ├── schema/01_create_tables.sql           # ANSI SQL DDL with PK/FK constraints and indexes
│   ├── staging/01_staging_tables.sql         # Staging buffer table definitions
│   ├── transformations/01_load_facts.sql     # Staging to fact/dimension ETL transformations
│   ├── analytics/01_analytical_views.sql     # Analytical views, CTEs, and window functions
│   └── quality_checks/01_integrity_checks.sql# SQL data integrity assertions
│
├── powerbi/
│   ├── README.md                             # Setup instructions and visual gallery
│   ├── data-model.md                         # Semantic model schema and DAX measures
│   └── screenshots/                          # Exported chart visuals
│
├── excel/
│   ├── README.md                             # Scenario model documentation
│   └── scenario_model/                       # Interactive trade promotion workbook (.xlsx)
│
├── reports/
│   ├── executive-insights.md                 # Findings and business recommendations
│   └── eda_statistical_summary.md            # Statistical summary tables from EDA
│
├── scripts/
│   ├── generate_data.py                      # Data generation runner
│   ├── validate_data.py                      # Pre-flight validation runner
│   ├── build_database.py                     # Database compilation and table loader
│   ├── export_analytics.py                   # Analytical decision layer export runner
│   ├── build_notebooks.py                    # Pre-rendered notebook and figure builder
│   └── run_pipeline.py                       # Master pipeline runner
│
└── tests/
    ├── test_boundary_parametric_cases.py     # 130 parametric boundary and stress tests
    ├── test_data_generation.py               # 30 generator scale and entity tests
    ├── test_validation.py                    # 15 validation assertion tests
    ├── test_database_and_excel.py            # 13 SQL views and Excel formula tests
    ├── test_inventory_logic.py               # 12 safety stock and risk scoring tests
    ├── test_metrics.py                       # 8 sales KPI and Pareto tests
    ├── test_opportunity_and_simulator.py     # 8 opportunity matrix and simulator tests
    ├── test_forecasting.py                   # 7 forecasting split and error tests
    └── test_platform.py                      # 6 platform reconciliation tests
```

---

## Quality Assurance & Traceability

- **Financial Reconciliation:** $\text{Gross Profit} \equiv \text{Revenue} - \text{Cost}$ across all 88,659 transactions with zero rounding tolerance failure.
- **Inventory Balance:** $\text{Closing Stock} \equiv \text{Opening Stock} + \text{Receipts} - \text{Sold}$ across all 314,934 records.
- **Relational Integrity:** Zero foreign key orphans between facts and dimensions.
- **Automated Testing:** 229 automated tests passing with `pytest` on Python 3.10+.
