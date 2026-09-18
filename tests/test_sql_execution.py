"""
PAYMENTIQ Integration Tests for PostgreSQL & DuckDB Query Execution
Validates that all analytical SQL views and advanced query scripts execute and produce non-empty datasets.
"""
import pytest
from pathlib import Path
from sqlalchemy import text
from python.utils.db import db_manager

@pytest.fixture(scope="module")
def pg_connection():
    """Provides an active PostgreSQL connection for query testing."""
    engine = db_manager.get_pg_engine()
    with engine.connect() as conn:
        yield conn

@pytest.fixture(scope="module")
def duckdb_connection():
    """Provides an active DuckDB connection for query testing."""
    return db_manager.get_duckdb()

ANALYTICAL_VIEWS = [
    "analytics.v_payment_performance_by_method",
    "analytics.v_payment_performance_by_category",
    "analytics.v_daily_payment_trends",
    "analytics.v_revenue_leakage_waterfall",
    "analytics.v_decline_code_leakage",
    "analytics.v_merchant_leakage_ranking",
    "analytics.v_customer_rfm_scores",
    "analytics.v_rfm_segment_summary",
    "analytics.v_merchant_opportunity_matrix",
    "analytics.v_operational_support_metrics",
    "analytics.v_technical_latency_summary"
]

@pytest.mark.parametrize("view_name", ANALYTICAL_VIEWS)
def test_postgresql_view_execution(pg_connection, view_name):
    """Rule: Every analytical view in PostgreSQL must be queryable and return non-empty records."""
    count = pg_connection.execute(text(f"SELECT COUNT(*) FROM {view_name};")).scalar()
    assert count > 0, f"PostgreSQL view {view_name} returned 0 rows!"

@pytest.mark.parametrize("view_name", ANALYTICAL_VIEWS)
def test_duckdb_view_execution(duckdb_connection, view_name):
    """Rule: Every analytical view in DuckDB must be queryable and return non-empty records."""
    res = duckdb_connection.execute(f"SELECT COUNT(*) FROM {view_name};").fetchone()
    assert res[0] > 0, f"DuckDB view {view_name} returned 0 rows!"

ADVANCED_QUERIES = [
    "cohort_retention_matrix.sql",
    "rolling_payment_velocity.sql",
    "dimensional_pareto.sql"
]

@pytest.mark.parametrize("query_filename", ADVANCED_QUERIES)
def test_postgresql_advanced_query_execution(pg_connection, query_filename):
    """Rule: Every advanced SQL analytical query must execute cleanly and return records in PostgreSQL."""
    q_path = Path("sql/advanced_queries") / query_filename
    assert q_path.exists(), f"Missing advanced query file: {query_filename}"
    sql_text = q_path.read_text(encoding="utf-8").strip().rstrip(";")
    result = pg_connection.execute(text(f"SELECT * FROM ({sql_text}) AS q_sub LIMIT 10;")).fetchall()
    assert len(result) > 0, f"Query {query_filename} returned 0 rows in PostgreSQL!"

@pytest.mark.parametrize("query_filename", ADVANCED_QUERIES)
def test_duckdb_advanced_query_execution(duckdb_connection, query_filename):
    """Rule: Every advanced SQL analytical query must execute cleanly in DuckDB."""
    q_path = Path("sql/advanced_queries") / query_filename
    sql_text = q_path.read_text(encoding="utf-8").strip().rstrip(";")
    result = duckdb_connection.execute(f"SELECT * FROM ({sql_text}) AS q_sub LIMIT 10;").fetchall()
    assert len(result) > 0, f"Query {query_filename} returned 0 rows in DuckDB!"
