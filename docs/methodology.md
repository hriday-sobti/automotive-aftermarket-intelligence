# Methodology & Baseline Estimation Standards

This document describes the baseline estimation techniques, statistical forecasting standards, and inventory modeling logic implemented in the project.

---

## 1. Trade Promotion Baseline Modeling

Evaluating whether a trade marketing campaign was profitable requires an accurate estimate of what sales would have been without the campaign.

### Why Prior-Period Comparisons Fail
Comparing "promotion month sales vs previous month sales" produces misleading conclusions in automotive parts:
1. **Seasonality:** Summer cooling parts naturally surge from March through May regardless of discounting.
2. **Post-Promotional Dips:** Distributors frequently stockpile during promotions, depressing sales in the following month.

### De-seasonalized Rolling Baseline Method
To solve this, the baseline uses transactions where `promotion_id = 'NONE'` within the matching product category and geographic region:
1. Filter sales records for the target category and region during non-promotional windows.
2. Calculate the non-promoted daily run-rates:
   $$\text{Daily Base Units} = \frac{\sum \text{Base Units}}{\text{Active Base Days}}$$
   $$\text{Daily Base GP} = \frac{\sum \text{Base Gross Profit}}{\text{Active Base Days}}$$
3. Scale daily run-rates over the campaign duration $D$:
   $$\text{Baseline Units} = \text{ROUND}(\text{Daily Base Units} \times D)$$
   $$\text{Baseline Gross Profit} = \text{ROUND}(\text{Daily Base GP} \times D, 2)$$
4. Compute incremental variances:
   $$\text{Incremental Units} = \text{Promoted Units} - \text{Baseline Units}$$
   $$\text{Incremental GP} = \text{Promoted GP} - \text{Baseline GP}$$
5. Compute the Promotion Effectiveness Index:
   $$\text{PEI} = \frac{\text{Incremental GP}}{\text{Trade Discount Cost} + \text{Campaign Budget}}$$

---

## 2. Inventory Buffer Sizing Methodology

### Normal Distribution Assumption
Safety stock sizing assumes daily workshop demand over a 90-day window approximates a normal distribution with mean $\bar{D}$ and standard deviation $\sigma_D$.

### Service Level Target
A standard wholesale service level of **95% Cycle Service Level** ($Z = 1.645$) is applied:
- 95% of replenishment cycles will conclude without a stockout.
- For critical Tier-1 distributor channels or high-velocity Class A parts, $Z$ can be adjusted upward (e.g., $Z = 2.326$ for 99%).

### Formula Consistency
All inventory units are maintained at the physical SKU level:
- Demand $\bar{D}$: Physical units per calendar day.
- Lead Time $L$: Integer calendar days.
- Safety Stock $SS = \lceil Z \times \sigma_D \times \sqrt{L} \rceil$: Whole physical units.
- Reorder Point $\text{ROP} = \lceil \bar{D} \times L \rceil + SS$: Whole physical units.

---

## 3. Forecasting Evaluation Standards

### Holdout Period Design
To prevent data leakage, the 24-month horizon is split temporally:
- **Training Window:** 2024-01-01 to 2025-08-31 (87 weeks).
- **Holdout Evaluation Window:** 2025-09-01 to 2025-12-31 (17 weeks).
- Zero observations from the holdout period are visible during model fitting.

### Error Metrics
Models are benchmarked on three standard out-of-sample metrics:
1. **Mean Absolute Error (MAE):**
   $$\text{MAE} = \frac{1}{N} \sum_{i=1}^{N} |y_i - \hat{y}_i|$$
2. **Root Mean Squared Error (RMSE):**
   $$\text{RMSE} = \sqrt{\frac{1}{N} \sum_{i=1}^{N} (y_i - \hat{y}_i)^2}$$
3. **Mean Absolute Percentage Error (MAPE):**
   $$\text{MAPE} = \frac{1}{N} \sum_{i=1}^{N} \left| \frac{y_i - \hat{y}_i}{\max(y_i, 1.0)} \right| \times 100$$
