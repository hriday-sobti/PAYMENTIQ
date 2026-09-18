"""
PAYMENTIQ Power BI Data Export Utility
Exports dimension tables, operational facts, and analytical models into optimized CSV/Parquet files
for direct consumption by Power BI Desktop and Power BI Service.
"""
import time
import pandas as pd
from pathlib import Path
from python.utils.db import db_manager
from python.utils.logger import setup_logger

logger = setup_logger("pbi_exporter")

def export_powerbi_data(output_dir: str = "powerbi/export_data"):
    """Extracts tables and analytical views from DuckDB into clean CSVs."""
    start_time = time.time()
    logger.info("======================================================================")
    logger.info("Exporting Data Warehouse Tables for Power BI Desktop")
    logger.info("======================================================================")

    out = Path(output_dir)
    out.mkdir(parents=True, exist_ok=True)
    ddb = db_manager.get_duckdb()

    # 1. Dimensions
    dimensions = [
        ("dim_customers", "SELECT * FROM core.dim_customers"),
        ("dim_merchants", "SELECT * FROM core.dim_merchants"),
        ("dim_payment_methods", "SELECT * FROM core.dim_payment_methods"),
        ("dim_dates", "SELECT * FROM core.dim_dates"),
        ("dim_decline_codes", "SELECT * FROM core.dim_decline_codes")
    ]

    for name, query in dimensions:
        df = ddb.execute(query).df()
        csv_path = out / f"{name}.csv"
        df.to_csv(csv_path, index=False)
        logger.info("Exported dimension %s: %d rows to %s", name, len(df), csv_path)

    # 2. Operational Facts
    facts = [
        ("fact_disputes", "SELECT * FROM core.fact_disputes"),
        ("fact_support_cases", "SELECT * FROM core.fact_support_cases"),
        ("v_customer_rfm_scores", "SELECT * FROM analytics.v_customer_rfm_scores"),
        ("v_merchant_opportunity_matrix", "SELECT * FROM analytics.v_merchant_opportunity_matrix")
    ]

    for name, query in facts:
        df = ddb.execute(query).df()
        csv_path = out / f"{name}.csv"
        df.to_csv(csv_path, index=False)
        logger.info("Exported operational model %s: %d rows to %s", name, len(df), csv_path)

    # 3. High-Performance Aggregated Fact Transactions (by date, merchant, rail, channel, status)
    logger.info("Exporting high-performance aggregated fact_transactions for Power BI...")
    agg_query = """
        SELECT 
            date_key,
            merchant_key,
            payment_method_key,
            channel,
            device_type,
            is_3ds_authenticated,
            auth_status,
            decline_code,
            COUNT(*) AS transaction_count,
            SUM(amount) AS total_amount,
            SUM(processing_fee) AS total_processing_fee,
            SUM(interchange_fee) AS total_interchange_fee,
            SUM(scheme_fee) AS total_scheme_fee,
            SUM(net_revenue) AS total_net_revenue,
            SUM(net_contribution) AS total_net_contribution,
            AVG(latency_ms) AS avg_latency_ms,
            SUM(CASE WHEN refund_flag THEN 1 ELSE 0 END) AS refund_count,
            SUM(CASE WHEN chargeback_flag THEN 1 ELSE 0 END) AS chargeback_count,
            SUM(CASE WHEN fraud_flag THEN 1 ELSE 0 END) AS fraud_count,
            SUM(CASE WHEN is_soft_decline THEN amount ELSE 0 END) AS soft_decline_amount
        FROM core.fact_transactions
        GROUP BY 
            date_key, merchant_key, payment_method_key, channel,
            device_type, is_3ds_authenticated, auth_status, decline_code;
    """
    agg_df = ddb.execute(agg_query).df()
    agg_csv = out / "fact_transactions_aggregated.csv"
    agg_df.to_csv(agg_csv, index=False)
    logger.info("Exported aggregated fact transactions (%d rows) to %s", len(agg_df), agg_csv)

    elapsed = time.time() - start_time
    logger.info("======================================================================")
    logger.info("Power BI Data Export Completed in %.2f seconds", elapsed)
    logger.info("======================================================================")

if __name__ == "__main__":
    export_powerbi_data()
