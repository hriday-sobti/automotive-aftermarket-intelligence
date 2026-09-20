# Power BI Project & Template Guide

This directory contains the semantic definitions, dimensional schemas, DAX measures, and data export assets for Microsoft Power BI.

## How to Load Data into Power BI Desktop:
1. Open **Power BI Desktop**.
2. Select **Get Data** -> **Text/CSV** (or **Folder** pointing to `data/processed/`).
3. Import the core dimensional and fact tables:
   - `dim_date.csv`
   - `dim_product.csv`
   - `dim_distributor.csv`
   - `dim_region.csv`
   - `dim_promotion.csv`
   - `dim_sku_pareto.csv`
   - `fact_sales.csv`
   - `fact_inventory.csv`
   - `fact_demand.csv`
   - Analytical decision exports: `inventory_risk_scores.csv`, `promotion_effectiveness.csv`, `sku_opportunity_matrix.csv`.
4. Check **Model View** and verify that 1-to-many relationships match `powerbi/data-model.md`.
5. Copy the DAX measures provided in `powerbi/data-model.md`.
