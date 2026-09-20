# Domain Understanding: Automotive Aftermarket Sales & Trade Marketing

## 1. Automotive Aftermarket Ecosystem Context
The automotive aftermarket encompasses the manufacturing, distribution, retailing, and installation of vehicle parts, chemicals, equipment, and accessories after the original equipment manufacturer (OEM) sale.

In this ecosystem:
- **Vehicle Parc (Vehicles in Operation - VIO):** The total population of active registered vehicles. The age distribution, mileage accumulation, and vehicle segments (Passenger Cars, Light Commercial Vehicles - LCV, Heavy Commercial Vehicles - HCV, and Two-Wheelers) drive non-discretionary replacement cycles.
- **Replacement Demand:** Wear-and-tear parts (brake pads, filters, spark plugs, wiper blades, fluids) exhibit recurring demand cycles governed by operational hours/kilometers. Higher-value assemblies (alternators, starters, steering racks, suspension struts) fail probabilistically based on operating environment and vehicle age.

## 2. Key Ecosystem Actors & Value Chain
1. **Manufacturer / Brand Owner (e.g., Tier-1 Aftermarket Supplier):** Designs, packages, and supplies cataloged SKUs. Focuses on brand equity, distributor fill-rates, gross margin health, and channel sell-in.
2. **Authorized Distributors / Wholesalers:** Regional channel partners holding regional stock. They purchase from manufacturers (sell-in) and supply workshops, retailers, and secondary jobbers (sell-through). Their performance is measured by sales velocity, inventory turnover, and service levels.
3. **Independent Workshops & Service Centers:** End-installers diagnosing vehicle faults and procuring replacement parts on-demand or with short daily lead times. They prioritize parts availability, fitment reliability, and delivery speed.
4. **End Vehicle Owners:** Rely on workshop recommendations; brand awareness impacts willingness to pay for premium versus economy replacement parts.

## 3. Demand Flow & Commercial Dynamics
- **Sell-In vs. Sell-Through:**
  - *Sell-In:* Manufacturer to Distributor. Often inflated by quarter-end trade promotions, rebate schemes, and minimum order quantities.
  - *Sell-Through:* Distributor to Workshop/Retailer. Reflects genuine market consumption driven by vehicle repair events.
- **Lead Times & Supply Volatility:** Aftermarket supply chains balance import/central warehouse transit lead times (14–45 days) with distributor local fulfillment windows (same day to 48 hours). Disruptions lead to stockouts and lost sales because workshops will substitute competing brands if parts are unavailable.
- **Safety Stock & Reorder Points:** Critical to absorb demand volatility without tying up excessive working capital in slow-moving SKUs.

## 4. Trade Marketing & Promotion Economics
Trade marketing in the aftermarket is primarily business-to-business (B2B):
- **Mechanism:** Volume rebates, temporary invoice discounts (e.g., 5%–15%), seasonal stocking packages (e.g., pre-monsoon wiper/brake campaigns, pre-winter battery checks), and bundled loyalty incentives.
- **Baseline vs. Incremental Sales:**
  - *Baseline Sales:* The volume expected under business-as-usual conditions without price concessions or promotional funding.
  - *Promotional Uplift:* The observed sales increase during the promotional window.
  - *Forward Buying / Stockpiling:* The risk that distributors purchase future demand at discounted prices, cannibalizing subsequent high-margin periods.
- **Commercial Viability Formula:**
  $$\text{Incremental Gross Profit} = \text{Promoted Gross Profit} - \text{Baseline Gross Profit}$$
  $$\text{Promotion Effectiveness} = \frac{\text{Incremental Gross Profit}}{\text{Promotion Cost}}$$
  If Incremental Gross Profit is less than the trade discount cost plus promotional budget, the promotion destroys value despite generating volume uplift.

## 5. The Four Integrated Analytical Layers
To solve the core business question—*Which products should an aftermarket distributor prioritize, where is sales potential being lost, which inventory is at risk, and which trade promotions are actually worth funding?*—the analytical platform connects four foundational layers:

1. **Sales Performance Intelligence:** Identifies Pareto concentration (top 20% SKUs driving 80% revenue), category contribution, distributor growth trajectories, and gross margin health.
2. **Inventory & Stockout Risk:** Analyzes inventory coverage (Days of Inventory), demand volatility (Coefficient of Variation), and lead-time exposure to produce an explainable, composite **Stockout Risk Score** that triggers proactive replenishment.
3. **Trade Promotion Effectiveness:** Disentangles true demand uplift from baseline run-rates, quantifying whether promotional investments yielded positive net incremental gross margin.
4. **Demand Forecasting & Operational Reorder Logic:** Forecasts forward demand at the SKU-Region-Period grain and translates predictive estimates into operational parameters: Safety Stock, Reorder Points, and Recommended Order Quantities.
