# Analytical Assumptions & Methodological Guardrails

This document transparently outlines all assumptions, simplifications, and limitations governing the Automotive Aftermarket Sales & Trade Marketing Intelligence Platform.

---

## 1. Synthetic Data Assumptions
- **Identification:** All data is synthetically modeled to replicate authentic automotive wholesale aftermarket operational environments. No proprietary or confidential corporate records are utilized.
- **Reproducibility:** All stochastic processes rely on deterministic pseudo-random number generators seeded with `RANDOM_SEED = 42`.
- **Ecosystem Dynamics:** The simulation assumes a two-tier distribution model: Manufacturer $\rightarrow$ Regional Wholesale Distributors $\rightarrow$ Multi-Brand Garages / Workshops. End vehicle retail pricing is held constant for catalog modeling.

## 2. Demand & Seasonality Assumptions
- **Latent Demand Model:** Latent market demand reflects registered vehicle parc density, annual mileage wear rates, and meteorological/seasonal stressors (e.g. monsoon brake wear in Q3, thermal cooling stress in Q1-Q2).
- **Macro Trend:** Underlying vehicle fleet growth is assumed at 7.0% per annum over the 24-month horizon.

## 3. Inventory & Supply Chain Assumptions
- **Inventory Balance:** Inventory adheres strictly to mass balance: $\text{Closing} = \text{Opening} + \text{Receipts} - \text{Sold}$.
- **Lead Time Reliability:** Supplier lead times are normally distributed around component-specific standard transit windows (10 to 45 days).
- **Stockout Representation:** A stockout event is triggered when unfulfilled demand occurs at zero inventory. Unmet demand in wholesale channels is partially lost and partially back-ordered in batch replenishment.

## 4. Promotion & Baseline Modeling Assumptions
- **Baseline Construction:** Baseline sales run-rates represent non-promoted periods within the same product category and regional territory.
- **Forward-Buying Effect:** High promotional discounts (>10%) incentivize distributor stockpiling, resulting in lower purchasing run-rates in subsequent periods.
- **Trade Concession Cost:** Trade discount expense represents the dollar variance between standard wholesale list price and the realized discounted invoice price.

## 5. Forecasting Assumptions
- **Temporal Separation:** Training data is strictly restricted to historical periods (2024-01-01 to 2025-08-31). Holdout evaluation (2025-09-01 to 2025-12-31) contains zero future leakage.
- **Model Selection:** Exponential Smoothing and 4-Week Moving Averages are evaluated against naive last-value persistence. Simpler, explainable models are prioritized over complex black-box architectures.

## 6. Analytical Limitations
- **Exogenous Shocks:** The model does not simulate macro supply chain blockades, port closures, or raw material tariff spikes beyond stochastic lead-time variance.
- **Cross-SKU Cannibalization:** Cannibalization within product families (e.g., standard brake pads cannibalizing premium ceramic pads during promotions) is modeled through category aggregate volume shifts rather than cross-price elasticity matrices.
