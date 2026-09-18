"""
PAYMENTIQ High-Performance Bulk Data Loader
Loads reference dimensions and multi-million transaction event streams into PostgreSQL
and DuckDB using high-throughput binary COPY and stream buffers.
"""
import io
import time
import psycopg
import pandas as pd
import numpy as np
from pathlib import Path
from typing import Dict, Any, List

from python.utils.db import db_manager
from python.utils.logger import setup_logger

logger = setup_logger("bulk_loader")

class BulkDataLoader:
    """High-speed dimensional and transactional data warehouse bulk loader."""

    def __init__(self, ref_dir: str = "data/reference", processed_dir: str = "data/processed"):
        self.ref_dir = Path(ref_dir)
        self.processed_dir = Path(processed_dir)

    def _copy_df_to_postgres(self, df: pd.DataFrame, table_name: str, conn: psycopg.Connection):
        """Loads a DataFrame into PostgreSQL using in-memory CSV stream and native COPY."""
        buffer = io.StringIO()
        df.to_csv(buffer, index=False, header=False, na_rep="\\N")
        buffer.seek(0)

        cols = [f'"{c}"' for c in df.columns]
        copy_sql = f"COPY {table_name} ({', '.join(cols)}) FROM STDIN WITH (FORMAT CSV, NULL '\\N')"

        with conn.cursor() as cur:
            with cur.copy(copy_sql) as copy:
                copy.write(buffer.getvalue())

    def load_dimensions(self, pg_conn: psycopg.Connection, ddb: Any):
        """Loads all reference dimension tables into PostgreSQL and DuckDB."""
        logger.info("--- Step 1: Loading Reference Dimensions ---")
        dim_files = [
            ("dim_customers", "core.dim_customers"),
            ("dim_merchants", "core.dim_merchants"),
            ("dim_payment_methods", "core.dim_payment_methods"),
            ("dim_dates", "core.dim_dates"),
            ("dim_decline_codes", "core.dim_decline_codes")
        ]

        for file_prefix, table_name in dim_files:
            p_file = self.ref_dir / f"{file_prefix}.parquet"
            if not p_file.exists():
                raise FileNotFoundError(f"Missing dimension file: {p_file}")

            df = pd.read_parquet(p_file)
            logger.info("Loading %s (%d rows)...", table_name, len(df))

            # PostgreSQL load
            with pg_conn.cursor() as cur:
                cur.execute(f"TRUNCATE TABLE {table_name} CASCADE;")
            self._copy_df_to_postgres(df, table_name, pg_conn)
            pg_conn.commit()

            # DuckDB load
            ddb.execute(f"CREATE OR REPLACE TABLE {table_name} AS SELECT * FROM df;")
            logger.info("Successfully loaded %s into PostgreSQL & DuckDB", table_name)

    def load_transactions(self, pg_conn: psycopg.Connection, ddb: Any):
        """Loads cleaned transaction partitions into core.fact_transactions."""
        logger.info("--- Step 2: Bulk Loading Transaction Partitions ---")
        tx_files = sorted(list(self.processed_dir.glob("clean_transactions_part_*.parquet")))
        if not tx_files:
            raise FileNotFoundError(f"No processed transaction partitions found in {self.processed_dir}")

        with pg_conn.cursor() as cur:
            cur.execute("TRUNCATE TABLE core.fact_transactions CASCADE;")
        pg_conn.commit()

        # Specific columns matching core.fact_transactions DDL
        fact_cols = [
            "transaction_id", "customer_key", "merchant_key", "date_key",
            "payment_method_key", "decline_code", "timestamp", "amount",
            "currency", "device_type", "channel", "is_3ds_authenticated",
            "auth_status", "decline_reason", "processing_fee", "interchange_fee",
            "scheme_fee", "net_revenue", "net_contribution", "latency_ms",
            "retry_attempt", "refund_flag", "chargeback_flag", "fraud_flag",
            "risk_score", "is_high_value", "is_cross_border", "is_soft_decline",
            "addressable_leakage_amount"
        ]

        total_tx_loaded = 0
        start_tx_time = time.time()

        for i, f in enumerate(tx_files):
            logger.info("Bulk copying partition %d/%d: %s...", i + 1, len(tx_files), f.name)
            df = pd.read_parquet(f)
            df_subset = df[fact_cols]

            # PostgreSQL copy
            self._copy_df_to_postgres(df_subset, "core.fact_transactions", pg_conn)
            pg_conn.commit()
            total_tx_loaded += len(df_subset)

        tx_elapsed = time.time() - start_tx_time
        logger.info(
            "PostgreSQL Fact Transactions Load Complete: %d rows loaded in %.2f seconds (%.0f rows/sec)",
            total_tx_loaded, tx_elapsed, total_tx_loaded / max(tx_elapsed, 0.01)
        )

        # DuckDB load all partitions via Parquet scan
        logger.info("Loading transactions into DuckDB core.fact_transactions...")
        parquet_pattern = str(self.processed_dir / "clean_transactions_part_*.parquet").replace("\\", "/")
        ddb.execute(f"CREATE OR REPLACE TABLE core.fact_transactions AS SELECT * FROM read_parquet('{parquet_pattern}');")
        duck_count = ddb.execute("SELECT COUNT(*) FROM core.fact_transactions;").fetchone()[0]
        logger.info("DuckDB Fact Transactions Load Complete: %d rows", duck_count)

    def load_operational_facts(self, pg_conn: psycopg.Connection, ddb: Any):
        """Loads disputes and support cases into PostgreSQL and DuckDB."""
        logger.info("--- Step 3: Loading Disputes and Support Cases ---")

        # 1. Disputes
        dsp_file = self.processed_dir / "clean_disputes.parquet"
        if dsp_file.exists():
            dsp_df = pd.read_parquet(dsp_file)
            with pg_conn.cursor() as cur:
                cur.execute("TRUNCATE TABLE core.fact_disputes CASCADE;")
            self._copy_df_to_postgres(dsp_df, "core.fact_disputes", pg_conn)
            pg_conn.commit()
            ddb.execute("CREATE OR REPLACE TABLE core.fact_disputes AS SELECT * FROM dsp_df;")
            logger.info("Loaded %d dispute records into PostgreSQL & DuckDB", len(dsp_df))

        # 2. Support Cases
        cases_file = self.processed_dir / "clean_support_cases.parquet"
        if cases_file.exists():
            cases_df = pd.read_parquet(cases_file)
            with pg_conn.cursor() as cur:
                cur.execute("TRUNCATE TABLE core.fact_support_cases CASCADE;")
            self._copy_df_to_postgres(cases_df, "core.fact_support_cases", pg_conn)
            pg_conn.commit()
            ddb.execute("CREATE OR REPLACE TABLE core.fact_support_cases AS SELECT * FROM cases_df;")
            logger.info("Loaded %d support case records into PostgreSQL & DuckDB", len(cases_df))

    def run_full_load(self):
        """Executes complete dimensional and fact bulk loading process."""
        start_time = time.time()
        logger.info("======================================================================")
        logger.info("Starting PAYMENTIQ Warehouse Bulk Loading Execution")
        logger.info("======================================================================")

        pg_url = db_manager.pg_url.replace("postgresql+psycopg://", "postgresql://")
        with psycopg.connect(pg_url) as pg_conn:
            ddb = db_manager.get_duckdb()

            self.load_dimensions(pg_conn, ddb)
            self.load_transactions(pg_conn, ddb)
            self.load_operational_facts(pg_conn, ddb)

        elapsed = time.time() - start_time
        logger.info("======================================================================")
        logger.info("Warehouse Bulk Loading Execution Completed in %.2f seconds", elapsed)
        logger.info("======================================================================")

if __name__ == "__main__":
    loader = BulkDataLoader()
    loader.run_full_load()
