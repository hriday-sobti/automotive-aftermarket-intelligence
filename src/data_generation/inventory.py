"""Inventory simulation engine for Automotive Aftermarket Intelligence Platform.

Fast, vectorized/batched inventory state flow:
- Strict stock balance equation: closing_stock = opening_stock + receipts - units_sold
- Weekly inventory positions + stockout & receipt events (keeps row count ~20,000 - 40,000 for lightning-fast queries)
- Rigorous lead time modeling and reorder mechanics
"""

from typing import Dict, List, Tuple
import numpy as np
import pandas as pd


def simulate_inventory_flow(
    sales_df: pd.DataFrame,
    products_df: pd.DataFrame,
    distributors_df: pd.DataFrame,
    date_df: pd.DataFrame,
    seed: int = 42
) -> pd.DataFrame:
    """Simulate weekly stock positions and replenishment events tied directly to sales."""
    rng = np.random.default_rng(seed)

    # 1. Map weekly dates
    date_series = pd.to_datetime(date_df["date"])
    weeks = sorted(date_df["year_month"].unique())
    dates_list = sorted(date_df["date"].unique())
    # Use Sunday weekly dates for periodic inventory reporting
    weekly_dates = [d for d in dates_list if pd.to_datetime(d).weekday() == 6]

    lead_time_map = dict(zip(products_df["sku_id"], products_df["standard_lead_time_days"]))
    velocity_map = dict(zip(products_df["sku_id"], products_df["velocity_profile"]))

    # Aggregate sales units by (date, distributor_id, sku_id)
    # Create a quick sparse matrix or multi-index series
    daily_sales = (
        sales_df.groupby(["distributor_id", "sku_id", "date"])["quantity"]
        .sum()
    )

    dist_ids = distributors_df["distributor_id"].tolist()
    sku_ids = products_df["sku_id"].tolist()

    records = []

    # Map dates to integer indices for array manipulation
    num_days = len(dates_list)
    date_to_idx = {d: i for i, d in enumerate(dates_list)}
    sunday_indices = set(date_to_idx[d] for d in weekly_dates)

    for d_id in dist_ids:
        for s_id in sku_ids:
            lead_time = lead_time_map[s_id]
            vel = velocity_map[s_id]

            if vel == "Fast Moving":
                curr_stock = int(rng.integers(200, 450))
                batch_order_qty = 300
                reorder_threshold = 120
            elif vel == "Medium Moving":
                curr_stock = int(rng.integers(60, 180))
                batch_order_qty = 100
                reorder_threshold = 45
            else:
                curr_stock = int(rng.integers(20, 60))
                batch_order_qty = 35
                reorder_threshold = 15

            # Get daily sales array for this (d_id, s_id)
            sales_series = daily_sales.get((d_id, s_id), None)
            sales_arr = np.zeros(num_days, dtype=int)
            if sales_series is not None:
                for dt_str, qty in sales_series.items():
                    sales_arr[date_to_idx[dt_str]] = qty

            # Pipeline of incoming orders: arrival_day_idx -> qty
            receipts_arr = np.zeros(num_days + 60, dtype=int)
            pending_orders = 0

            # Run temporal daily simulation in fast loop
            for day_idx in range(num_days):
                opening_stock = curr_stock
                receipts = receipts_arr[day_idx]
                if receipts > 0:
                    pending_orders = max(0, pending_orders - 1)

                sold = sales_arr[day_idx]
                actual_delivered = min(sold, opening_stock + receipts)
                closing_stock = (opening_stock + receipts) - actual_delivered
                stockout_flag = 1 if closing_stock == 0 and sold > 0 else 0

                # Reorder trigger
                effective_inv = closing_stock + (pending_orders * batch_order_qty)
                if effective_inv <= reorder_threshold and pending_orders < 2:
                    arrival_idx = day_idx + max(4, int(round(rng.normal(lead_time, 1.5))))
                    receipts_arr[arrival_idx] += batch_order_qty
                    pending_orders += 1

                # Record weekly snapshots or critical events (stockouts / major receipts)
                if day_idx in sunday_indices or stockout_flag == 1 or receipts > 0:
                    records.append({
                        "date": dates_list[day_idx],
                        "distributor_id": d_id,
                        "sku_id": s_id,
                        "opening_stock": opening_stock,
                        "receipts": int(receipts),
                        "units_sold": int(actual_delivered),
                        "closing_stock": int(closing_stock),
                        "lead_time_days": lead_time,
                        "stockout_flag": stockout_flag
                    })

                curr_stock = closing_stock

    return pd.DataFrame(records)
