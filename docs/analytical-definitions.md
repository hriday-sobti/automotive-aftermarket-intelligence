# Analytical Definitions & Methodology Reference

This document formalizes the mathematical formulas, grains, inputs, and business rationale for every commercial metric used in the Automotive Aftermarket Sales & Trade Marketing Intelligence Platform.

---

## 1. Commercial Sales Metrics

### Net Revenue
- **Definition:** Total realized wholesale invoice value received from parts distributed to workshops, net of promotional discounts and commercial rebates.
- **Formula:** 
  $$\text{Net Revenue} = \sum (\text{Quantity} \times \text{Net Unit Price})$$
  $$\text{Net Unit Price} = \text{ROUND}(\text{List Price} \times (1.0 - \text{Discount Pct}), 2)$$
- **Grain:** Transaction line item level (`FACT_SALES`).
- **Inputs:** `quantity`, `list_price`, `discount_pct`.
- **Business Use:** Core top-line performance indicator, distributor quota tracking, regional mix assessment.
- **Limitations:** Does not reflect distributor sell-out to vehicle owners; represents wholesale sell-through.

### Gross Profit & Gross Margin %
- **Definition:** Realized commercial dollar margin and percentage return above standard product manufacturing/procurement cost.
- **Formula:**
  $$\text{Gross Profit} = \text{Net Revenue} - \text{Total Cost}$$
  $$\text{Gross Margin \%} = \left(\frac{\text{Gross Profit}}{\text{Net Revenue}}\right) \times 100$$
- **Grain:** Transaction line item, product, category, and distributor aggregations.
- **Inputs:** `revenue`, `cost_price`, `quantity`.
- **Business Use:** Margin defense, pricing review, promotional viability checks.

### Sales Velocity
- **Definition:** Physical sales velocity of an individual SKU across distributor sales channels over a 90-day rolling evaluation window.
- **Formula:**
  $$\text{Daily Sales Velocity} = \frac{\sum_{t-90}^{t} \text{Units Sold}}{90}$$
- **Grain:** SKU × Distributor level.
- **Business Use:** Foundation for Days of Inventory (DOI), safety stock sizing, and ABC classification.

---

## 2. Inventory & Stockout Risk Metrics

### Days of Inventory (DOI)
- **Definition:** Estimated duration in days that existing physical warehouse stock will satisfy current consumption run-rates.
- **Formula:**
  $$\text{DOI} = \frac{\text{Current Closing Stock}}{\text{Daily Sales Velocity}}$$
- **Grain:** SKU × Distributor snapshot.
- **Business Use:** Liquidity audit, excess stock identification, and early warning for stock depletion.
- **Limitations:** Highly sensitive to historical velocity when volume is near zero. Capped in calculation to avoid divide-by-zero errors.

### Safety Stock (SS)
- **Definition:** Statistically derived buffer inventory maintained to protect against demand variability during supplier replenishment transit.
- **Formula:**
  $$SS = \lceil Z \times \sigma_D \times \sqrt{L} \rceil$$
  *Where:*
  - $Z = 1.645$ (95% Cycle Service Level normal distribution quantile)
  - $\sigma_D$ = Standard deviation of daily demand over the trailing 90 days
  - $L$ = Supplier lead time in calendar days
- **Grain:** SKU × Distributor replenishment profile.
- **Business Use:** Buffer sizing, automated inventory parameter calibration.

### Reorder Point (ROP)
- **Definition:** The stock level threshold that triggers an automated purchase replenishment order.
- **Formula:**
  $$\text{ROP} = (\bar{D} \times L) + SS$$
  *Where $\bar{D}$ is average daily demand rate.*
- **Grain:** SKU × Distributor warehouse.
- **Business Use:** Triggers purchase orders to avoid running below safety stock during transit.

### Recommended Order Quantity (ROQ)
- **Definition:** Suggested purchase order size calculated to replenish inventory back to target cycle stock (30 days of forward demand).
- **Formula:**
  $$\text{ROQ} = \max\left(0, \lceil \text{ROP} + (\bar{D} \times 30) - \text{Current Stock} \rceil\right)$$

### Composite Stockout Risk Score (0 - 100)
- **Definition:** Multi-factor weighted decision index quantifying immediate stockout vulnerability.
- **Formula:**
  $$\text{Risk Score} = 0.35 \cdot S_{\text{Coverage}} + 0.25 \cdot S_{\text{Demand}} + 0.20 \cdot S_{\text{LeadTime}} + 0.10 \cdot S_{\text{Volatility}} + 0.10 \cdot S_{\text{History}}$$
- **Thresholds:**
  - `Low Risk`: $< 30.0$
  - `Watch`: $30.0 - 55.0$
  - `High Risk`: $55.0 - 75.0$
  - `Critical`: $> 75.0$

---

## 3. Trade Promotion Analytics

### De-seasonalized Rolling Baseline
- **Definition:** Expected sales units, revenue, and gross profit that would have occurred under standard commercial conditions without promotional intervention.
- **Methodology:** Trailing median daily sales in identical product category and regional territory during non-promotional periods (`promotion_id = 'NONE'`), projected across campaign duration.

### Incremental Units & Incremental Gross Profit
- **Formulas:**
  $$\text{Incremental Units} = \text{Promoted Units} - \text{Baseline Units}$$
  $$\text{Incremental Gross Profit} = \text{Promoted Gross Profit} - \text{Baseline Gross Profit}$$

### Promotion Effectiveness Index (PEI)
- **Definition:** Return on investment ratio measuring net dollar profit expansion relative to total promotional investment.
- **Formula:**
  $$\text{PEI} = \frac{\text{Incremental Gross Profit}}{\text{Trade Discount Concessions} + \text{Campaign Budget}}$$
- **Commercial Classification:**
  - $\text{PEI} > 1.0$: **Value Accretive** (Expands total gross profit above all costs).
  - $0.0 \le \text{PEI} \le 1.0$: **Margin Dilutive** (Drives physical volume but shrinks gross profit).
  - $\text{PEI} < 0.0$: **Value Destructive** (Yields lower gross margin dollars than non-promoted baseline).
