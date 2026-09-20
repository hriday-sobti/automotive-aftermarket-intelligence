# Automotive Aftermarket Sales & Trade Marketing Intelligence Platform

[![Python 3.10+](https://img.shields.io/badge/Python-3.10%2B-blue.svg)](https://www.python.org/)
[![Database: SQLite & PostgreSQL](https://img.shields.io/badge/Database-SQLite%20%7C%20PostgreSQL-darkblue.svg)](https://www.sqlite.org/)
[![Tests: Pytest Passing](https://img.shields.io/badge/Tests-Pytest%20Passing-brightgreen.svg)](tests/)
[![Power BI Ready](https://img.shields.io/badge/BI-Power%20BI%20Ready-yellow.svg)](powerbi/)
[![Excel Scenario Model](https://img.shields.io/badge/Excel-Scenario%20Model-green.svg)](excel/)

> **Project Classification:** Enterprise Commercial Analytics & Decision-Support System  
> **Data Notice:** Explicitly and consistently engineered using **Synthetic / Project-Generated Data** simulating a multi-tier automotive wholesale aftermarket ecosystem (`RANDOM_SEED = 42`).

---

## 1. Project Overview & Business Problem

In the commercial automotive aftermarket, manufacturers and wholesale distributors face four critical commercial questions:
1. **Commercial Prioritization:** Which catalog SKUs and regional partners drive genuine gross margin, and how concentrated is top-line revenue?
2. **Lost Sales & Availability Risk:** Where are stockout events occurring, and how can inventory buffer thresholds (Safety Stock, ROP) be dynamically sized to protect service levels without inflating working capital?
3. **Trade Marketing ROI:** Are B2B wholesale trade promotions and invoice discounts actually driving incremental profit, or merely subsidizing baseline sales and eroding gross margin?
4. **Demand Predictability & Actionability:** How can forward demand forecasts directly feed operational purchase order recommendations rather than ending as isolated statistical charts?

This platform integrates **synthetic domain simulation, automated data validation, relational star-schema modeling, advanced SQL window analytics, statistical time-series forecasting, a composite stockout risk model, a 4-quadrant strategic portfolio matrix, Power BI dashboards, and a live Excel scenario model** into a single reproducible analytics pipeline.

---

## 2. Integrated Analytics Architecture

```text
[Synthetic Domain Generator (Python)]
       │
       ▼
[Raw Data Tables (88,659 Sales Lines, 314,934 Inventory Snapshots, 24 Months)]
       │
       ▼
[Pre-Flight Validation Engine (Rigorous mathematical reconciliation & FK checks)]
       │
       ▼
[Relational Database / Star Schema (PostgreSQL DDL & SQLite Embedded Engine)]
       │
       ▼
[SQL Analytical Layer (CTEs, Window Functions, Views & Data Quality Suite)]
       │
       ▼
┌───────────────────────┬─────────────────────────┬─────────────────────────┬─────────────────────────┐
│ Sales Intelligence   │ Inventory & Stockout    │ Promotion Effectiveness │ Demand Forecasting      │
│ - 80/20 Pareto Mix    │ - Days of Inventory     │ - De-seasonalized Base  │ - Naive / SMA / SES     │
│ - YoY Revenue Growth  │ - Composite Risk Score  │ - Incremental Margin    │ - Holdout Backtesting   │
│ - Margin Variance     │ - Safety Stock & ROP    │ - Promotion ROI (PEI)   │ - Reorder Quantities    │
└───────────────────────┴─────────────────────────┴─────────────────────────┴─────────────────────────┘
       │                                                                                 │
       ▼                                                                                 ▼
[Power BI Semantic Models & 4-Page Dashboard Specs]                          [Manager Decision Simulator]
       │                                                                                 │
       ▼                                                                                 ▼
[Excel Commercial Scenario Model (.xlsx)]                                    [Executive Insights Report]
```

---

## 3. Data Model & Star Schema

The database architecture is designed as a star schema with clearly defined fact and dimension table grains:

### Dimensional Entities
- `DIM_DATE`: Calendar day grain (731 rows, 2024-01-01 to 2025-12-31).
- `DIM_PRODUCT`: Catalog SKU grain (150 SKUs across Braking, Filtration, Electrical, Chassis, Thermal).
- `DIM_DISTRIBUTOR`: Wholesale distributor partner grain (20 regional distributors).
- `DIM_WORKSHOP`: Multi-brand service center customer grain (120 workshops).
- `DIM_REGION`: Geographic territory grain (4 major regional clusters).
- `DIM_PROMOTION`: Trade marketing campaign calendar (16 structured campaigns).
- `DIM_SKU_PARETO`: 80/20 revenue concentration classification (Class A, B, C).

### Fact Tables
- `FACT_SALES`: **Grain: One row per transaction line item** (88,659 rows).
  - Exact financial reconciliation: $\text{Gross Profit} = \text{Revenue} - \text{Cost} = (\text{Quantity} \times \text{Net Unit Price}) - (\text{Quantity} \times \text{Cost Price})$.
- `FACT_INVENTORY`: **Grain: One row per SKU × Distributor × Date snapshot** (314,934 rows).
  - Rigid mass balance: $\text{Closing Stock} = \text{Opening Stock} + \text{Receipts} - \text{Units Sold}$.
- `FACT_DEMAND`: **Grain: One row per SKU × Region × Week** (63,000 rows).

---

## 4. Analytical Modules & Methodologies

### Layer 1: Sales Performance & Pareto Concentration
- **Pareto Intelligence:** Top 29.3% of catalog SKUs generate 80.0% of cumulative revenue (Class A champions concentrated in Braking Systems and Filtration).
- **YoY Growth Analysis:** Reconciles FY 2024 (₹1,234.44M) vs FY 2025 (₹1,198.59M), surfacing channel inventory dynamics and post-promotional run-rates.

### Layer 2: Inventory & Composite Stockout Risk Model
- **Days of Inventory (DOI):** $\text{DOI} = \frac{\text{Current Stock}}{\text{Average Daily Demand Rate}}$.
- **Composite Stockout Risk Score ($0 - 100$):** Weighted multi-factor normalization:
  - Inventory Coverage Exposure (35% weight)
  - Demand Pressure Velocity (25% weight)
  - Supplier Lead Time Exposure (20% weight)
  - Demand Volatility / CV (10% weight)
  - Historical Stockout Frequency (10% weight)
- **Operational Replenishment Parameters:**
  - $\text{Safety Stock} = \lceil Z \times \sigma_D \times \sqrt{L} \rceil$ ($Z = 1.645$ for 95% service level).
  - $\text{Reorder Point} = (\bar{D} \times L) + \text{Safety Stock}$.
  - $\text{Recommended Order Qty} = \max(0, \lceil \text{ROP} + (\bar{D} \times 30) - \text{Current Stock} \rceil)$.

### Layer 3: Trade Promotion Effectiveness & Baseline Uplift
- **De-seasonalized Rolling Baseline:** Evaluates non-promotional daily run-rates during matched non-promoted periods within identical categories and regions.
- **Promotion Effectiveness Index (PEI):**
  $$\text{PEI} = \frac{\text{Incremental Gross Profit}}{\text{Trade Discount Concession Cost} + \text{Campaign Fixed Budget}}$$
- **Key Discovery:** Flat across-the-board discounting produced positive volume uplift (+12% to +32%) but negative incremental dollar margin due to deadweight loss on baseline volume.

### Layer 4: Demand Forecasting Benchmark
- Evaluates **Naive Baseline**, **4-Week Simple Moving Average (SMA)**, and **Simple Exponential Smoothing (SES)** across a 17-week holdout evaluation window (zero future leakage):
  - **MAE:** 69.91 units
  - **RMSE:** 82.65 units
  - **MAPE:** 12.17%
- Selected optimal smoothing model automatically feeds forward replenishment pipelines.

### Layer 5: Commercial Opportunity Matrix (4-Quadrant Model)
- **Core Champions (44 SKUs):** High Sales / High Growth $\rightarrow$ Guarantee availability and prioritize trade support.
- **Cash Cows (31 SKUs):** High Sales / Low Growth $\rightarrow$ Defend margins and eliminate price concessions.
- **Emerging Stars (31 SKUs):** Low Sales / High Growth $\rightarrow$ Expand workshop distribution and trial packages.
- **Under Review (44 SKUs):** Low Sales / Low Growth $\rightarrow$ Audit catalog fitment and review for phase-out.

---

## 5. Decision-Support Deliverables

### Microsoft Power BI Dashboard Suite
Four fully documented dashboard pages with DAX semantic models (`powerbi/data-model.md`):
1. **Executive Sales Overview:** Headline KPIs, monthly revenue trends, category contribution, and distributor ranking matrix.
2. **Inventory Risk & Availability:** DOI scatter matrix, critical stockout watchlist, and distributor-level inventory health.
3. **Trade Marketing & Financial Viability:** Waterfall analysis of incremental profit, discount concessions vs uplift, and campaign PEI.
4. **Commercial Opportunity & Manager Simulator:** Interactive 4-quadrant portfolio map and real-time SKU-distributor 360° diagnostic card.

### Microsoft Excel Commercial Scenario Model
- **File:** `excel/scenario_model/trade_promotion_scenario_model.xlsx`
- **Features:** Dynamic spreadsheet formulas simulating baseline units, discount tiers, price elasticity, and net incremental gross profit with an automated two-way sensitivity data table (Discount % vs Volume Uplift %).

### Executive Insights Report
- **Document:** `reports/executive-insights.md`
- Structured executive briefing translating empirical findings into actionable business recommendations following the **Observation $\rightarrow$ Evidence $\rightarrow$ Business Implication $\rightarrow$ Suggested Action $\rightarrow$ Caveat** protocol.

---

## 6. Quick Start & Execution Guide

### Prerequisites
- Python 3.10+ (Tested on Python 3.14.6 x64)
- Standard scientific Python libraries: `pandas`, `numpy`, `statsmodels`, `openpyxl`, `sqlalchemy`, `pyyaml`, `pytest`

### Single-Command Pipeline Execution
Run the complete end-to-end platform with a single command:
```bash
python scripts/run_pipeline.py
```
This automatically executes:
1. `scripts/generate_data.py`: Generates dimensions, demand, promotions, sales transactions, inventory flow, runs pre-flight validation, and cleans features.
2. `scripts/build_database.py`: Builds the database schema, compiles indexes, and ingests all dimensional tables.
3. `src/analytics/eda_engine.py`: Performs exploratory data analysis and generates statistical summaries.
4. `scripts/export_analytics.py`: Computes risk scores, safety stock, promotion uplift, forecasting benchmarks, and opportunity matrices.
5. `src/analytics/excel_scenario_generator.py`: Generates the live Excel commercial scenario workbook.
6. `tests/`: Runs the automated unit and integration test suite via `pytest`.

### Run Automated Tests
```bash
python -m pytest tests/
```

---

## 7. Repository Structure

```text
automotive-aftermarket-intelligence/
├── README.md                                 # Primary project documentation
├── pyproject.toml                            # Build metadata and package configuration
├── requirements.txt                          # Pinned project dependencies
│
├── config/
│   └── project_config.yaml                   # Central project parameters and thresholds
│
├── data/
│   ├── raw/                                  # Raw synthetic dimension and fact outputs
│   ├── interim/                              # Pre-flight validation reports and audit logs
│   ├── processed/                            # Final star-schema CSVs and aftermarket.db
│   └── README.md
│
├── docs/
│   ├── domain-understanding.md               # Aftermarket business ecosystem & value chain
│   ├── blueprint-architecture.md             # Technical architecture & mathematical blueprint
│   ├── data-dictionary.md                    # Formal dictionary for all tables and fields
│   ├── analytical-definitions.md             # Business formulas, inputs, and definitions
│   ├── assumptions.md                        # Methodological assumptions & guardrails
│   └── environment.md                        # Hardware, OS, and tool runtime specifications
│
├── src/
│   ├── data_generation/                      # Dimension, demand, promotion, sales & stock simulation
│   ├── validation/                           # Pre-flight data validation & rejection logger
│   ├── cleaning/                             # Feature engineering & Pareto classification
│   ├── analytics/                            # Sales intelligence, opportunity matrix & simulator
│   ├── inventory/                            # Composite stockout risk & safety stock logic
│   ├── promotions/                           # Trade promotion baseline & uplift modeling
│   ├── forecasting/                          # Time-series forecasting & holdout evaluation
│   └── utils/                                # Config loaders and standardized logging
│
├── sql/
│   ├── schema/01_create_tables.sql           # ANSI SQL DDL with PK/FK constraints & indexes
│   ├── analytics/01_analytical_views.sql     # Analytical views, CTEs, and window functions
│   └── quality_checks/01_integrity_checks.sql# Automated SQL data integrity test suite
│
├── powerbi/
│   ├── README.md                             # Power BI setup and import guide
│   └── data-model.md                         # Semantic model schema & DAX measure formulas
│
├── excel/
│   ├── README.md                             # Spreadsheet guide and calculation notes
│   └── scenario_model/                       # Dynamic Excel commercial scenario workbook (.xlsx)
│
├── reports/
│   ├── executive-insights.md                 # C-suite commercial findings & recommendations
│   └── eda_statistical_summary.md            # Tabulated statistical EDA distributions
│
├── scripts/
│   ├── generate_data.py                      # Data generation and validation runner
│   ├── validate_data.py                      # Standalone validation runner
│   ├── build_database.py                     # Database DDL compiler and data loader
│   ├── export_analytics.py                   # Analytical decision layer export runner
│   └── run_pipeline.py                       # Single-command master orchestrator
│
└── tests/
    └── test_platform.py                      # Unit tests for financial reconciliation & logic
```

---

## 8. Analytical Traceability & Integrity Guarantee

Every number presented in executive reports, Power BI models, and analytical views is strictly traceable back to source calculations:
- **Financial Reconciliation:** $\text{Gross Profit} \equiv \text{Revenue} - \text{Cost}$ across all 88,659 transactions with zero discrepancy.
- **Physical Mass Balance:** $\text{Closing Stock} \equiv \text{Opening Stock} + \text{Receipts} - \text{Sold}$ across all 314,934 warehouse observations.
- **No Data Fabrication:** All metrics originate from deterministic formulas executed over reproducible synthetic datasets.
