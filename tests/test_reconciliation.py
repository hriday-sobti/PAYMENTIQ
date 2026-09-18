"""
PAYMENTIQ Automated Multi-Layer and Dimensional Reconciliation Tests
Asserts 0.00% variance across all 5 architectural storage layers and reconciles
dimensional breakdowns between PostgreSQL and DuckDB.
"""
import pytest
from sqlalchemy import text
from python.utils.db import db_manager
from python.pipeline.reconciliation import DataReconciliationAuditor

@pytest.fixture(scope="module")
def reconciliation_data():
    """Runs the 5-layer reconciliation audit and returns extracted layer metrics."""
    auditor = DataReconciliationAuditor()
    return auditor.audit_all_layers()

def test_overall_audit_status(reconciliation_data):
    """Rule: Overall multi-layer reconciliation audit status must strictly be PASS."""
    assert reconciliation_data["status"] == "PASS"

# --- Parameterized Core Metric Reconciliation Across All 5 Layers ---

CORE_METRICS = [
    ("row_count", 0),
    ("gtv", 0.05),
    ("settled_gtv", 0.05),
    ("net_revenue", 0.05),
    ("approved_count", 0),
    ("chargeback_count", 0)
]

@pytest.mark.parametrize("metric,tolerance", CORE_METRICS)
def test_metric_reconciliation_across_layers(reconciliation_data, metric, tolerance):
    """Rule: Every core financial and volume metric must match across all 5 layers within tolerance."""
    layers = reconciliation_data["layers"]
    base_val = layers["Layer_1_Raw_Parquet"][metric]

    for layer_name in ["Layer_2_Clean_Parquet", "Layer_3_PostgreSQL_DW", "Layer_4_DuckDB_Analytics", "Layer_5_PowerBI_Model"]:
        layer_val = layers[layer_name][metric]
        diff = abs(layer_val - base_val)
        assert diff <= tolerance, (
            f"Drift detected in metric '{metric}' on {layer_name}! "
            f"Base Raw: {base_val}, Layer Val: {layer_val}, Diff: {diff}"
        )

# --- Dimensional Reconciliation: Category GTV (PostgreSQL vs. DuckDB) ---

CATEGORIES = [
    "Grocery & Supermarkets",
    "Restaurants & Dining",
    "Department Stores & Retail",
    "Consumer Electronics",
    "Hotels & Travel",
    "Airlines & Transit",
    "Digital Goods & Gaming",
    "Apparel & Fashion"
]

@pytest.mark.parametrize("category", CATEGORIES)
def test_category_reconciliation_pg_vs_duckdb(category):
    """Rule: Category GTV must reconcile identically between PostgreSQL and DuckDB."""
    pg_engine = db_manager.get_pg_engine()
    ddb = db_manager.get_duckdb()

    sql = f"""
        SELECT ROUND(SUM(t.amount)::numeric, 2)
        FROM core.fact_transactions t
        JOIN core.dim_merchants m ON t.merchant_key = m.merchant_key
        WHERE m.merchant_category = '{category}';
    """
    with pg_engine.connect() as conn:
        pg_val = float(conn.execute(text(sql)).scalar())

    duck_val = float(ddb.execute(sql).fetchone()[0])
    assert abs(pg_val - duck_val) < 0.05, f"Category '{category}' GTV mismatch: PG={pg_val}, DuckDB={duck_val}"

# --- Dimensional Reconciliation: Payment Method Volume (PostgreSQL vs. DuckDB) ---

METHODS = [
    "Credit Card",
    "Debit Card",
    "Digital Wallet",
    "BNPL",
    "Instant Bank Transfer"
]

@pytest.mark.parametrize("method", METHODS)
def test_payment_method_reconciliation_pg_vs_duckdb(method):
    """Rule: Settled GTV per payment method must reconcile identically between PostgreSQL and DuckDB."""
    pg_engine = db_manager.get_pg_engine()
    ddb = db_manager.get_duckdb()

    sql = f"""
        SELECT ROUND(SUM(CASE WHEN t.auth_status = 'Approved' THEN t.amount ELSE 0 END)::numeric, 2)
        FROM core.fact_transactions t
        JOIN core.dim_payment_methods pm ON t.payment_method_key = pm.payment_method_key
        WHERE pm.method_name = '{method}';
    """
    with pg_engine.connect() as conn:
        pg_val = float(conn.execute(text(sql)).scalar())

    duck_val = float(ddb.execute(sql).fetchone()[0])
    assert abs(pg_val - duck_val) < 0.05, f"Method '{method}' Settled GTV mismatch: PG={pg_val}, DuckDB={duck_val}"

# --- Dimensional Reconciliation: Regional Country Volume (PostgreSQL vs. DuckDB) ---

COUNTRIES = ["US", "GB", "DE", "FR", "CA", "AU"]

@pytest.mark.parametrize("country", COUNTRIES)
def test_country_volume_reconciliation_pg_vs_duckdb(country):
    """Rule: Total transaction attempts per country must match identically between PostgreSQL and DuckDB."""
    pg_engine = db_manager.get_pg_engine()
    ddb = db_manager.get_duckdb()

    sql = f"""
        SELECT COUNT(*)
        FROM core.fact_transactions t
        JOIN core.dim_merchants m ON t.merchant_key = m.merchant_key
        WHERE m.merchant_country = '{country}';
    """
    with pg_engine.connect() as conn:
        pg_count = int(conn.execute(text(sql)).scalar())

    duck_count = int(ddb.execute(sql).fetchone()[0])
    assert pg_count == duck_count, f"Country '{country}' count mismatch: PG={pg_count}, DuckDB={duck_count}"
