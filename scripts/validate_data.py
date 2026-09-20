"""Dedicated standalone data validation runner."""

import os
import sys
import pandas as pd

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.utils.config_utils import load_config, setup_logger
from src.validation.validator import DataValidator


def main():
    logger = setup_logger("validate_data")
    logger.info("Running pre-flight data integrity assertions...")
    config = load_config()
    raw_dir = config["paths"]["raw_dir"]
    interim_dir = config["paths"]["interim_dir"]

    # Load tables
    dim_names = ["dim_region", "dim_vehicle_segment", "dim_product", "dim_distributor", "dim_workshop", "dim_date"]
    dimensions = {d: pd.read_csv(os.path.join(raw_dir, f"{d}.csv")) for d in dim_names}
    promotions_df = pd.read_csv(os.path.join(raw_dir, "dim_promotion.csv"))
    sales_df = pd.read_csv(os.path.join(raw_dir, "raw_sales.csv"))
    inventory_df = pd.read_csv(os.path.join(raw_dir, "fact_inventory.csv"))

    validator = DataValidator()
    validator.validate_dimensions(dimensions)
    valid_sales, rejected_sales = validator.validate_sales(sales_df, dimensions, promotions_df)
    validator.validate_inventory(inventory_df)

    report = validator.get_summary_report()
    report_path = os.path.join(interim_dir, "data_validation_report.csv")
    report.to_csv(report_path, index=False)
    logger.info(f"Validation finished. Audit saved to {report_path}:\n" + report.to_string())


if __name__ == "__main__":
    main()
