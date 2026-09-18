"""
PAYMENTIQ Dimensional Entity Generator
Generates realistic, reference-grade dimension tables for customers, merchants, payment methods, decline codes, and dates.
"""
import uuid
import datetime
import pandas as pd
import numpy as np
from pathlib import Path
from typing import Dict, Any

from python.utils.logger import setup_logger

logger = setup_logger("entity_generator")

class EntityGenerator:
    """Generates deterministic dimensional entities with realistic business attributes."""

    def __init__(self, seed: int = 42):
        self.seed = seed
        self.rng = np.random.default_rng(seed)

    def generate_customers(self, n_customers: int) -> pd.DataFrame:
        """Generates customer dimension records."""
        logger.info("Generating %d customer records...", n_customers)

        customer_ids = [f"CUST-{i+1:06d}" for i in range(n_customers)]
        
        # Registration dates spread over 2022-01-01 to 2024-06-30
        start_date = datetime.date(2022, 1, 1)
        end_date = datetime.date(2024, 6, 30)
        days_range = (end_date - start_date).days
        signup_offsets = self.rng.integers(0, days_range, size=n_customers)
        signup_dates = [start_date + datetime.timedelta(days=int(offset)) for offset in signup_offsets]

        # Geographic distribution (weighted to key cardholder markets)
        countries = ["US", "GB", "DE", "FR", "CA", "AU"]
        country_probs = [0.45, 0.20, 0.12, 0.10, 0.08, 0.05]
        customer_countries = self.rng.choice(countries, size=n_customers, p=country_probs)

        # Segments & acquisition channels
        segments = ["Retail Consumer", "Affluent / VIP", "Small Business", "Corporate / Commercial"]
        segment_probs = [0.65, 0.15, 0.15, 0.05]
        customer_segments = self.rng.choice(segments, size=n_customers, p=segment_probs)

        channels = ["Organic Search", "Paid Digital", "Partner Referral", "Direct App", "Affiliate"]
        channel_probs = [0.35, 0.25, 0.20, 0.12, 0.08]
        acq_channels = self.rng.choice(channels, size=n_customers, p=channel_probs)

        # Baseline credit/risk tiers
        risk_tiers = ["Low Risk", "Standard", "Elevated Risk"]
        risk_probs = [0.75, 0.20, 0.05]
        risk_assignments = self.rng.choice(risk_tiers, size=n_customers, p=risk_probs)

        df = pd.DataFrame({
            "customer_key": np.arange(1, n_customers + 1, dtype=np.int32),
            "customer_id": customer_ids,
            "signup_date": signup_dates,
            "customer_country": customer_countries,
            "customer_segment": customer_segments,
            "acquisition_channel": acq_channels,
            "risk_tier": risk_assignments
        })
        return df

    def generate_merchants(self, n_merchants: int) -> pd.DataFrame:
        """Generates merchant dimension records."""
        logger.info("Generating %d merchant records...", n_merchants)

        merchant_ids = [f"MERCH-{i+1:04d}" for i in range(n_merchants)]

        categories_catalog = [
            ("5411", "Grocery & Supermarkets", 0.18, 15),
            ("5812", "Restaurants & Dining", 0.22, 25),
            ("5311", "Department Stores & Retail", 0.20, 20),
            ("5732", "Consumer Electronics", 0.10, 35),
            ("7011", "Hotels & Travel", 0.08, 30),
            ("4722", "Airlines & Transit", 0.04, 25),
            ("5999", "Digital Goods & Gaming", 0.10, 45),
            ("5651", "Apparel & Fashion", 0.08, 25),
        ]

        mcc_codes = [c[0] for c in categories_catalog]
        mcc_names = [c[1] for c in categories_catalog]
        mcc_weights = [c[2] for c in categories_catalog]
        mcc_markups = {c[0]: c[3] for c in categories_catalog}

        mcc_assignments = self.rng.choice(mcc_codes, size=n_merchants, p=mcc_weights)
        mcc_name_map = dict(zip(mcc_codes, mcc_names))

        merchant_names = [
            f"{mcc_name_map[mcc].split()[0]} Enterprise {i+1}"
            for i, mcc in enumerate(mcc_assignments)
        ]

        countries = ["US", "GB", "DE", "FR", "CA", "AU"]
        country_probs = [0.45, 0.20, 0.12, 0.10, 0.08, 0.05]
        merchant_countries = self.rng.choice(countries, size=n_merchants, p=country_probs)

        pricing_tiers = ["Enterprise IC+", "Mid-Market Blended", "SMB Flat Rate"]
        tier_probs = [0.10, 0.30, 0.60]
        pricing_assignments = self.rng.choice(pricing_tiers, size=n_merchants, p=tier_probs)

        # Base contract fee markups (in basis points)
        base_markups = np.array([mcc_markups[mcc] for mcc in mcc_assignments], dtype=np.int32)
        tier_modifier = np.where(pricing_assignments == "Enterprise IC+", -5,
                        np.where(pricing_assignments == "SMB Flat Rate", 15, 0))
        fee_markups = base_markups + tier_modifier

        # Onboarding date spread
        start_date = datetime.date(2021, 1, 1)
        end_date = datetime.date(2023, 12, 31)
        days_range = (end_date - start_date).days
        onboarding_offsets = self.rng.integers(0, days_range, size=n_merchants)
        onboarding_dates = [start_date + datetime.timedelta(days=int(offset)) for offset in onboarding_offsets]

        df = pd.DataFrame({
            "merchant_key": np.arange(1, n_merchants + 1, dtype=np.int32),
            "merchant_id": merchant_ids,
            "merchant_name": merchant_names,
            "mcc_code": mcc_assignments,
            "merchant_category": [mcc_name_map[m] for m in mcc_assignments],
            "merchant_country": merchant_countries,
            "onboarding_date": onboarding_dates,
            "pricing_tier": pricing_assignments,
            "acquirer_markup_bps": fee_markups
        })
        return df

    def generate_payment_methods(self) -> pd.DataFrame:
        """Generates payment method dimension catalog."""
        logger.info("Generating payment methods catalog...")
        data = [
            (1, "PM-01", "Credit Card", "Visa", "Consumer Credit", 0.890, 165, 14, 25),
            (2, "PM-02", "Credit Card", "Mastercard", "Consumer Credit", 0.885, 160, 13, 25),
            (3, "PM-03", "Credit Card", "American Express", "Commercial Credit", 0.875, 235, 18, 30),
            (4, "PM-04", "Debit Card", "Visa", "Consumer Debit", 0.918, 65, 11, 20),
            (5, "PM-05", "Debit Card", "Mastercard", "Consumer Debit", 0.912, 60, 11, 20),
            (6, "PM-06", "Digital Wallet", "Apple Pay (Card Backed)", "Consumer Digital", 0.935, 145, 15, 22),
            (7, "PM-07", "Digital Wallet", "Google Pay (Card Backed)", "Consumer Digital", 0.928, 145, 15, 22),
            (8, "PM-08", "BNPL", "Klarna / Afterpay Rail", "Installment Loan", 0.820, 240, 20, 50),
            (9, "PM-09", "Instant Bank Transfer", "FedNow / SEPA Instant", "Direct A2A", 0.952, 35, 8, 15)
        ]
        columns = [
            "payment_method_key", "payment_method_id", "method_name", "card_brand",
            "card_type", "auth_rate_baseline", "interchange_rate_bps", "scheme_fee_bps", "acquirer_fee_bps"
        ]
        return pd.DataFrame(data, columns=columns)

    def generate_decline_codes(self) -> pd.DataFrame:
        """Generates decline codes catalog with ISO 8583 standards."""
        logger.info("Generating decline codes catalog...")
        data = [
            ("00", "Approved", "None", False, "Transaction approved by issuer"),
            ("51", "Insufficient Funds", "Soft Decline", True, "Retry after 24-48 hours or prompt alternative payment method"),
            ("91", "Issuer System Unavailable", "Soft Technical", True, "Automatic immediate retry with exponential backoff"),
            ("19", "Network Timeout", "Soft Technical", True, "Retry transaction through secondary routing gateway"),
            ("05", "Do Not Honor", "Hard Decline", False, "Customer must contact issuing bank; do not retry automatically"),
            ("54", "Expired Card", "Hard Decline", False, "Prompt customer for updated card expiration or new credential"),
            ("14", "Invalid Card Number", "Hard Decline", False, "Reject card entry; potential data entry error or fraud card testing"),
            ("41", "Lost / Stolen Card", "Hard Fraud", False, "Immediate transaction block and alert fraud operations team")
        ]
        columns = ["decline_code", "decline_reason", "decline_type", "is_retryable", "recommended_action"]
        return pd.DataFrame(data, columns=columns)

    def generate_date_dimension(self, start_date: str = "2022-01-01", end_date: str = "2026-12-31") -> pd.DataFrame:
        """Generates full calendar dimension with financial periods."""
        logger.info("Generating date dimension from %s to %s...", start_date, end_date)
        dates = pd.date_range(start=start_date, end=end_date, freq="D")
        
        df = pd.DataFrame({
            "date_key": dates.strftime("%Y%m%d").astype(np.int32),
            "full_date": dates.date,
            "year": dates.year.astype(np.int16),
            "quarter": dates.quarter.astype(np.int8),
            "month": dates.month.astype(np.int8),
            "month_name": dates.strftime("%B"),
            "week_of_year": dates.isocalendar().week.astype(np.int8),
            "day_of_month": dates.day.astype(np.int8),
            "day_of_week": dates.dayofweek.astype(np.int8),
            "day_name": dates.strftime("%A"),
            "is_weekend": dates.dayofweek.isin([5, 6]).astype(bool),
            "is_month_end": dates.is_month_end.astype(bool),
            "is_quarter_end": dates.is_quarter_end.astype(bool)
        })
        return df

    def generate_and_save_all(self, output_dir: str = "data/reference", n_customers: int = 5000, n_merchants: int = 250) -> Dict[str, pd.DataFrame]:
        """Generates all dimension tables and persists them to parquet/csv."""
        Path(output_dir).mkdir(parents=True, exist_ok=True)

        customers = self.generate_customers(n_customers)
        merchants = self.generate_merchants(n_merchants)
        payment_methods = self.generate_payment_methods()
        decline_codes = self.generate_decline_codes()
        dates = self.generate_date_dimension()

        entities = {
            "dim_customers": customers,
            "dim_merchants": merchants,
            "dim_payment_methods": payment_methods,
            "dim_decline_codes": decline_codes,
            "dim_dates": dates
        }

        for name, df in entities.items():
            parquet_path = Path(output_dir) / f"{name}.parquet"
            csv_path = Path(output_dir) / f"{name}.csv"
            df.to_parquet(parquet_path, index=False)
            df.to_csv(csv_path, index=False)
            logger.info("Saved %s (%d rows) to %s", name, len(df), parquet_path)

        return entities

if __name__ == "__main__":
    generator = EntityGenerator(seed=42)
    generator.generate_and_save_all(n_customers=5000, n_merchants=250)
