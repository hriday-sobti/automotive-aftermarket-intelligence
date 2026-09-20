"""Exploratory Data Analysis (EDA) engine and reporting script.

Performs structured statistical examination without external markdown dependencies.
"""

import os
import sys
import numpy as np
import pandas as pd

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from src.utils.config_utils import load_config, setup_logger


def df_to_markdown_simple(df: pd.DataFrame) -> str:
    """Render a DataFrame as a clean Markdown table string without tabulate dependency."""
    cols = list(df.columns)
    header = "| " + " | ".join(str(c) for c in cols) + " |"
    separator = "| " + " | ".join(["---"] * len(cols)) + " |"
    rows = []
    for _, row in df.iterrows():
        row_str = "| " + " | ".join(str(row[c]) for c in cols) + " |"
        rows.append(row_str)
    return "\n".join([header, separator] + rows)


def run_eda():
    logger = setup_logger("eda")
    config = load_config()
    processed_dir = config["paths"]["processed_dir"]
    reports_dir = config["paths"]["reports_dir"]
    os.makedirs(reports_dir, exist_ok=True)

    logger.info("Loading processed datasets for EDA...")
    sales_df = pd.read_csv(os.path.join(processed_dir, "fact_sales.csv"))
    products_df = pd.read_csv(os.path.join(processed_dir, "dim_product.csv"))
    inventory_df = pd.read_csv(os.path.join(processed_dir, "fact_inventory.csv"))

    eda_lines = ["# Exploratory Data Analysis (EDA) Audit Report\n\n"]
    eda_lines.append(f"- **Total Sales Line Items Analyzed:** {len(sales_df):,}\n")
    eda_lines.append(f"- **Total Net Revenue:** ₹{sales_df['revenue'].sum():,.2f}\n")
    eda_lines.append(f"- **Total Gross Profit:** ₹{sales_df['gross_profit'].sum():,.2f}\n")
    eda_lines.append(f"- **Overall Gross Margin:** {((sales_df['gross_profit'].sum() / sales_df['revenue'].sum()) * 100):.2f}%\n\n")

    # 1. Distributional Statistics
    eda_lines.append("## 1. Sales Transaction Numeric Distributions\n\n")
    num_cols = ["quantity", "list_price", "discount_pct", "net_unit_price", "revenue", "cost", "gross_profit", "gross_margin_pct"]
    stats_df = sales_df[num_cols].describe().T.reset_index().rename(columns={"index": "metric"})
    eda_lines.append(df_to_markdown_simple(stats_df) + "\n\n")

    # 2. Category Performance Summary
    eda_lines.append("## 2. Product Category Performance Breakdown\n\n")
    merged_sales = sales_df.merge(products_df[["sku_id", "product_category", "velocity_profile"]], on="sku_id")
    cat_summary = (
        merged_sales.groupby("product_category")
        .agg(
            total_revenue=("revenue", "sum"),
            total_units=("quantity", "sum"),
            total_profit=("gross_profit", "sum"),
            avg_discount=("discount_pct", "mean"),
            avg_margin=("gross_margin_pct", "mean")
        )
        .reset_index()
    )
    cat_summary["revenue_share_pct"] = np.round((cat_summary["total_revenue"] / sales_df["revenue"].sum()) * 100, 2)
    cat_summary["avg_discount"] = np.round(cat_summary["avg_discount"] * 100, 2)
    cat_summary["avg_margin"] = np.round(cat_summary["avg_margin"], 2)
    cat_summary["total_revenue"] = np.round(cat_summary["total_revenue"], 2)
    cat_summary["total_profit"] = np.round(cat_summary["total_profit"], 2)
    cat_summary = cat_summary.sort_values(by="total_revenue", ascending=False)
    eda_lines.append(df_to_markdown_simple(cat_summary) + "\n\n")

    # 3. Inventory Stockout Analysis
    eda_lines.append("## 3. Inventory Stockout & Flow Profile\n\n")
    stockout_rate = (inventory_df["stockout_flag"].sum() / len(inventory_df)) * 100
    eda_lines.append(f"- **Total Inventory Records:** {len(inventory_df):,}\n")
    eda_lines.append(f"- **Stockout Incidents Recorded:** {inventory_df['stockout_flag'].sum():,} ({stockout_rate:.2f}% of observation days)\n")
    eda_lines.append(f"- **Average Closing Stock across Distributor-SKUs:** {inventory_df['closing_stock'].mean():.1f} units\n")
    eda_lines.append(f"- **Average Supplier Lead Time:** {inventory_df['lead_time_days'].mean():.1f} days\n\n")

    report_content = "".join(eda_lines)
    report_file = os.path.join(reports_dir, "eda_statistical_summary.md")
    with open(report_file, "w", encoding="utf-8") as f:
        f.write(report_content)

    logger.info(f"EDA completed successfully. Report saved to {report_file}")


if __name__ == "__main__":
    run_eda()
