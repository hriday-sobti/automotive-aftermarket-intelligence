# Domain Notes: Automotive Aftermarket Distribution

These notes outline how the automotive replacement parts ecosystem operates, who the key commercial players are, and how demand, inventory, and trade marketing interact in practice.

---

## 1. Ecosystem Overview

The automotive aftermarket covers everything that happens after a vehicle rolls out of the showroom: replacement parts, wear-and-tear consumables, maintenance chemicals, accessories, and repair equipment.

Two key structural factors drive demand in this market:
- **Vehicle Parc (Vehicles in Operation):** The total active population of vehicles on the road. Older vehicles naturally consume more parts, and different segments (passenger cars, light commercial vans, heavy-duty trucks, and two-wheelers) run on very different replacement cycles.
- **Wear Profiles:** Fast-moving consumables (brake pads, oil filters, spark plugs, wiper blades) follow recurring replacement intervals based on mileage or calendar time. Major mechanical assemblies (alternators, starters, steering racks, suspension struts) fail probabilistically based on road conditions, driving behavior, and vehicle age.

---

## 2. Market Players & Channel Structure

```text
[Manufacturer / Brand Owner]
         │
         ▼  (Sell-In: Minimum order quantities, volume rebates)
[Authorized Wholesale Distributors]
         │
         ▼  (Sell-Through: Local delivery, credit terms, parts cataloging)
[Independent Workshops & Fleet Garages]
         │
         ▼  (Installation & Service)
[Vehicle Owners / Fleets]
```

1. **Brand Owners / Component Manufacturers:**
   Design, manufacture, and catalog replacement parts under recognized brand names. Commercial goals: maintaining wholesale margins, keeping distributor fill-rates high, and defending market share against cheap unbranded alternatives.
2. **Regional Wholesale Distributors:**
   Commercial partners holding warehouse inventory across geographic clusters. They buy in bulk from manufacturers (sell-in) and supply local garages with daily or same-day delivery (sell-through). Their profitability depends on inventory turnover, sales velocity, and effective working capital management.
3. **Independent Workshops & Fleet Garages:**
   The end-installers diagnosing faults and procuring parts. Their top priorities are delivery speed, fitment accuracy, and catalog reliability. If a distributor doesn't have brake pads in stock when a vehicle is on the hoist, the mechanic will immediately call a competitor.
4. **Vehicle Owners:**
   Usually rely on the mechanic's recommendation, though brand awareness influences willingness to pay for premium OE-quality parts over budget options.

---

## 3. Commercial Dynamics: Sell-In vs. Sell-Through

A classic trap in aftermarket analytics is confusing **sell-in** (manufacturer $\rightarrow$ distributor) with **sell-through** (distributor $\rightarrow$ workshop):
- **Sell-In:** Often spikes at quarter-ends because of promotional schemes, volume discounts, or distributor target chasing. A surge in sell-in does not mean market demand grew—it often means distributors stocked up at lower prices.
- **Sell-Through:** Represents true end-consumption driven by actual vehicle repair events. If sell-in exceeds sell-through for too long, distributors end up sitting on excess inventory and stop ordering in subsequent quarters (the classic bullwhip effect).

---

## 4. Trade Marketing & Promotional Economics

Trade marketing in this market is almost exclusively B2B. Distributors are incentivized through temporary invoice discounts (e.g., 5% to 15%), volume rebates, or seasonal pre-stocking deals (like stocking up on wipers and brake pads before the monsoon).

Evaluating these promotions requires a clear financial baseline:
$$\text{Incremental Units} = \text{Promoted Units} - \text{Baseline Run-Rate Units}$$
$$\text{Incremental Gross Profit} = \text{Promoted Gross Profit} - \text{Baseline Gross Profit}$$
$$\text{Promotion Effectiveness Index (PEI)} = \frac{\text{Incremental Gross Profit}}{\text{Trade Discount Cost} + \text{Campaign Budget}}$$

- **PEI > 1.0:** Value-accretive (the campaign expanded gross margin dollars beyond all costs).
- **0.0 to 1.0:** Margin-dilutive (drove unit volume, but net dollar profit shrank because of price concessions).
- **< 0.0:** Value-destructive (promoted sales produced less gross profit than normal run-rate demand).

---

## 5. How the Analytics Modules Connect

To answer the commercial questions meaningfully, the analysis layers build on each other:

1. **Sales Performance:** Pinpoints revenue concentration (80/20 Pareto), product category margins, and distributor growth rates.
2. **Inventory Risk & Sizing:** Analyzes Days of Inventory (DOI), lead-time exposure, and demand volatility to set dynamic Safety Stock and Reorder Points (ROP) so high-velocity parts don't stock out.
3. **Trade Marketing Analytics:** Strips out baseline demand to measure whether promotions generated true incremental profit or merely gave away margin.
4. **Demand Forecasting:** Forecasts future weekly demand across SKU-region combinations and translates those numbers directly into purchase order quantities.
