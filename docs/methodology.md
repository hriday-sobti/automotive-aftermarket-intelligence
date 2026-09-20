# Analytical Methodology & Statistical Standards

## 1. End-to-End Analytical Pipeline
The platform implements a deterministic sequence connecting data generation to commercial decision-support:

```text
Synthetic Domain Generator ──> Pre-Flight Validation ──> Relational Database
                                                              │
┌───────────────────────────┬─────────────────────────────────┴─────────────────────────────────┐
│                           │                                                                   │
▼                           ▼                                                                   ▼
Sales & Pareto Intelligence  Inventory Risk & ROP Logic   Promotion Effectiveness   Demand Forecasting
- Revenue Contribution      - DOI & Velocity              - De-seasonalized Baseline - Exponential Smoothing
- YoY Growth Matrix         - Composite Risk Scoring      - Net Incremental Profit   - Holdout Evaluation
```

## 2. Statistical Baseline Methodology
Evaluating trade promotions without proper baselines distorts commercial conclusions:
- **Baseline Construction:** Non-promoted transactions (`promotion_id = 'NONE'`) in the matching product category and region form the reference daily sales rate.
- **Incremental Volume:** Promoted units minus expected baseline units over identical duration.
- **Financial Uplift:** Incremental Gross Profit compared against the sum of trade discounts granted and fixed campaign marketing budgets.

## 3. Inventory Optimization Formulations
- **Safety Stock Formulation:**
  $$SS = \lceil Z \times \sigma_D \times \sqrt{L} \rceil$$
  Where $Z = 1.645$ (95% Cycle Service Level), $\sigma_D$ is daily demand standard deviation over trailing 90 days, and $L$ is lead time in days.
- **Reorder Point (ROP):**
  $$\text{ROP} = (\bar{D} \times L) + SS$$
- **Composite Risk Normalization:**
  Weights: Inventory Coverage (35%), Demand Pressure (25%), Lead Time (20%), Volatility CV (10%), Stockout Rate (10%).

## 4. Forecasting Validation
- Strict temporal split: Training window through 2025-08-31, holdout window from 2025-09-01 through 2025-12-31.
- No future information is leaked into model estimation.
- Models evaluated on Out-of-Sample MAE, RMSE, and MAPE.
