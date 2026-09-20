"""Analytical export generator for Power BI and executive consumption."""

import os
import sys
import pandas as pd

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.utils.config_utils import load_config, setup_logger
from src.inventory.risk_model import compute_stockout_risk_model
from src.inventory.reorder_logic import compute_reorder_parameters
from src.promotions.promotion_analytics import evaluate_promotions
from src.forecasting.forecast_engine import evaluate_forecasting_models
from src.analytics.opportunity_matrix import compute_sku_opportunity_matrix


def export_analytical_datasets():
    logger = setup_logger("export_analytics")
    config = load_config()
    processed_dir = config["paths"]["processed_dir"]

    logger.info("Loading processed facts and dimensions...")
    sales_df = pd.read_csv(os.path.join(processed_dir, "fact_sales.csv"))
    products_df = pd.read_csv(os.path.join(processed_dir, "dim_product.csv"))
    distributors_df = pd.read_csv(os.path.join(processed_dir, "dim_distributor.csv"))
    inventory_df = pd.read_csv(os.path.join(processed_dir, "fact_inventory.csv"))
    promotions_df = pd.read_csv(os.path.join(processed_dir, "dim_promotion.csv"))
    demand_df = pd.read_csv(os.path.join(processed_dir, "fact_demand.csv"))

    # 1. Inventory Risk Model
    logger.info("Computing stockout risk model...")
    risk_df = compute_stockout_risk_model(sales_df, inventory_df, products_df, distributors_df, config)
    risk_path = os.path.join(processed_dir, "analytical_inventory_risk_scores.csv")
    risk_df.to_csv(risk_path, index=False)
    logger.info(f"Saved {risk_path}: {len(risk_df)} records.")

    # 2. Reorder Parameters
    logger.info("Computing safety stock and reorder parameters...")
    reorder_df = compute_reorder_parameters(sales_df, inventory_df, products_df, config["inventory_risk"]["service_level_z"])
    reorder_path = os.path.join(processed_dir, "analytical_reorder_parameters.csv")
    reorder_df.to_csv(reorder_path, index=False)
    logger.info(f"Saved {reorder_path}: {len(reorder_df)} records.")

    # 3. Trade Promotion Effectiveness
    logger.info("Computing trade promotion effectiveness...")
    promo_perf_df = evaluate_promotions(sales_df, promotions_df, products_df)
    promo_path = os.path.join(processed_dir, "analytical_promotion_effectiveness.csv")
    promo_perf_df.to_csv(promo_path, index=False)
    logger.info(f"Saved {promo_path}: {len(promo_perf_df)} campaign evaluations.")

    # 4. SKU Opportunity Matrix
    logger.info("Computing commercial opportunity matrix...")
    opp_df = compute_sku_opportunity_matrix(sales_df, products_df)
    opp_path = os.path.join(processed_dir, "analytical_sku_opportunity_matrix.csv")
    opp_df.to_csv(opp_path, index=False)
    logger.info(f"Saved {opp_path}: {len(opp_df)} SKUs classified into strategic quadrants.")

    # 5. Demand Forecast Benchmark
    logger.info("Computing demand forecasting models benchmark...")
    forecast_df, forecast_summary = evaluate_forecasting_models(demand_df, config["forecasting"]["test_split_date"])
    forecast_path = os.path.join(processed_dir, "analytical_forecast_evaluation.csv")
    forecast_df.to_csv(forecast_path, index=False)
    logger.info(f"Saved {forecast_path}: {len(forecast_df)} forecast evaluation rows.")
    logger.info(f"Forecasting benchmark metrics: {forecast_summary}")

    logger.info("All analytical decision layers successfully exported.")


if __name__ == "__main__":
    export_analytical_datasets()
