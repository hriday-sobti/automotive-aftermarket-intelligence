# Dimensional Data Model & Star Schema Specification

## 1. Dimensional Architecture Overview
The Automotive Aftermarket Sales & Trade Marketing Intelligence Platform implements an enterprise-grade Star Schema architecture.

```text
       ┌────────────────┐
       │   DIM_REGION   │
       └───────┬────────┘
               │ 1
               │
               │ *
       ┌───────▼────────┐             1 ┌────────────────┐
       │DIM_DISTRIBUTOR ├───────────────┤   DIM_DATE     │
       └───────┬────────┘               └───────┬────────┘
               │ 1                              │ 1
               │                                │
               │ *                            * │
       ┌───────▼────────────────────────────────▼────────┐
       │                   FACT_SALES                    │
       │  (Grain: One row per transaction line item)     │
       └───────▲────────────────▲───────────────▲────────┘
             * │              * │             * │
               │ 1              │ 1             │ 1
       ┌───────┴────────┐ ┌─────┴──────────┐ ┌──┴────────────┐
       │  DIM_WORKSHOP  │ │  DIM_PRODUCT   │ │ DIM_PROMOTION │
       └────────────────┘ └─────┬──────────┘ └───────────────┘
                                │ 1
                                │
                                │ *
                        ┌───────▼────────┐
                        │ FACT_INVENTORY │
                        └────────────────┘
```

## 2. Table Grains, Keys & Business Meanings

### Dimension Tables
1. **`DIM_DATE`**
   - **Grain:** One row per calendar date.
   - **Primary Key:** `date` (ISO `YYYY-MM-DD`).
   - **Business Meaning:** Temporal master reference enabling period-over-period and YoY time-intelligence aggregations.
2. **`DIM_REGION`**
   - **Grain:** One row per geographic sales territory.
   - **Primary Key:** `region_id`.
   - **Business Meaning:** Regional logistics clusters with vehicle parc weightings.
3. **`DIM_PRODUCT`**
   - **Grain:** One row per catalog SKU.
   - **Primary Key:** `sku_id`.
   - **Foreign Keys:** `vehicle_segment` $\rightarrow$ `DIM_VEHICLE_SEGMENT(segment_id)`.
   - **Business Meaning:** Master product definition with costs, list prices, lead times, and velocity profiles.
4. **`DIM_DISTRIBUTOR`**
   - **Grain:** One row per authorized wholesale distributor.
   - **Primary Key:** `distributor_id`.
   - **Foreign Keys:** `region_id` $\rightarrow$ `DIM_REGION(region_id)`.
   - **Business Meaning:** Channel partners holding regional stock and servicing garage networks.
5. **`DIM_WORKSHOP`**
   - **Grain:** One row per workshop/garage customer.
   - **Primary Key:** `workshop_id`.
   - **Foreign Keys:** `region_id` $\rightarrow$ `DIM_REGION(region_id)`.
   - **Business Meaning:** Repair centers generating replacement demand.
6. **`DIM_PROMOTION`**
   - **Grain:** One row per marketing campaign.
   - **Primary Key:** `promotion_id`.
   - **Business Meaning:** Commercial initiatives targeting categories and regions with discounted pricing.
7. **`DIM_SKU_PARETO`**
   - **Grain:** One row per SKU.
   - **Primary Key:** `sku_id`.
   - **Business Meaning:** Cumulative revenue concentration tier (Class A: 80% revenue, Class B: 15%, Class C: 5%).

### Fact Tables
1. **`FACT_SALES`**
   - **Grain:** One row per transaction line item.
   - **Primary Key:** `line_item_id`.
   - **Foreign Keys:** `date`, `distributor_id`, `workshop_id`, `region_id`, `sku_id`, `promotion_id`.
   - **Reconciliation Invariant:** $\text{Revenue} = \text{Quantity} \times \text{Net Unit Price}$, $\text{Gross Profit} = \text{Revenue} - \text{Cost}$.
2. **`FACT_INVENTORY`**
   - **Grain:** One row per SKU × Distributor × Observation Date.
   - **Primary Key:** `(date, distributor_id, sku_id)`.
   - **Foreign Keys:** `date`, `distributor_id`, `sku_id`.
   - **Reconciliation Invariant:** $\text{Closing} = \text{Opening} + \text{Receipts} - \text{Units Sold}$.
3. **`FACT_DEMAND`**
   - **Grain:** One row per SKU × Region × Week.
   - **Primary Key:** `(week_start_date, sku_id, region_id)`.
   - **Foreign Keys:** `sku_id`, `region_id`.
   - **Business Meaning:** Latent vehicle parc wear demand across regions and seasons.
