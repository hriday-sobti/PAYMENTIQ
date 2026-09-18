"""
PAYMENTIQ Unit Tests for Financial Integrity & Accounting Rules
Validates that all financial calculations (GTV, fees, net revenue, contribution) obey P&L accounting invariants.
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
