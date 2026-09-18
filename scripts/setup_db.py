"""
PAYMENTIQ Database Health & Setup Utility
Checks local PostgreSQL server status, starts instance if stopped, runs migrations,
bulk loads available datasets, and deploys analytical views.
"""
import os
import sys
import subprocess
import time
from pathlib import Path

# Add project root to sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from python.utils.db import db_manager
from python.utils.logger import setup_logger
from python.pipeline.schema_migrator import run_migrations
from python.pipeline.loader import BulkDataLoader
from python.pipeline.apply_views import deploy_views

logger = setup_logger("setup_db")

def ensure_database():
    pg_bin = r"C:\Users\hrida\.local\pgsql\bin"
    pg_data = r"C:\Users\hrida\.local\pgdata"
    pg_ctl = os.path.join(pg_bin, "pg_ctl.exe")

    print("\n" + "="*70)
    print(" PAYMENTIQ Database Setup & Health Inspector")
    print("="*70 + "\n")

    if os.path.exists(pg_ctl) and os.path.exists(pg_data):
        status = subprocess.run([pg_ctl, "-D", pg_data, "status"], capture_output=True, text=True)
        if "is running" not in status.stdout:
            print("[INFO] Starting PostgreSQL server on port 5433...")
            log_file = os.path.join(pg_data, "server.log")
            subprocess.run([pg_ctl, "-D", pg_data, "-l", log_file, "-o", "-p 5433", "start"], check=True)
            time.sleep(2)
        else:
            print("[OK] PostgreSQL server is already active on port 5433.")

    # Test connections
    conn_results = db_manager.test_connections()
    print(f"[STATUS] PostgreSQL Connected: {conn_results['postgresql']}")
    print(f"[STATUS] DuckDB Connected:     {conn_results['duckdb']}")

    if conn_results['postgresql']:
        print("\nApplying database schema migrations...")
        run_migrations()

        # Check if processed files exist to load
        proc_files = list(Path("data/processed").glob("clean_transactions_part_*.parquet"))
        if proc_files:
            print(f"\nLoading {len(proc_files)} processed partitions into PostgreSQL & DuckDB...")
            loader = BulkDataLoader()
            loader.run_full_load()

            print("\nDeploying analytical views...")
            deploy_views()

        print("\n[SUCCESS] Database is fully operational, populated, and views are verified!")
    else:
        print("\n[ERROR] Could not connect to PostgreSQL. Check server logs.")

    print("="*70 + "\n")

if __name__ == "__main__":
    ensure_database()
