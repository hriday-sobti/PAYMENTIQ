"""
PAYMENTIQ Unit Tests for Schema Conformity, Key Constraints & Referential Integrity
Validates primary keys, foreign keys, column structures, and domain boundaries across all entities.
"""
import pytest
import pandas as pd
from pathlib import Path

@pytest.fixture(scope="module")
def dimensions():
    """Loads all reference dimension datasets."""
    ref_dir = Path("data/reference")
    return {
        "dim_customers": pd.read_parquet(ref_dir / "dim_customers.parquet"),
        "dim_merchants": pd.read_parquet(ref_dir / "dim_merchants.parquet"),
        "dim_payment_methods": pd.read_parquet(ref_dir / "dim_payment_methods.parquet"),
        "dim_dates": pd.read_parquet(ref_dir / "dim_dates.parquet"),
        "dim_decline_codes": pd.read_parquet(ref_dir / "dim_decline_codes.parquet")
    }

@pytest.fixture(scope="module")
def transactions():
    """Loads first partition of cleaned transactions."""
    files = sorted(list(Path("data/processed").glob("clean_transactions_part_*.parquet")))
    assert len(files) > 0, "No processed partitions found"
    return pd.read_parquet(files[0])

@pytest.fixture(scope="module")
def operational_facts():
    """Loads disputes and support cases."""
    proc_dir = Path("data/processed")
    return {
        "fact_disputes": pd.read_parquet(proc_dir / "clean_disputes.parquet"),
        "fact_support_cases": pd.read_parquet(proc_dir / "clean_support_cases.parquet")
    }

# --- Foreign Key Integrity Tests ---

def test_customer_foreign_keys(transactions, dimensions):
    """Verifies that all customer_keys in transactions exist in dim_customers."""
    valid_keys = set(dimensions["dim_customers"]["customer_key"])
    assert transactions["customer_key"].isin(valid_keys).all()

def test_merchant_foreign_keys(transactions, dimensions):
    """Verifies that all merchant_keys in transactions exist in dim_merchants."""
    valid_keys = set(dimensions["dim_merchants"]["merchant_key"])
    assert transactions["merchant_key"].isin(valid_keys).all()

def test_payment_method_foreign_keys(transactions, dimensions):
    """Verifies that all payment_method_keys exist in dim_payment_methods."""
    valid_keys = set(dimensions["dim_payment_methods"]["payment_method_key"])
    assert transactions["payment_method_key"].isin(valid_keys).all()

def test_date_foreign_keys(transactions, dimensions):
    """Verifies that all date_keys exist in dim_dates."""
    valid_keys = set(dimensions["dim_dates"]["date_key"])
    assert transactions["date_key"].isin(valid_keys).all()

def test_disputes_merchant_foreign_keys(operational_facts, dimensions):
    """Verifies that dispute merchant_keys exist in dim_merchants."""
    valid_merchs = set(dimensions["dim_merchants"]["merchant_key"])
    assert operational_facts["fact_disputes"]["merchant_key"].isin(valid_merchs).all()

def test_support_cases_customer_foreign_keys(operational_facts, dimensions):
    """Verifies that support cases customer_keys exist in dim_customers."""
    valid_custs = set(dimensions["dim_customers"]["customer_key"])
    assert operational_facts["fact_support_cases"]["customer_key"].isin(valid_custs).all()

# --- Primary Key Uniqueness Tests ---

PRIMARY_KEY_TABLES = [
    ("dim_customers", "customer_key"),
    ("dim_merchants", "merchant_key"),
    ("dim_payment_methods", "payment_method_key"),
    ("dim_dates", "date_key"),
    ("dim_decline_codes", "decline_code")
]

@pytest.mark.parametrize("table_name,pk_col", PRIMARY_KEY_TABLES)
def test_dimension_pk_uniqueness(dimensions, table_name, pk_col):
    """Rule: Every dimension table must have strictly unique primary keys."""
    df = dimensions[table_name]
    assert df[pk_col].nunique() == len(df), f"Duplicate primary keys detected in {table_name}!"

def test_transaction_id_uniqueness(transactions):
    """Rule: Fact transactions partition must have strictly unique transaction_ids."""
    assert transactions["transaction_id"].nunique() == len(transactions)

def test_disputes_id_uniqueness(operational_facts):
    """Rule: Disputes must have strictly unique dispute_ids."""
    df = operational_facts["fact_disputes"]
    assert df["dispute_id"].nunique() == len(df)

def test_support_cases_id_uniqueness(operational_facts):
    """Rule: Support cases must have strictly unique case_ids."""
    df = operational_facts["fact_support_cases"]
    assert df["case_id"].nunique() == len(df)

# --- Timestamp & Temporal Boundary Tests ---

def test_transaction_timestamp_range(transactions):
    """Rule: Transaction timestamps must be strictly within operating year 2024."""
    min_ts = pd.to_datetime(transactions["timestamp"].min())
    max_ts = pd.to_datetime(transactions["timestamp"].max())
    assert min_ts >= pd.Timestamp("2024-01-01 00:00:00")
    assert max_ts <= pd.Timestamp("2024-12-31 23:59:59")

def test_dispute_timestamp_lags(operational_facts):
    """Rule: Dispute timestamps must fall within 2024 or 2025."""
    min_ts = pd.to_datetime(operational_facts["fact_disputes"]["dispute_timestamp"].min())
    max_ts = pd.to_datetime(operational_facts["fact_disputes"]["dispute_timestamp"].max())
    assert min_ts >= pd.Timestamp("2024-01-01 00:00:00")
    assert max_ts <= pd.Timestamp("2025-06-30 23:59:59")

# --- Domain & Geographic Codes ---

VALID_COUNTRIES = ["US", "GB", "DE", "FR", "CA", "AU"]

@pytest.mark.parametrize("country", VALID_COUNTRIES)
def test_customer_country_membership(dimensions, country):
    """Rule: Customer countries must map to active ISO country codes."""
    cust_countries = set(dimensions["dim_customers"]["customer_country"].unique())
    assert country in cust_countries

@pytest.mark.parametrize("country", VALID_COUNTRIES)
def test_merchant_country_membership(dimensions, country):
    """Rule: Merchant countries must map to active ISO country codes."""
    merch_countries = set(dimensions["dim_merchants"]["merchant_country"].unique())
    assert country in merch_countries
