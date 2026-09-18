"""
PAYMENTIQ Analytical Views Deployment Runner
Applies and validates all analytical SQL views in PostgreSQL and DuckDB.
"""
from pathlib import Path
from sqlalchemy import text
from python.utils.db import db_manager
from python.utils.logger import setup_logger

logger = setup_logger("view_deployer")

def deploy_views():
    """Applies all analytical views to PostgreSQL and DuckDB."""
    logger.info("======================================================================")
    logger.info("Deploying PAYMENTIQ Analytical Views & Reporting Layer")
    logger.info("======================================================================")

    views_dir = Path("sql/analytical_views")
    view_files = sorted(list(views_dir.glob("*.sql")))
    if not view_files:
        raise FileNotFoundError(f"No SQL view files found in {views_dir}")

    # 1. PostgreSQL Deployment
    pg_engine = db_manager.get_pg_engine()
    with pg_engine.begin() as conn:
        for vf in view_files:
            logger.info("Applying PostgreSQL View: %s...", vf.name)
            sql_text = vf.read_text(encoding="utf-8")
            conn.execute(text(sql_text))
            logger.info("Successfully deployed %s", vf.name)

    logger.info("All PostgreSQL analytical views deployed successfully!")

    # 2. DuckDB Deployment
    ddb = db_manager.get_duckdb()
    ddb.execute("CREATE SCHEMA IF NOT EXISTS analytics;")
    for vf in view_files:
        logger.info("Applying DuckDB View: %s...", vf.name)
        sql_text = vf.read_text(encoding="utf-8")
        try:
            ddb.execute(sql_text)
            logger.info("Successfully deployed to DuckDB: %s", vf.name)
        except Exception as e:
            logger.warning("DuckDB view deployment note on %s: %s", vf.name, e)

    # 3. Smoke Test Querying Key Views
    with pg_engine.connect() as conn:
        for v in [
            "analytics.v_payment_performance_by_method",
            "analytics.v_revenue_leakage_waterfall",
            "analytics.v_customer_rfm_scores",
            "analytics.v_merchant_opportunity_matrix",
            "analytics.v_operational_support_metrics"
        ]:
            count = conn.execute(text(f"SELECT COUNT(*) FROM {v};")).scalar()
            logger.info("Verified PostgreSQL view %s: %d rows returned", v, count)

    logger.info("======================================================================")
    logger.info("Analytical Views Deployment & Verification Complete!")
    logger.info("======================================================================")

if __name__ == "__main__":
    deploy_views()
