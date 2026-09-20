# Exploratory Data Analysis (EDA) Audit Report

- **Total Sales Line Items Analyzed:** 88,659
- **Total Net Revenue:** ₹2,433,028,061.72
- **Total Gross Profit:** ₹872,954,426.94
- **Overall Gross Margin:** 35.88%

## 1. Sales Transaction Numeric Distributions

| metric | count | mean | std | min | 25% | 50% | 75% | max |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| quantity | 88659.0 | 11.658229846941653 | 9.273183679663136 | 1.0 | 5.0 | 10.0 | 15.0 | 65.0 |
| list_price | 88659.0 | 2934.9813862100864 | 2494.0998639537274 | 193.57 | 1487.94 | 1973.67 | 3859.25 | 15272.92 |
| discount_pct | 88659.0 | 0.061805682446226556 | 0.03349171421262808 | 0.03 | 0.05 | 0.05 | 0.08 | 0.23 |
| net_unit_price | 88659.0 | 2758.187207502904 | 2361.6674631761025 | 152.92 | 1402.26 | 1857.16 | 3602.8 | 14814.73 |
| revenue | 88659.0 | 27442.538960737205 | 27580.213504721203 | 309.72 | 9788.75 | 18816.0 | 35251.6 | 302871.4 |
| cost | 88659.0 | 17596.336917628214 | 18000.64601833184 | 244.26 | 6265.35 | 12176.9 | 22186.26 | 207742.6 |
| gross_profit | 88659.0 | 9846.202043108991 | 9989.561458645707 | 65.46 | 3553.4 | 6900.5 | 12472.900000000001 | 110970.6 |
| gross_margin_pct | 88659.0 | 35.862237674686156 | 6.64735716221666 | 9.63 | 30.37 | 36.06 | 41.15 | 50.32 |

## 2. Product Category Performance Breakdown

| product_category | total_revenue | total_units | total_profit | avg_discount | avg_margin | revenue_share_pct |
| --- | --- | --- | --- | --- | --- | --- |
| Braking Systems | 1338950762.98 | 511163 | 475530783.36 | 6.49 | 34.94 | 55.03 |
| Filtration | 673007012.2 | 451663 | 268753934.73 | 6.18 | 39.71 | 27.66 |
| Electrical & Ignition | 244801438.51 | 32119 | 78802630.36 | 5.31 | 31.66 | 10.06 |
| Thermal & Cooling | 88518161.6 | 18961 | 24412900.7 | 5.45 | 27.95 | 3.64 |
| Chassis & Steering | 87750686.43 | 19701 | 25454177.79 | 5.62 | 29.0 | 3.61 |

## 3. Inventory Stockout & Flow Profile

- **Total Inventory Records:** 314,934
- **Stockout Incidents Recorded:** 15 (0.00% of observation days)
- **Average Closing Stock across Distributor-SKUs:** 161.3 units
- **Average Supplier Lead Time:** 21.2 days

