"""
PAYMENTIQ Unit Tests for Schema Conformity & Referential Integrity
"""
import pytest
import pandas as pd
from pathlib import Path

@pytest.fixture(scope="module")
def dimensions():
    """Loads all reference dimension datasets."""
    ref_dir = Path("data/reference")
    return {
        "customers": pd.read_parquet(ref_dir / "dim_customers.parquet"),
        "merchants": pd.read_parquet(ref_dir / "dim_merchants.parquet"),
        "payment_methods": pd.read_parquet(ref_dir / "dim_payment_methods.parquet"),
        "dates": pd.read_parquet(ref_dir / "dim_dates.parquet"),
        "decline_codes": pd.read_parquet(ref_dir / "dim_decline_codes.parquet")
    }

@pytest.fixture(scope="module")
def transactions():
    """Loads first partition of cleaned transactions."""
    files = sorted(list(Path("data/processed").glob("clean_transactions_part_*.parquet")))
    assert len(files) > 0, "No processed partitions found"
    return pd.read_parquet(files[0])

def test_customer_foreign_keys(transactions, dimensions):
    """Verifies that all customer_keys in transactions exist in dim_customers."""
    valid_keys = set(dimensions["customers"]["customer_key"])
    assert transactions["customer_key"].isin(valid_keys).all()

def test_merchant_foreign_keys(transactions, dimensions):
    """Verifies that all merchant_keys in transactions exist in dim_merchants."""
    valid_keys = set(dimensions["merchants"]["merchant_key"])
    assert transactions["merchant_key"].isin(valid_keys).all()

def test_payment_method_foreign_keys(transactions, dimensions):
    """Verifies that all payment_method_keys exist in dim_payment_methods."""
    valid_keys = set(dimensions["payment_methods"]["payment_method_key"])
    assert transactions["payment_method_key"].isin(valid_keys).all()

def test_date_foreign_keys(transactions, dimensions):
    """Verifies that all date_keys exist in dim_dates."""
    valid_keys = set(dimensions["dates"]["date_key"])
    assert transactions["date_key"].isin(valid_keys).all()

def test_expected_schema_columns(transactions):
    """Verifies that all required analytical columns exist with expected data presence."""
    required = [
        "transaction_id", "customer_key", "customer_id", "merchant_key", "merchant_id",
        "date_key", "timestamp", "amount", "currency", "payment_method_key", "payment_method",
        "merchant_category", "merchant_country", "customer_country", "device_type", "channel",
        "is_3ds_authenticated", "auth_status", "processing_fee", "interchange_fee", "scheme_fee",
        "net_revenue", "net_contribution", "latency_ms", "risk_score", "refund_flag",
        "chargeback_flag", "fraud_flag", "is_soft_decline", "addressable_leakage_amount"
    ]
    for col in required:
        assert col in transactions.columns, f"Missing expected column: {col}"
