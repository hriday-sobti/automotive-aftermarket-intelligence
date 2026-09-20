# Trade Marketing Commercial Scenario Model

This directory contains the financial spreadsheet model for B2B wholesale trade discount sensitivity analysis:
- **`trade_promotion_scenario_model.xlsx`** (Native Excel workbook with dynamic spreadsheet formulas and two-way sensitivity matrix)
- **`scenario_model_reconciliation.csv`** (Plain-text tabular version viewable directly on GitHub in your web browser)
- **`scenario_model_inputs.csv`** (Baseline and promotional parameters table)

---

## Why Does Clicking "Raw" on GitHub Show an Error for `.xlsx`?

**`.xlsx` is a zipped binary file format (Office Open XML), not a plain text file.** 

When you click the **"Raw"** button on GitHub for an Excel file (`.xlsx`), your browser tries to display raw binary bytes as text or throws a download prompt/error because web browsers cannot render raw spreadsheet binaries directly as HTML text.

### How to Open and View It:
1. **To Open in Microsoft Excel / LibreOffice:**
   - On GitHub, go to `excel/scenario_model/trade_promotion_scenario_model.xlsx`.
   - Click the **"Download"** button (or the download icon next to "Raw").
   - Open the downloaded `.xlsx` file in Excel.
2. **To View Directly in GitHub's Web Interface:**
   - Open **`scenario_model_reconciliation.csv`** or **`scenario_model_inputs.csv`** in this same folder to see the exact numbers rendered cleanly in GitHub's table viewer.

---

## Model Structure & Formulas

### 1. Baseline vs. Promoted Financial Reconciliation
| Metric | Baseline | Promoted | Variance | Formula in Excel |
| :--- | :---: | :---: | :---: | :--- |
| **Total Units Sold** | 15,000 | 19,200 | +4,200 | `=ROUND(C6*(1+C14), 0)` |
| **Net Selling Price / Unit** | ₹1,757.50 | ₹1,628.00 | -₹129.50 | `=C7*(1-C13)` |
| **Gross Revenue** | ₹26,362,500 | ₹31,257,600 | +₹4,895,100 | `=H7*H8` |
| **Cost of Goods Sold** | ₹17,250,000 | ₹22,080,000 | +₹4,830,000 | `=H7*C8` |
| **Gross Profit** | ₹9,112,500 | ₹9,177,600 | +₹65,100 | `=H9-H10` |
| **Realized Gross Margin %** | 34.57% | 29.36% | -5.21% | `=H11/H9` |
| **Trade Concession Cost** | ₹1,387,500 | ₹4,262,400 | +₹2,874,900 | `=H7*(C7-H8)` |
| **Total Promotion Cost** | ₹0 | ₹4,612,400 | +₹4,612,400 | `=H13+C10` |
| **Net Incremental Profit** | ₹0 | **₹65,100** | **+₹65,100** | `=H11-G11` |
| **Promotion Effectiveness (PEI)**| — | **0.01x** | — | `=I11/H14` |

---

## Live Sensitivity Table (Discount % vs Volume Uplift %)

The Excel model contains a live two-way sensitivity matrix in cells `F17:L24` calculating Net Incremental Gross Profit (₹) across 5 discount tiers and 6 volume uplift levels:

$$= \text{ROUND}((\$C\$6 \times (1 + \text{Uplift})) \times ((\$C\$7 \times (1 - \text{Discount})) - \$C\$8) - \$G\$11, 0)$$
