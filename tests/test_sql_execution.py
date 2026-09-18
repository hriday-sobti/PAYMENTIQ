"""
PAYMENTIQ Integration Tests for PostgreSQL & DuckDB Query Execution
Validates that all analytical views and advanced queries execute without errors and return populated datasets.
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

def test_analytical_views_row_counts(pg_connection):
    """Verifies that all 5 analytical views return non-empty datasets from PostgreSQL."""
    views = [
        "analytics.v_payment_performance_by_method",
        "analytics.v_payment_performance_by_category",
        "analytics.v_revenue_leakage_waterfall",
        "analytics.v_customer_rfm_scores",
        "analytics.v_merchant_opportunity_matrix",
        "analytics.v_operational_support_metrics"
    ]
    for view in views:
        count = pg_connection.execute(text(f"SELECT COUNT(*) FROM {view};")).scalar()
        assert count > 0, f"Analytical view {view} returned 0 rows!"

def test_advanced_queries_execution(pg_connection):
    """Verifies that all advanced SQL query scripts execute and produce non-empty results."""
    query_files = sorted(list(Path("sql/advanced_queries").glob("*.sql")))
    assert len(query_files) >= 3, "Missing expected advanced SQL query files"

    for qf in query_files:
        sql_content = qf.read_text(encoding="utf-8")
        cleaned_sql = sql_content.strip().rstrip(";")
        result = pg_connection.execute(text(f"SELECT * FROM ({cleaned_sql}) AS q_sub LIMIT 10;")).fetchall()
        assert len(result) > 0, f"Query {qf.name} returned 0 rows!"
