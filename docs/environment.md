# Environment & Execution Setup

## Environment Summary
- **Operating System:** Windows 11 Home (x64)
- **Python Version:** 3.14.6
- **Architecture:** AMD64
- **Primary Data Science Stack Installed:**
  - `pandas` (Fast vectorized tabular operations)
  - `numpy` (Numerical and statistical routines)
  - `statsmodels` (Time series and forecasting analysis)
  - `openpyxl` (Native Excel spreadsheet scenario model generation)
  - `sqlalchemy` (Database abstraction layer)
  - `pyyaml` (Project configuration parsing)

## Database Architecture: Dual-Engine Design
1. **Primary Relational Engine:** SQLite (Native, zero external daemon dependency, ACID compliant, embedded).
2. **PostgreSQL Compatibility:** Full ANSI SQL DDL, dimensional modeling, CTEs, and window functions written in clean SQL compatible with standard PostgreSQL and SQLite (via SQLAlchemy).
3. **Staging & Analytical Layer:** Structured SQL scripts located in `sql/schema/`, `sql/staging/`, `sql/transformations/`, `sql/analytics/`, and `sql/quality_checks/`.

## Reproducibility Strategy
- Deterministic random seed (`RANDOM_SEED = 42`) set across NumPy, Python standard library `random`.
- Configuration centrally declared in `config/project_config.yaml`.
- Fully automated single-command execution pipeline `scripts/run_pipeline.py`.
