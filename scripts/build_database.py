"""Database builder and data loader script for Aftermarket Platform.

Loads processed CSV dimensional and fact tables into the relational database engine.
Supports both SQLite (local embedded) and PostgreSQL (via connection string if provided).
"""

import os
import sys
import sqlite3
import pandas as pd
from sqlalchemy import create_engine, text

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.utils.config_utils import load_config, setup_logger


def build_database():
    logger = setup_logger("build_database")
    config = load_config()

    db_path = config["database"]["sqlite_path"]
    schema_path = config["database"]["schema_ddl_path"]
    processed_dir = config["paths"]["processed_dir"]

    os.makedirs(os.path.dirname(db_path), exist_ok=True)

    logger.info(f"Connecting to relational database at {db_path}...")
    engine = create_engine(f"sqlite:///{db_path}")

    # 1. Execute DDL
    logger.info(f"Executing DDL script from {schema_path}...")
    with open(schema_path, "r", encoding="utf-8") as f:
        ddl_script = f.read()

    # SQLite executes script
    with sqlite3.connect(db_path) as conn:
        cursor = conn.cursor()
        cursor.executescript(ddl_script)
        conn.commit()

    logger.info("Database tables and indexes created successfully.")

    # 2. Table Load Order
    load_sequence = [
        ("dim_date", "dim_date.csv"),
        ("dim_region", "dim_region.csv"),
        ("dim_vehicle_segment", "dim_vehicle_segment.csv"),
        ("dim_product", "dim_product.csv"),
        ("dim_distributor", "dim_distributor.csv"),
        ("dim_workshop", "dim_workshop.csv"),
        ("dim_promotion", "dim_promotion.csv"),
        ("dim_sku_pareto", "dim_sku_pareto.csv"),
        ("fact_demand", "fact_demand.csv"),
        ("fact_inventory", "fact_inventory.csv"),
        ("fact_sales", "fact_sales.csv")
    ]

    for table_name, file_name in load_sequence:
        csv_file = os.path.join(processed_dir, file_name)
        if not os.path.exists(csv_file):
            logger.error(f"Required table CSV missing: {csv_file}")
            continue

        logger.info(f"Loading {table_name} from {csv_file}...")
        df = pd.read_csv(csv_file)
        
        # Load using native sqlite execute_many for max speed and zero variable limit issues
        with sqlite3.connect(db_path) as conn:
            columns = list(df.columns)
            placeholders = ",".join(["?"] * len(columns))
            sql = f"INSERT INTO {table_name} ({','.join(columns)}) VALUES ({placeholders})"
            # Convert to list of tuples
            records = df.itertuples(index=False, name=None)
            cursor = conn.cursor()
            cursor.executemany(sql, records)
            conn.commit()

        logger.info(f"[PASS] {table_name} successfully populated with {len(df)} records.")
    # 3. Compile Analytical Views
    views_path = config["database"]["views_ddl_path"]
    if os.path.exists(views_path):
        logger.info(f"Compiling analytical views from {views_path}...")
        with open(views_path, "r", encoding="utf-8") as f:
            views_script = f.read()
        with sqlite3.connect(db_path) as conn:
            conn.cursor().executescript(views_script)
            conn.commit()
        logger.info("[PASS] Analytical views compiled successfully.")

    # 4. Quick row count audit
    logger.info("Verifying database load counts:")
    with engine.connect() as conn:
        for table_name, _ in load_sequence:
            res = conn.execute(text(f"SELECT COUNT(*) FROM {table_name}")).scalar()
            logger.info(f"  - {table_name}: {res:,} rows")
    logger.info("Database build and ingestion completed.")


if __name__ == "__main__":
    build_database()
