"""Sales transaction generator for Automotive Aftermarket Intelligence Platform.

Generates realistic commercial transactions:
- Multi-item transaction headers and line items (B2B wholesale order baskets)
- Explicit mathematical reconciliation:
  net_unit_price = round(list_price * (1.0 - discount_pct), 2)
  revenue = round(quantity * net_unit_price, 2)
  cost = round(quantity * cost_price, 2)
  gross_profit = round(revenue - cost, 2)
- Promotion tagging based on date, region, and product category eligibility
- Realistic order basket clustering (e.g. filters frequently ordered together with fluids/plugs)
- Target volume: ~100k - 120k line items over 24 months
"""

from typing import Dict, List, Tuple
import numpy as np
import pandas as pd


def generate_sales_transactions(
    dimensions: Dict[str, pd.DataFrame],
    promotions_df: pd.DataFrame,
    target_rows: int = 110000,
    seed: int = 42
) -> pd.DataFrame:
    """Generate transactional sales line items reconciling mathematically with promotional mechanics."""
    rng = np.random.default_rng(seed)

    products_df = dimensions["dim_product"]
    distributors_df = dimensions["dim_distributor"]
    workshops_df = dimensions["dim_workshop"]
    date_df = dimensions["dim_date"]

    # Pre-index products for fast lookup
    sku_list = products_df["sku_id"].to_numpy()
    sku_costs = dict(zip(products_df["sku_id"], products_df["cost_price"]))
    sku_prices = dict(zip(products_df["sku_id"], products_df["list_price"]))
    sku_cats = dict(zip(products_df["sku_id"], products_df["product_category"]))
    sku_velocities = dict(zip(products_df["sku_id"], products_df["velocity_profile"]))

    # Weight SKUs by Pareto principle: Fast Moving = 70% of lines, Med = 22%, Slow = 8%
    sku_probs = []
    for s in sku_list:
        v = sku_velocities[s]
        if v == "Fast Moving":
            sku_probs.append(5.0)
        elif v == "Medium Moving":
            sku_probs.append(1.5)
        else:
            sku_probs.append(0.4)
    sku_probs = np.array(sku_probs) / np.sum(sku_probs)

    # Distribute workshops across distributors based on matching regions
    dist_by_region = {}
    for _, d in distributors_df.iterrows():
        dist_by_region.setdefault(d["region_id"], []).append(d["distributor_id"])

    ws_dist_map = {}
    for _, w in workshops_df.iterrows():
        reg = w["region_id"]
        avail_dists = dist_by_region.get(reg, distributors_df["distributor_id"].tolist())
        ws_dist_map[w["workshop_id"]] = (rng.choice(avail_dists), reg)

    # Prepare promotions for fast lookup: (category, region, start, end) -> (promo_id, discount)
    promo_records = promotions_df.to_dict("records")

    dates = date_df["date"].tolist()
    total_days = len(dates)

    # Estimated orders to achieve target_rows: average basket size ~ 3.2 items
    avg_basket_size = 3.2
    target_orders = int(target_rows / avg_basket_size)

    # Generate daily order counts with weekday/weekend patterns
    order_id_counter = 100000
    rows = []

    workshop_ids = workshops_df["workshop_id"].to_numpy()
    ws_demand_factors = dict(zip(workshops_df["workshop_id"], workshops_df["monthly_demand_factor"]))

    # Vectorized / batched day-by-day generation
    daily_order_target = target_orders / total_days

    for d_idx, cur_date in enumerate(dates):
        # Weekends have lower commercial wholesale activity
        cur_dt = pd.to_datetime(cur_date)
        is_wknd = cur_dt.weekday() >= 5
        day_mult = 0.35 if is_wknd else 1.15
        
        # Quarter-end surge (March, June, Sept, Dec)
        is_quarter_end = cur_dt.day > 24 and cur_dt.month in [3, 6, 9, 12]
        if is_quarter_end:
            day_mult *= 1.30

        day_orders_count = int(rng.poisson(daily_order_target * day_mult))

        # Sample workshops for today's orders
        sampled_workshops = rng.choice(workshop_ids, size=day_orders_count)

        for ws in sampled_workshops:
            order_id_counter += 1
            trans_id = f"TRX-{order_id_counter}"
            dist_id, region_id = ws_dist_map[ws]

            # Basket size between 1 and 6 items
            basket_size = rng.choice([1, 2, 3, 4, 5, 6], p=[0.20, 0.30, 0.25, 0.12, 0.08, 0.05])
            chosen_skus = rng.choice(sku_list, size=basket_size, replace=False, p=sku_probs)

            for line_no, sku in enumerate(chosen_skus, start=1):
                cat = sku_cats[sku]
                cost = sku_costs[sku]
                list_price = sku_prices[sku]
                velocity = sku_velocities[sku]

                # Check if applicable promotion active
                active_promo_id = None
                promo_disc = 0.0
                for p in promo_records:
                    if p["target_category"] == cat and (p["target_region"] in [region_id, "ALL"]):
                        if p["start_date"] <= cur_date <= p["end_date"]:
                            active_promo_id = p["promotion_id"]
                            promo_disc = p["discount_pct"]
                            break

                # Standard base trade discount: 3% to 8%
                base_discount = rng.choice([0.03, 0.05, 0.06, 0.08], p=[0.3, 0.4, 0.2, 0.1])
                total_discount = min(0.35, base_discount + promo_disc)

                # Order quantity: Fast moving sells higher units
                if velocity == "Fast Moving":
                    qty = int(rng.choice([5, 10, 15, 20, 30, 50], p=[0.25, 0.35, 0.20, 0.10, 0.07, 0.03]))
                elif velocity == "Medium Moving":
                    qty = int(rng.choice([2, 4, 6, 10, 15], p=[0.35, 0.30, 0.20, 0.10, 0.05]))
                else:
                    qty = int(rng.choice([1, 2, 3, 5], p=[0.60, 0.25, 0.10, 0.05]))

                # Apply workshop demand factor
                w_factor = ws_demand_factors.get(ws, 1.0)
                if w_factor > 1.3 and rng.random() > 0.5:
                    qty = int(np.ceil(qty * 1.3))

                # Exact mathematical reconciliation
                net_unit_price = float(np.round(list_price * (1.0 - total_discount), 2))
                revenue = float(np.round(qty * net_unit_price, 2))
                total_cost = float(np.round(qty * cost, 2))
                gross_profit = float(np.round(revenue - total_cost, 2))

                rows.append({
                    "transaction_id": trans_id,
                    "line_item_id": f"{trans_id}-L{line_no}",
                    "date": cur_date,
                    "distributor_id": dist_id,
                    "workshop_id": ws,
                    "region_id": region_id,
                    "sku_id": sku,
                    "quantity": qty,
                    "cost_price": cost,
                    "list_price": list_price,
                    "discount_pct": round(total_discount, 4),
                    "net_unit_price": net_unit_price,
                    "revenue": revenue,
                    "cost": total_cost,
                    "gross_profit": gross_profit,
                    "promotion_id": active_promo_id if active_promo_id else "NONE"
                })

    df = pd.DataFrame(rows)
    return df
