"""
PAYMENTIQ Schema Migration & DDL Execution Runner
Executes versioned SQL DDL scripts to build staging, core star schema, and indexes in PostgreSQL and DuckDB.
"""
from pathlib import Path
from sqlalchemy import text
from python.utils.db import db_manager
from python.utils.logger import setup_logger

logger = setup_logger("schema_migrator")

def run_migrations():
    """Executes all DDL scripts in sequence against PostgreSQL and initializes DuckDB."""
    logger.info("======================================================================")
    logger.info("Running PAYMENTIQ Database Schema Migrations")
    logger.info("======================================================================")

    ddl_dir = Path("sql/ddl")
    ddl_files = sorted(list(ddl_dir.glob("*.sql")))
    if not ddl_files:
        raise FileNotFoundError(f"No DDL files found in {ddl_dir}")

    # 1. PostgreSQL Schema Execution
    engine = db_manager.get_pg_engine()
    with engine.begin() as conn:
        for f in ddl_files:
            logger.info("Applying PostgreSQL DDL: %s...", f.name)
            sql_content = f.read_text(encoding="utf-8")
            # Execute statement blocks
            conn.execute(text(sql_content))
            logger.info("Successfully applied %s", f.name)

    logger.info("PostgreSQL schemas and tables created successfully!")

    # 2. DuckDB Schema Initialization (for local embedded analytical queries)
    ddb = db_manager.get_duckdb()
    logger.info("Initializing DuckDB schema structure...")
    ddb.execute("CREATE SCHEMA IF NOT EXISTS core;")
    ddb.execute("CREATE SCHEMA IF NOT EXISTS staging;")
    logger.info("DuckDB schemas initialized successfully!")

    logger.info("======================================================================")
    logger.info("All Database Schema Migrations Completed Successfully!")
    logger.info("======================================================================")

if __name__ == "__main__":
    run_migrations()
