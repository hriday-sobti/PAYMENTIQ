"""
PAYMENTIQ Disputes and Customer Service Cases Generator
Generates realistic chargeback dispute cases and customer operational support tickets
linked to underlying transaction events and system incidents.
"""
import uuid
import datetime
import numpy as np
import pandas as pd
from pathlib import Path
from typing import Dict, Any

from python.utils.logger import setup_logger

logger = setup_logger("disputes_and_cases")

class OperationalEventsGenerator:
    """Generates post-transaction dispute events and customer support incidents."""

    def __init__(self, seed: int = 42):
        self.seed = seed
        self.rng = np.random.default_rng(seed)

    def generate_disputes(self, transactions_df: pd.DataFrame) -> pd.DataFrame:
        """Generates formal chargeback dispute records from flagged transactions."""
        logger.info("Generating chargeback dispute records from transactions...")

        # Select transactions marked with chargeback_flag
        cb_txs = transactions_df[transactions_df["chargeback_flag"] == True].copy()
        n_disputes = len(cb_txs)
        logger.info("Found %d flagged chargeback transactions", n_disputes)

        if n_disputes == 0:
            return pd.DataFrame(columns=[
                "dispute_id", "transaction_id", "merchant_key", "customer_key",
                "dispute_date_key", "dispute_timestamp", "dispute_amount",
                "chargeback_fee", "dispute_reason", "dispute_status"
            ])

        # Dispute occurs 14 to 75 days after original transaction
        lag_days = self.rng.integers(14, 76, size=n_disputes)
        dispute_timestamps = [
            t + datetime.timedelta(days=int(d), hours=int(self.rng.integers(1, 24)))
            for t, d in zip(cb_txs["timestamp"].values, lag_days)
        ]
        dispute_timestamps = pd.to_datetime(dispute_timestamps)
        dispute_date_keys = dispute_timestamps.strftime("%Y%m%d").astype(np.int32)

        # Dispute reasons
        reasons = [
            "Fraudulent Card-Not-Present",
            "Merchandise / Service Not Received",
            "Merchandise Defective / Not As Described",
            "Canceled Recurring Subscription",
            "Unrecognized Transaction Entry"
        ]
        reason_probs = [0.45, 0.25, 0.15, 0.10, 0.05]
        assigned_reasons = self.rng.choice(reasons, size=n_disputes, p=reason_probs)

        # Standard merchant chargeback assessment fee ($15 - $25)
        fees = self.rng.choice([15.00, 20.00, 25.00], size=n_disputes, p=[0.30, 0.50, 0.20])

        # Dispute outcomes: merchants typically win 22% of disputes, lose 68%, 10% under review
        statuses = ["Lost (Debited)", "Won (Reversed)", "Under Arbitration"]
        status_probs = [0.68, 0.22, 0.10]
        assigned_statuses = self.rng.choice(statuses, size=n_disputes, p=status_probs)

        dispute_ids = [f"DSP-{uuid.uuid4().hex[:10].upper()}" for _ in range(n_disputes)]

        df = pd.DataFrame({
            "dispute_id": dispute_ids,
            "transaction_id": cb_txs["transaction_id"].values,
            "merchant_key": cb_txs["merchant_key"].values,
            "customer_key": cb_txs["customer_key"].values,
            "dispute_date_key": dispute_date_keys,
            "dispute_timestamp": dispute_timestamps,
            "dispute_amount": cb_txs["amount"].values,
            "chargeback_fee": fees,
            "dispute_reason": assigned_reasons,
            "dispute_status": assigned_statuses
        })
        return df

    def generate_support_cases(self, transactions_df: pd.DataFrame, n_extra_cases: int = 1500) -> pd.DataFrame:
        """Generates customer support incident tickets linked to declines and latency."""
        logger.info("Generating customer support tickets...")

        # 1. Cases directly triggered by transaction declines (especially soft declines)
        declined_txs = transactions_df[transactions_df["auth_status"] != "Approved"]
        # ~2.5% of declined cardholders contact support
        n_declined_sample = min(len(declined_txs), max(500, int(len(declined_txs) * 0.025)))
        sample_indices = self.rng.choice(len(declined_txs), size=n_declined_sample, replace=False)
        tx_sample = declined_txs.iloc[sample_indices].copy()

        # Support creation occurs 5 minutes to 48 hours after transaction
        delay_mins = self.rng.integers(5, 2880, size=n_declined_sample)
        case_timestamps = [
            t + datetime.timedelta(minutes=int(m))
            for t, m in zip(tx_sample["timestamp"].values, delay_mins)
        ]
        case_timestamps = pd.to_datetime(case_timestamps)
        date_keys = case_timestamps.strftime("%Y%m%d").astype(np.int32)

        categories = [
            "Decline / Authorization Failure Inquiry",
            "Suspected Duplicate Charge",
            "Refund Processing Status",
            "Account Security / Card Verification"
        ]
        cat_probs = [0.55, 0.20, 0.15, 0.10]
        case_cats = self.rng.choice(categories, size=n_declined_sample, p=cat_probs)

        severities = ["Low", "Medium", "High", "Critical"]
        sev_probs = [0.35, 0.45, 0.15, 0.05]
        case_sevs = self.rng.choice(severities, size=n_declined_sample, p=sev_probs)

        # Resolution time in minutes (log-normal, median ~120 mins)
        res_times = np.round(np.exp(self.rng.normal(4.8, 0.75, size=n_declined_sample))).astype(np.int32)
        res_times = np.clip(res_times, 10, 2880)

        # SLA threshold is 240 minutes (4 hours)
        sla_breached = (res_times > 240)

        # Customer Satisfaction (CSAT) score 1 to 5
        csat = np.where(sla_breached, self.rng.integers(1, 3, size=n_declined_sample),
               self.rng.integers(3, 6, size=n_declined_sample))

        case_ids = [f"CASE-{uuid.uuid4().hex[:8].upper()}" for _ in range(n_declined_sample)]

        df = pd.DataFrame({
            "case_id": case_ids,
            "customer_key": tx_sample["customer_key"].values,
            "customer_id": tx_sample["customer_id"].values,
            "transaction_id": tx_sample["transaction_id"].values,
            "created_date_key": date_keys,
            "created_timestamp": case_timestamps,
            "category": case_cats,
            "severity": case_sevs,
            "resolution_time_minutes": res_times,
            "sla_breached_flag": sla_breached,
            "csat_score": csat,
            "status": np.where(res_times < 1440, "Resolved", "Escalated")
        })
        return df
