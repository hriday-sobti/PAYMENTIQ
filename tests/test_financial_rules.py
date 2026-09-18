"""
PAYMENTIQ Unit Tests for Financial Integrity, Accounting Invariants & Fee Dynamics
Validates that all financial calculations obey P&L accounting invariants across categories and rails.
"""
import pytest
import pandas as pd
import numpy as np
from pathlib import Path

@pytest.fixture(scope="module")
def sample_transactions():
    """Loads a partition of processed transactions for financial rule auditing."""
    files = sorted(list(Path("data/processed").glob("clean_transactions_part_*.parquet")))
    assert len(files) > 0, "No processed transaction partitions found!"
    df = pd.read_parquet(files[0])
    return df

# --- Core Accounting Invariants ---

def test_amount_strictly_positive(sample_transactions):
    """Rule: All transaction amounts must be strictly greater than $0.00."""
    assert (sample_transactions["amount"] > 0.0).all()

def test_fees_non_negative(sample_transactions):
    """Rule: Processing, interchange, and scheme fees must be non-negative."""
    assert (sample_transactions["processing_fee"] >= 0.0).all()
    assert (sample_transactions["interchange_fee"] >= 0.0).all()
    assert (sample_transactions["scheme_fee"] >= 0.0).all()

def test_processing_fee_less_than_amount(sample_transactions):
    """Rule: Processing fee must never exceed transaction gross amount."""
    assert (sample_transactions["processing_fee"] < sample_transactions["amount"]).all()

def test_net_revenue_formula_reconciliation(sample_transactions):
    """Rule: Net Revenue == Gross Processing Fee - Interchange Cost - Scheme Fee."""
    expected_net = np.round(
        sample_transactions["processing_fee"] -
        sample_transactions["interchange_fee"] -
        sample_transactions["scheme_fee"],
        2
    )
    diff = np.abs(sample_transactions["net_revenue"] - expected_net)
    assert (diff < 0.01).all()

def test_net_contribution_integrity(sample_transactions):
    """Rule: Net contribution must properly penalize chargebacks by amount + assessment fee."""
    cb_mask = sample_transactions["chargeback_flag"]
    if cb_mask.any():
        cb_rows = sample_transactions[cb_mask]
        expected_cb_contribution = np.round(cb_rows["net_revenue"] - (cb_rows["amount"] + 20.0), 2)
        diff = np.abs(cb_rows["net_contribution"] - expected_cb_contribution)
        assert (diff < 0.01).all()

def test_approved_transactions_decline_consistency(sample_transactions):
    """Rule: Approved transactions must not have decline reasons or decline codes."""
    app_mask = sample_transactions["auth_status"] == "Approved"
    assert sample_transactions.loc[app_mask, "decline_code"].isnull().all()
    assert sample_transactions.loc[app_mask, "decline_reason"].isnull().all()

def test_declined_transactions_decline_consistency(sample_transactions):
    """Rule: Declined and failed transactions must have valid decline codes and reasons."""
    not_app = sample_transactions["auth_status"] != "Approved"
    assert sample_transactions.loc[not_app, "decline_code"].notnull().all()
    assert sample_transactions.loc[not_app, "decline_reason"].notnull().all()

# --- Parameterized Tests Across Merchant Categories ---

MERCHANT_CATEGORIES = [
    "Grocery & Supermarkets",
    "Restaurants & Dining",
    "Department Stores & Retail",
    "Consumer Electronics",
    "Hotels & Travel",
    "Airlines & Transit",
    "Digital Goods & Gaming",
    "Apparel & Fashion"
]

@pytest.mark.parametrize("category", MERCHANT_CATEGORIES)
def test_category_amount_bounds(sample_transactions, category):
    """Rule: Each merchant category must exhibit positive amounts and valid ticket sizes."""
    cat_df = sample_transactions[sample_transactions["merchant_category"] == category]
    if len(cat_df) > 0:
        assert (cat_df["amount"] > 0.0).all()
        assert cat_df["amount"].mean() > 5.0
        assert cat_df["processing_fee"].mean() > 0.0

@pytest.mark.parametrize("category", MERCHANT_CATEGORIES)
def test_category_fee_sanity(sample_transactions, category):
    """Rule: Processing fees in every category must obey economic bounds (<20% for retail, <40% for digital micro-txs)."""
    cat_df = sample_transactions[sample_transactions["merchant_category"] == category]
    if len(cat_df) > 0:
        fee_pct = cat_df["processing_fee"] / cat_df["amount"]
        threshold = 0.40 if category == "Digital Goods & Gaming" else 0.20
        assert (fee_pct < threshold).all()

# --- Parameterized Tests Across Payment Rails ---

PAYMENT_RAILS = [
    "Credit Card",
    "Debit Card",
    "Digital Wallet",
    "BNPL",
    "Instant Bank Transfer"
]

@pytest.mark.parametrize("rail", PAYMENT_RAILS)
def test_payment_rail_auth_bounds(sample_transactions, rail):
    """Rule: Each payment rail must have an authorization rate between 70% and 99%."""
    rail_df = sample_transactions[sample_transactions["payment_method"] == rail]
    if len(rail_df) > 0:
        auth_rate = (rail_df["auth_status"] == "Approved").mean() * 100.0
        assert 70.0 <= auth_rate <= 99.0

@pytest.mark.parametrize("rail", PAYMENT_RAILS)
def test_payment_rail_net_revenue_positive(sample_transactions, rail):
    """Rule: Sum of net revenue across each payment rail must be positive."""
    rail_df = sample_transactions[sample_transactions["payment_method"] == rail]
    if len(rail_df) > 0:
        assert rail_df["net_revenue"].sum() > 0.0

# --- Currencies & Cross-Border Rules ---

CURRENCIES = ["USD", "EUR", "GBP", "CAD", "AUD"]

@pytest.mark.parametrize("curr", CURRENCIES)
def test_currency_amount_consistency(sample_transactions, curr):
    """Rule: Transactions denominated in active currencies must obey positive bounds."""
    curr_df = sample_transactions[sample_transactions["currency"] == curr]
    if len(curr_df) > 0:
        assert (curr_df["amount"] > 0.0).all()
        assert (curr_df["processing_fee"] >= 0.0).all()
