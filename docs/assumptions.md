# Analytical Assumptions & Known Limitations

This document records the modeling assumptions, parameter choices, and known constraints of the project.

---

## 1. Synthetic Data Construction
- **Synthetic Scope:** All datasets are synthetically generated to simulate an automotive wholesale parts distributor environment. No confidential or real-world company records were used.
- **Reproducibility:** Random number generation is seeded with `RANDOM_SEED = 42` across Python and NumPy modules.
- **Two-Tier Model:** The simulation focuses on the wholesale distribution tier (Manufacturer $\rightarrow$ Regional Wholesale Distributors $\rightarrow$ Garages/Workshops). Retail pricing to vehicle owners is held constant.

---

## 2. Demand & Seasonality Parameters
- **Seasonal Factors:** Monthly indices represent real-world automotive stress events:
  - Braking: Monsoon road wear peak in Q3 (July–September).
  - Thermal & Cooling: Pre-summer and summer heat stress in Q1–Q2 (April–June).
  - Electrical & Ignition: Cold battery and starter motor stress in winter (December–January).
- **Macro Trend:** Latent market demand incorporates a steady 7.0% annual vehicle parc expansion rate over the 24-month timeline.

---

## 3. Inventory & Supply Chain Rules
- **Mass Balance:** Warehouse stock strictly satisfies $\text{Closing} = \text{Opening} + \text{Receipts} - \text{Sold}$.
- **Lead Times:** Supplier lead times are normally distributed around component-specific baselines (10 to 45 days).
- **Stockouts:** When closing stock hits 0 and unmet orders exist, unfulfilled units are logged as a stockout event. Wholesale customers either wait for the next replenishment batch or substitute an alternate part.

---

## 4. Trade Marketing Assumptions
- **Baseline Integrity:** Baseline demand is estimated from non-promoted periods within the same product category and regional cluster.
- **Trade Concession Cost:** Represents the wholesale invoice discount given on all units sold during the campaign: $\sum \text{Quantity} \times (\text{List Price} - \text{Net Realized Price})$.
- **Stockpiling Dynamics:** Significant discounts (>10%) produce forward-buying spikes followed by lower reorder volume in subsequent weeks.

---

## 5. Forecasting Assumptions
- **Strict Temporal Split:** Training is strictly bounded to the first 20 months (2024-01-01 to 2025-08-31); the final 4 months (2025-09-01 to 2025-12-31) serve as an out-of-sample holdout test.
- **Model Choice:** Classical explainable time-series models (Moving Averages, Exponential Smoothing) are prioritized over black-box methods to ensure predictions can be directly explained to commercial managers.

---

## 6. Known Limitations
- **Cross-SKU Cannibalization:** Cannibalization within product families (e.g., standard ceramic pads taking volume from semi-metallic pads during discounts) is modeled at category volume shifts rather than an explicit cross-price elasticity matrix.
- **Macro Disruptions:** The model does not simulate extreme black-swan supply disruptions (port blockades, material embargoes) beyond stochastic lead-time variances.
