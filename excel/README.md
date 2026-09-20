# Trade Marketing Commercial Scenario Model

This folder contains the financial spreadsheet model for B2B aftermarket trade discount simulation:
`trade_promotion_scenario_model.xlsx`

## Model Structure
- **Inputs (Cells B6:C14 - Yellow Background):**
  - Baseline Units (Run-rate without promotion)
  - List Price & Cost of Goods Sold (COGS)
  - Standard Wholesale Trade Discount %
  - Campaign Promotional Budget
  - Proposed Promotional Discount %
  - Expected Volume Uplift %
- **Calculations (Cells F6:I14 - Slate Background):**
  - Dynamic formulas computing Net Selling Price, Gross Revenue, COGS, Gross Profit, and Trade Concession Cost.
- **Outputs & KPIs (Cells B17:C21 - Mint Green Background):**
  - Net Incremental Gross Profit (₹)
  - Promotion Effectiveness Index (PEI)
  - Gross Margin Dilution (bps)
  - Automated Commercial Recommendation:
    - `APPROVE: Value Accretive` if PEI > 1.0
    - `REVIEW: Volume Driver / Margin Dilutive` if 0.0 <= PEI <= 1.0
    - `REJECT: Value Destructive` if PEI < 0.0
- **Sensitivity Matrix (Cells F17:L24):**
  - Live two-way sensitivity table calculating Net Incremental Gross Profit across 5 discount tiers (8% - 16%) against 6 uplift levels (15% - 40%).
