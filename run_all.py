"""
PAYMENTIQ Master End-to-End Execution Orchestrator
Executes the full pipeline from database migrations, synthetic generation, validation,
warehouse loading, analytical modeling, Power BI export, reconciliation, report generation, and tests.
"""
import sys
import time
import subprocess
from python.utils.logger import setup_logger

logger = setup_logger("master_orchestrator")

STEPS = [
    ("Database Schema Migrations", ["python", "-m", "python.pipeline.schema_migrator"]),
    ("Data Quality & Integrity Validation", ["python", "-m", "python.pipeline.validation"]),
    ("Data Cleaning & Feature Engineering", ["python", "-m", "python.pipeline.cleaning"]),
    ("Warehouse Bulk Data Loading", ["python", "-m", "python.pipeline.loader"]),
    ("Analytical SQL Views Deployment", ["python", "-m", "python.pipeline.apply_views"]),
    ("Exploratory Data Analysis (EDA)", ["python", "-m", "python.analytics.eda"]),
    ("Unified KPI Engine Calculation", ["python", "-m", "python.analytics.kpi_engine"]),
    ("Payment Performance Intelligence", ["python", "-m", "python.analytics.payment_performance"]),
    ("Revenue Leakage & TVaR Analytics", ["python", "-m", "python.analytics.revenue_leakage"]),
    ("Customer RFM & Cohort Intelligence", ["python", "-m", "python.analytics.customer_intelligence"]),
    ("Merchant Opportunity Matrix Analysis", ["python", "-m", "python.analytics.merchant_analytics"]),
    ("Unsupervised Anomaly Detection", ["python", "-m", "python.analytics.anomaly_detection"]),
    ("Operational Incident Root-Cause Analysis", ["python", "-m", "python.analytics.root_cause"]),
    ("Time-Series Forecasting Engine", ["python", "-m", "python.analytics.forecasting"]),
    ("Inferential Statistical Hypothesis Testing", ["python", "-m", "python.analytics.statistical_analysis"]),
    ("Power BI Dataset Exporter", ["python", "-m", "powerbi.export_data_for_powerbi"]),
    ("Cross-Platform Data Reconciliation Audit", ["python", "-m", "python.pipeline.reconciliation"]),
    ("6-Page Executive Analytics Review PDF", ["python", "-m", "reports.generate_executive_report"]),
    ("Comprehensive Automated Test Suite", ["python", "-m", "pytest", "tests/"])
]

def run_pipeline():
    start_total = time.time()
    print("\n" + "="*75)
    print(" PAYMENTIQ | End-to-End Payment Analytics Platform Execution")
    print("="*75 + "\n")

    for i, (name, cmd) in enumerate(STEPS, 1):
        step_start = time.time()
        print(f"[{i:02d}/{len(STEPS):02d}] Executing: {name}...")
        res = subprocess.run(cmd, capture_output=True, text=True)
        step_elapsed = time.time() - step_start

        if res.returncode != 0:
            print(f"\n[ERROR] Step {name} failed with code {res.returncode}!")
            print("STDOUT:\n", res.stdout)
            print("STDERR:\n", res.stderr)
            sys.exit(1)
        else:
            print(f"       -> PASSED in {step_elapsed:.2f} seconds.")

    total_elapsed = time.time() - start_total
    print("\n" + "="*75)
    print(f" ALL {len(STEPS)} PIPELINE STAGES COMPLETED SUCCESSFULLY IN {total_elapsed:.2f} SECONDS!")
    print("="*75)
    print(" Output Deliverables:")
    print("  - PostgreSQL Star Schema:   'paymentiq_dw' (Tables, Views, Indexes populated)")
    print("  - DuckDB Analytical DB:     'data/processed/paymentiq.duckdb'")
    print("  - Executive PDF Report:     'reports/PAYMENTIQ_Executive_Review.pdf'")
    print("  - Power BI Project Suite:   'powerbi/PAYMENTIQ.pbip'")
    print("  - Audit Reports:            'reports/' and 'documentation/'")
    print("  - Interactive AI Assistant: 'python -m ai.assistant_cli'")
    print("="*75 + "\n")

if __name__ == "__main__":
    run_pipeline()
