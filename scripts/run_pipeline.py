"""Master End-to-End Orchestrator Pipeline.

Executes the entire platform sequentially:
1. Synthetic Data Generation & Dimensions
2. Pre-flight Data Validation & Rejection Audits
3. Data Cleaning & Feature Engineering
4. Relational Database Schema Execution & Ingestion
5. SQL Analytical Views Compilation & Quality Assertions
6. Statistical EDA Analysis
7. Analytical Decision Layers (Risk, Reorder, Promo, Forecast, Opportunity)
8. Excel Commercial Scenario Model Generation
9. Test Suite Execution & Pipeline Verification
"""

import os
import sys
import subprocess
import time

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.utils.config_utils import load_config, setup_logger


def run_pipeline():
    logger = setup_logger("run_pipeline")
    start_time = time.time()
    logger.info("====================================================================")
    logger.info("STARTING AUTOMOTIVE AFTERMARKET INTELLIGENCE MASTER PIPELINE")
    steps = [
        ("Step 1: Data Generation & Pre-flight Validation", "scripts/generate_data.py"),
        ("Step 2: Database Build & Table Ingestion", "scripts/build_database.py"),
        ("Step 3: Exploratory Data Analysis (EDA)", "src/analytics/eda_engine.py"),
        ("Step 4: Analytical Decision Layer Exports", "scripts/export_analytics.py"),
        ("Step 5: Excel Scenario Model Generation", "src/analytics/excel_scenario_generator.py"),
        ("Step 6: Pre-rendered Notebooks & Visuals Generation", "scripts/build_notebooks.py"),
    ]

    for label, script in steps:
        logger.info(f"\n--- Running {label} ({script}) ---")
        cmd = [sys.executable, script]
        res = subprocess.run(cmd, capture_output=True, text=True)
        if res.returncode != 0:
            logger.error(f"Pipeline failed at {label}!\nError:\n{res.stderr}")
            sys.exit(1)
        else:
            if res.stdout.strip():
                for line in res.stdout.strip().split("\n"):
                    logger.info(f"  {line}")

    # Run automated test suite
    logger.info("\n--- Running Step 6: Automated Test Verification (pytest) ---")
    test_res = subprocess.run([sys.executable, "-m", "pytest", "tests/"], capture_output=True, text=True)
    if test_res.returncode != 0:
        logger.error(f"Tests failed!\n{test_res.stderr}")
        sys.exit(1)
    else:
        logger.info(f"  [PASS] All unit tests completed successfully.")

    elapsed = round(time.time() - start_time, 1)
    logger.info("====================================================================")
    logger.info(f"MASTER PIPELINE COMPLETED SUCCESSFULLY IN {elapsed}s")
    logger.info("====================================================================")


if __name__ == "__main__":
    run_pipeline()
