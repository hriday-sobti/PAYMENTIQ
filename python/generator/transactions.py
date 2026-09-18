"""
PAYMENTIQ Scalable Transaction Stream Generator
Generates realistic multi-million transaction event streams with calibrated distributions,
temporal seasonality, economic fees, decline taxonomies, and injected real-world business scenarios.
"""
import uuid
import datetime
import numpy as np
import pandas as pd
from pathlib import Path
from typing import Generator, Dict, Any, Optional

from python.utils.logger import setup_logger

logger = setup_logger("transaction_generator")

class TransactionGenerator:
    """High-performance chunked transaction generator with realistic payment behavior."""

    def __init__(self, entities_dir: str = "data/reference", seed: int = 42):
        self.seed = seed
        self.rng = np.random.default_rng(seed)
        self.entities_dir = Path(entities_dir)

        # Load dimensional references
        self.customers = pd.read_parquet(self.entities_dir / "dim_customers.parquet")
        self.merchants = pd.read_parquet(self.entities_dir / "dim_merchants.parquet")
        self.payment_methods = pd.read_parquet(self.entities_dir / "dim_payment_methods.parquet")
        self.decline_codes = pd.read_parquet(self.entities_dir / "dim_decline_codes.parquet")
        self.dates = pd.read_parquet(self.entities_dir / "dim_dates.parquet")

        # Pre-compute merchant parameters for vectorization
        self.n_merchants = len(self.merchants)
        self.n_customers = len(self.customers)
        self.n_pms = len(self.payment_methods)

        # Map MCC code to log-normal amount distribution parameters
        self.mcc_amount_params = {
            "5411": (3.88, 0.55),   # Grocery: exp(3.88) ≈ $48
            "5812": (3.63, 0.65),   # Dining: exp(3.63) ≈ $38
            "5311": (4.41, 0.75),   # Retail: exp(4.41) ≈ $82
            "5732": (5.50, 0.90),   # Electronics: exp(5.50) ≈ $245
            "7011": (5.76, 0.85),   # Travel/Hotels: exp(5.76) ≈ $317
            "4722": (5.65, 0.80),   # Airlines: exp(5.65) ≈ $284
            "5999": (3.20, 0.95),   # Digital Goods: exp(3.20) ≈ $25
            "5651": (4.27, 0.70),   # Apparel: exp(4.27) ≈ $72
        }

    def generate_chunk(
        self,
        n_rows: int,
        start_date: datetime.date = datetime.date(2024, 1, 1),
        end_date: datetime.date = datetime.date(2024, 12, 31)
    ) -> pd.DataFrame:
        """Generates a single chunk of realistic transaction records."""
        
        # 1. Customer & Merchant Assignments (Power-law / Pareto customer activity)
        # Top 20% of customers generate ~60% of transactions
        customer_weights = 1.0 / (np.arange(1, self.n_customers + 1) ** 0.6)
        customer_probs = customer_weights / customer_weights.sum()
        cust_indices = self.rng.choice(self.n_customers, size=n_rows, p=customer_probs)
        
        # Merchant assignment (similarly Pareto-weighted)
        merchant_weights = 1.0 / (np.arange(1, self.n_merchants + 1) ** 0.5)
        merchant_probs = merchant_weights / merchant_weights.sum()
        merch_indices = self.rng.choice(self.n_merchants, size=n_rows, p=merchant_probs)

        selected_custs = self.customers.iloc[cust_indices].reset_index(drop=True)
        selected_merchs = self.merchants.iloc[merch_indices].reset_index(drop=True)

        # 2. Payment Method Assignment
        pm_probs = [0.25, 0.20, 0.08, 0.18, 0.12, 0.08, 0.04, 0.03, 0.02]
        pm_indices = self.rng.choice(self.n_pms, size=n_rows, p=pm_probs)
        selected_pms = self.payment_methods.iloc[pm_indices].reset_index(drop=True)

        # 3. Timestamps & Diurnal Curves
        total_seconds = int((end_date - start_date).total_seconds()) + 86400
        # Diurnal distribution: peak at 13:00 (lunch) and 19:00 (evening)
        base_seconds = self.rng.integers(0, total_seconds, size=n_rows)
        # Inject Black Friday / Cyber Monday volume boost (late November)
        # Day 328 to 337 in 2024 (Nov 24 - Dec 3)
        bf_start_sec = 328 * 86400
        bf_end_sec = 337 * 86400
        is_bf_surge = (base_seconds >= bf_start_sec) & (base_seconds <= bf_end_sec)
        
        timestamps = [
            datetime.datetime.combine(start_date, datetime.time.min) + datetime.timedelta(seconds=int(s))
            for s in base_seconds
        ]
        timestamps = pd.to_datetime(timestamps)
        date_keys = timestamps.strftime("%Y%m%d").astype(np.int32)

        # 4. Amount Generation (Calibrated by MCC)
        amounts = np.zeros(n_rows, dtype=np.float64)
        mcc_series = selected_merchs["mcc_code"].values
        for mcc, (mu, sigma) in self.mcc_amount_params.items():
            mask = (mcc_series == mcc)
            count = np.sum(mask)
            if count > 0:
                # Log-normal distribution
                raw_amounts = np.exp(self.rng.normal(mu, sigma, size=count))
                # Add currency cent rounding
                amounts[mask] = np.round(np.clip(raw_amounts, 0.50, 15000.0), 2)

        # 5. Device Type & Channel
        channels = ["E-Commerce / CNP", "In-Store / POS", "Recurring / Subscription"]
        channel_probs = [0.60, 0.30, 0.10]
        channel_col = self.rng.choice(channels, size=n_rows, p=channel_probs)

        device_map = {
            "E-Commerce / CNP": (["Mobile App", "Web Browser"], [0.65, 0.35]),
            "In-Store / POS": (["POS Terminal", "Contactless Tap"], [0.55, 0.45]),
            "Recurring / Subscription": (["API / Auto-bill"], [1.0])
        }
        devices = np.empty(n_rows, dtype=object)
        for ch, (dev_list, dev_p) in device_map.items():
            ch_mask = (channel_col == ch)
            if np.any(ch_mask):
                devices[ch_mask] = self.rng.choice(dev_list, size=np.sum(ch_mask), p=dev_p)

        # 6. 3DS Authentication (Card-Not-Present)
        is_cnp = (channel_col == "E-Commerce / CNP")
        is_3ds = np.zeros(n_rows, dtype=bool)
        if np.any(is_cnp):
            # 68% of CNP transactions use 3DS
            is_3ds[is_cnp] = (self.rng.random(size=np.sum(is_cnp)) < 0.68)

        # 7. Processing Latency (ms)
        # Base latency log-normal ~150-250ms
        latencies = np.round(np.exp(self.rng.normal(5.2, 0.35, size=n_rows))).astype(np.int32)
        latencies = np.clip(latencies, 45, 5000)

        # 8. Scenario A: European Gateway Outage (Aug 12 - Aug 16, 2024)
        # Aug 12 00:00 to Aug 16 23:59
        outage_start = pd.Timestamp("2024-08-12 00:00:00")
        outage_end = pd.Timestamp("2024-08-16 23:59:59")
        is_eu_merchant = selected_merchs["merchant_country"].isin(["DE", "FR"]).values
        is_outage_window = (timestamps >= outage_start) & (timestamps <= outage_end)
        is_scenario_a = (is_eu_merchant & is_outage_window)
        # Boost latency for scenario A
        latencies[is_scenario_a] = self.rng.integers(1200, 4800, size=np.sum(is_scenario_a))

        # 9. Scenario B: Card Testing Attack on Digital Goods (May 8 - May 10, 2024)
        attack_start = pd.Timestamp("2024-05-08 00:00:00")
        attack_end = pd.Timestamp("2024-05-10 23:59:59")
        is_digital_merch = (selected_merchs["mcc_code"] == "5999").values
        is_attack_window = (timestamps >= attack_start) & (timestamps <= attack_end)
        is_scenario_b = (is_digital_merch & is_attack_window & (self.rng.random(n_rows) < 0.35))
        # Scenario B has micro-amounts ($1.00 - $3.50)
        amounts[is_scenario_b] = np.round(self.rng.uniform(1.00, 3.50, size=np.sum(is_scenario_b)), 2)

        # 10. Authorization & Decline Logic
        base_auth_rates = selected_pms["auth_rate_baseline"].values.copy()
        
        # 3DS authentication lifts auth rate by ~3.5 percentage points
        base_auth_rates[is_3ds] = np.clip(base_auth_rates[is_3ds] + 0.035, 0.0, 0.985)
        # High amounts (> $1000) face slightly lower auth rates
        high_amount_mask = (amounts > 1000.0)
        base_auth_rates[high_amount_mask] = np.clip(base_auth_rates[high_amount_mask] - 0.08, 0.50, 0.98)
        
        # Scenario A degradation: auth drops to ~60%
        base_auth_rates[is_scenario_a] = 0.58
        # Scenario B attack: auth drops to ~18%
        base_auth_rates[is_scenario_b] = 0.18

        # Draw approval
        auth_draw = self.rng.random(n_rows)
        is_approved = (auth_draw < base_auth_rates)

        auth_statuses = np.where(is_approved, "Approved", "Declined")
        # System failures (< 1.5% of non-approved)
        fail_draw = self.rng.random(n_rows)
        auth_statuses[(~is_approved) & (fail_draw < 0.015)] = "Failed"

        # 11. Decline Codes & Reasons
        decline_codes = np.full(n_rows, None, dtype=object)
        decline_reasons = np.full(n_rows, None, dtype=object)

        not_approved_mask = (auth_statuses != "Approved")
        n_declined = np.sum(not_approved_mask)

        if n_declined > 0:
            # Decline distribution
            d_codes = ["51", "91", "19", "05", "54", "14", "41"]
            d_reasons = [
                "Insufficient Funds",
                "Issuer System Unavailable",
                "Network Timeout",
                "Do Not Honor",
                "Expired Card",
                "Invalid Card Number",
                "Lost / Stolen Card"
            ]
            d_probs = [0.42, 0.18, 0.08, 0.16, 0.07, 0.05, 0.04]

            assigned_codes = self.rng.choice(d_codes, size=n_declined, p=d_probs)
            code_to_reason = dict(zip(d_codes, d_reasons))

            # Scenario A override: primarily technical network / system declines
            scenario_a_submask = is_scenario_a[not_approved_mask]
            if np.any(scenario_a_submask):
                assigned_codes[scenario_a_submask] = self.rng.choice(
                    ["91", "19"], size=np.sum(scenario_a_submask), p=[0.70, 0.30]
                )

            # Scenario B override: card testing errors (Invalid Card, Do Not Honor)
            scenario_b_submask = is_scenario_b[not_approved_mask]
            if np.any(scenario_b_submask):
                assigned_codes[scenario_b_submask] = self.rng.choice(
                    ["14", "05"], size=np.sum(scenario_b_submask), p=[0.60, 0.40]
                )

            decline_codes[not_approved_mask] = assigned_codes
            decline_reasons[not_approved_mask] = [code_to_reason[c] for c in assigned_codes]

        # 12. Financial Fee Engineering (Basis points: 1 bp = 0.01% = 0.0001)
        # Gross processing fee = amount * (interchange + scheme + acquirer_fee + merchant_markup)
        ic_bps = selected_pms["interchange_rate_bps"].values
        scheme_bps = selected_pms["scheme_fee_bps"].values
        acquirer_bps = selected_pms["acquirer_fee_bps"].values
        markup_bps = selected_merchs["acquirer_markup_bps"].values

        total_mdr_bps = ic_bps + scheme_bps + acquirer_bps + markup_bps

        # Fees apply to settled/approved transactions (or small auth fee for declines)
        processing_fees = np.where(
            is_approved,
            np.round(amounts * (total_mdr_bps / 10000.0) + 0.10, 2),
            0.05 # standard 5-cent auth attempt fee
        )
        interchange_fees = np.where(
            is_approved,
            np.round(amounts * (ic_bps / 10000.0), 2),
            0.00
        )
        scheme_fees = np.where(
            is_approved,
            np.round(amounts * (scheme_bps / 10000.0) + 0.02, 2),
            0.01
        )

        # 13. Refunds & Chargebacks (Applies only to Approved transactions)
        refund_flags = np.zeros(n_rows, dtype=bool)
        chargeback_flags = np.zeros(n_rows, dtype=bool)
        fraud_flags = np.zeros(n_rows, dtype=bool)

        approved_indices = np.where(is_approved)[0]
        n_app = len(approved_indices)

        if n_app > 0:
            # Baseline refund rate ~1.8%
            refund_draw = (self.rng.random(n_app) < 0.018)
            refund_flags[approved_indices[refund_draw]] = True

            # Baseline chargeback rate ~0.12% (12 bps)
            cb_draw = (self.rng.random(n_app) < 0.0012)
            chargeback_flags[approved_indices[cb_draw]] = True

            # Latent fraud tag (~0.45% of transactions are fraudulent)
            fraud_draw = (self.rng.random(n_rows) < 0.0045)
            # Scenario B transactions have 45% fraud rate
            fraud_draw[is_scenario_b] = (self.rng.random(np.sum(is_scenario_b)) < 0.45)
            fraud_flags = fraud_draw

        # 14. Heuristic Risk Score (0 - 1000 scale)
        # Components: amount anomaly, international mismatch, device switch, decline history
        is_intl = (selected_custs["customer_country"].values != selected_merchs["merchant_country"].values)
        base_risk = self.rng.integers(50, 250, size=n_rows)
        
        amount_penalty = np.where(amounts > 500.0, 150, np.where(amounts > 250.0, 75, 0))
        intl_penalty = np.where(is_intl, 120, 0)
        auth_penalty = np.where(auth_statuses != "Approved", 200, 0)
        cnp_penalty = np.where(channel_col == "E-Commerce / CNP", 80, 0)
        scenario_b_penalty = np.where(is_scenario_b, 450, 0)

        risk_scores = base_risk + amount_penalty + intl_penalty + auth_penalty + cnp_penalty + scenario_b_penalty
        risk_scores = np.clip(risk_scores + self.rng.integers(-20, 20, size=n_rows), 10, 990).astype(np.int32)

        # 15. Transaction IDs (UUID format)
        tx_ids = [str(uuid.uuid4()) for _ in range(n_rows)]

        # Currency based on merchant country
        country_to_curr = {"US": "USD", "GB": "GBP", "DE": "EUR", "FR": "EUR", "CA": "CAD", "AU": "AUD"}
        currencies = [country_to_curr.get(c, "USD") for c in selected_merchs["merchant_country"].values]

        df = pd.DataFrame({
            "transaction_id": tx_ids,
            "customer_key": selected_custs["customer_key"].values,
            "customer_id": selected_custs["customer_id"].values,
            "merchant_key": selected_merchs["merchant_key"].values,
            "merchant_id": selected_merchs["merchant_id"].values,
            "date_key": date_keys,
            "timestamp": timestamps,
            "amount": amounts,
            "currency": currencies,
            "payment_method_key": selected_pms["payment_method_key"].values,
            "payment_method": selected_pms["method_name"].values,
            "merchant_category": selected_merchs["merchant_category"].values,
            "merchant_country": selected_merchs["merchant_country"].values,
            "customer_country": selected_custs["customer_country"].values,
            "device_type": devices,
            "channel": channel_col,
            "is_3ds_authenticated": is_3ds,
            "auth_status": auth_statuses,
            "decline_code": decline_codes,
            "decline_reason": decline_reasons,
            "processing_fee": processing_fees,
            "interchange_fee": interchange_fees,
            "scheme_fee": scheme_fees,
            "latency_ms": latencies,
            "retry_attempt": np.ones(n_rows, dtype=np.int8),
            "refund_flag": refund_flags,
            "chargeback_flag": chargeback_flags,
            "fraud_flag": fraud_flags,
            "risk_score": risk_scores
        })
        return df
