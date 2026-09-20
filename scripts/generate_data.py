"""Master data generation script for Automotive Aftermarket Platform."""

import os
import sys
import pandas as pd

# Add project root to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.utils.config_utils import load_config, setup_logger
from src.data_generation.dimensions import generate_all_dimensions
from src.data_generation.demand import generate_demand_profiles
from src.data_generation.promotions import generate_promotions
from src.data_generation.sales import generate_sales_transactions
from src.data_generation.inventory import simulate_inventory_flow
from src.validation.validator import DataValidator
from src.cleaning.cleaning_pipeline import clean_and_engineer_sales, calculate_sku_pareto


def main():
    logger = setup_logger("generate_data")
    logger.info("Initializing synthetic data generation pipeline...")

    config = load_config()
    raw_dir = config["paths"]["raw_dir"]
    interim_dir = config["paths"]["interim_dir"]
    processed_dir = config["paths"]["processed_dir"]
    seed = config["project"]["random_seed"]
    target_sales = config["scale"]["target_sales_rows"]

    os.makedirs(raw_dir, exist_ok=True)
    os.makedirs(interim_dir, exist_ok=True)
    os.makedirs(processed_dir, exist_ok=True)

    # 1. Dimensions
    logger.info("Generating dimension tables...")
    dimensions = generate_all_dimensions(config)
    for name, df in dimensions.items():
        df.to_csv(os.path.join(raw_dir, f"{name}.csv"), index=False)
        logger.info(f"Saved {name}: {len(df)} rows")

    # 2. Demand profiles
    logger.info("Generating latent demand profiles...")
    demand_df = generate_demand_profiles(
        products_df=dimensions["dim_product"],
        regions_df=dimensions["dim_region"],
        start_date=config["timeline"]["start_date"],
        end_date=config["timeline"]["end_date"],
        seed=seed
    )
    demand_df.to_csv(os.path.join(raw_dir, "fact_demand.csv"), index=False)
    logger.info(f"Saved fact_demand: {len(demand_df)} rows")

    # 3. Promotions
    logger.info("Generating promotional campaigns...")
    promotions_df = generate_promotions(
        products_df=dimensions["dim_product"],
        regions_df=dimensions["dim_region"],
        seed=seed
    )
    promotions_df.to_csv(os.path.join(raw_dir, "dim_promotion.csv"), index=False)
    logger.info(f"Saved dim_promotion: {len(promotions_df)} rows")

    # 4. Sales transactions
    logger.info(f"Generating sales transactions (target: {target_sales} rows)...")
    sales_df = generate_sales_transactions(
        dimensions=dimensions,
        promotions_df=promotions_df,
        target_rows=target_sales,
        seed=seed
    )
    sales_df.to_csv(os.path.join(raw_dir, "raw_sales.csv"), index=False)
    logger.info(f"Generated raw sales: {len(sales_df)} line items across {sales_df['transaction_id'].nunique()} transactions")

    # 5. Inventory simulation
    logger.info("Simulating inventory stock balance and lead times...")
    inventory_df = simulate_inventory_flow(
        sales_df=sales_df,
        products_df=dimensions["dim_product"],
        distributors_df=dimensions["dim_distributor"],
        date_df=dimensions["dim_date"],
        seed=seed
    )
    inventory_df.to_csv(os.path.join(raw_dir, "fact_inventory.csv"), index=False)
    logger.info(f"Saved fact_inventory: {len(inventory_df)} stock observations")

    # 6. Validation
    logger.info("Running pre-flight validation checks...")
    validator = DataValidator()
    validator.validate_dimensions(dimensions)
    valid_sales, rejected_sales = validator.validate_sales(sales_df, dimensions, promotions_df)
    validator.validate_inventory(inventory_df)

    val_report = validator.get_summary_report()
    val_report.to_csv(os.path.join(interim_dir, "data_validation_report.csv"), index=False)
    logger.info("Validation summary:\n" + val_report.to_string())

    if not rejected_sales.empty:
        rejected_sales.to_csv(os.path.join(interim_dir, "rejected_sales.csv"), index=False)
        logger.warning(f"Logged {len(rejected_sales)} rejected sales rows to interim directory.")

    # 7. Cleaning and feature engineering
    logger.info("Applying feature engineering to sales fact table...")
    processed_sales = clean_and_engineer_sales(valid_sales, dimensions["dim_product"])
    processed_sales.to_csv(os.path.join(processed_dir, "fact_sales.csv"), index=False)

    # Save cleaned dimensions & inventory to processed
    for name, df in dimensions.items():
        df.to_csv(os.path.join(processed_dir, f"{name}.csv"), index=False)
    promotions_df.to_csv(os.path.join(processed_dir, "dim_promotion.csv"), index=False)
    inventory_df.to_csv(os.path.join(processed_dir, "fact_inventory.csv"), index=False)
    demand_df.to_csv(os.path.join(processed_dir, "fact_demand.csv"), index=False)

    # Pareto concentration table
    pareto_df = calculate_sku_pareto(processed_sales)
    pareto_df.to_csv(os.path.join(processed_dir, "dim_sku_pareto.csv"), index=False)
    logger.info(f"Saved dim_sku_pareto: {len(pareto_df)} SKUs classified into Pareto tiers.")

    logger.info("Data generation, validation, and processing completed successfully.")


if __name__ == "__main__":
    main()
