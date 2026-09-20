"""Pytest session fixtures for autonomous test suite execution."""

import os
import sys
import subprocess
import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))


@pytest.fixture(scope="session", autouse=True)
def ensure_database_and_data_present():
    """Ensure data files and database exist before running tests.

    If run on a fresh clone where raw/processed CSVs were gitignored,
    this automatically runs generation and database compilation once.
    """
    db_path = os.path.join("data", "processed", "aftermarket.db")
    sales_csv = os.path.join("data", "processed", "fact_sales.csv")

    if not os.path.exists(db_path) or not os.path.exists(sales_csv):
        print("\n[conftest] Data artifacts missing in clone. Running data generation and DB build...")
        subprocess.run([sys.executable, "scripts/generate_data.py"], check=True)
        subprocess.run([sys.executable, "scripts/build_database.py"], check=True)
        print("[conftest] Environment successfully initialized.")
