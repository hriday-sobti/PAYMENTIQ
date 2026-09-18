"""
PAYMENTIQ Data Cleaning & Feature Transformation Pipeline
Downcasts memory types, enriches transaction features with financial margins,
flags cross-border payments, and calculates addressable leakage.
"""
import time
import pandas as pd
import numpy as np
from pathlib import Path
from typing import Dict, Any, List

from python.utils.logger import setup_logger

logger = setup_logger("data_cleaner")

class DataCleaner:
    """Enriches and optimizes transaction batches for analytics warehouse loading."""

    def __init__(self, raw_dir: str = "data/raw", processed_dir: str = "data/processed", ref_dir: str = "data/reference"):
        self.raw_dir = Path(raw_dir)
        self.processed_dir = Path(processed_dir)
        self.ref_dir = Path(ref_dir)
        self.processed_dir.mkdir(parents=True, exist_ok=True)

        # Load decline codes for retryability mapping
        self.decline_codes_df = pd.read_parquet(self.ref_dir / "dim_decline_codes.parquet")
        self.soft_codes = set(self.decline_codes_df[self.decline_codes_df["is_retryable"]]["decline_code"])

    def clean_and_transform_chunk(self, df: pd.DataFrame) -> pd.DataFrame:
        """Applies type downcasting, feature engineering, and financial margins."""
        # 1. Type Downcasting
        df["customer_key"] = df["customer_key"].astype(np.int32)
        df["merchant_key"] = df["merchant_key"].astype(np.int32)
        df["payment_method_key"] = df["payment_method_key"].astype(np.int16)
        df["date_key"] = df["date_key"].astype(np.int32)
        df["latency_ms"] = df["latency_ms"].astype(np.int32)
        df["risk_score"] = df["risk_score"].astype(np.int16)
        df["retry_attempt"] = df["retry_attempt"].astype(np.int8)

        # Categorical columns for high memory compression
        cat_cols = ["currency", "merchant_country", "customer_country", "device_type", "channel", "auth_status"]
        for col in cat_cols:
            df[col] = df[col].astype("category")

        # 2. Temporal Features
        ts = pd.to_datetime(df["timestamp"])
        df["hour_of_day"] = ts.dt.hour.astype(np.int8)
        df["day_of_week"] = ts.dt.dayofweek.astype(np.int8)
        df["is_weekend"] = ts.dt.dayofweek.isin([5, 6]).astype(bool)

        # 3. Behavioral Flags
        df["is_high_value"] = (df["amount"] >= 500.0).astype(bool)
        df["is_cross_border"] = (df["customer_country"] != df["merchant_country"]).astype(bool)

        # 4. Financial Margins & Unit Economics
        # Net Revenue = Gross Processing Fee - Interchange Cost - Scheme Fee
        df["net_revenue"] = np.round(df["processing_fee"] - df["interchange_fee"] - df["scheme_fee"], 2)

        # Addressable Revenue Leakage
        # Soft declines are recoverable via retry routing
        is_soft = df["decline_code"].isin(self.soft_codes)
        df["is_soft_decline"] = is_soft
        df["addressable_leakage_amount"] = np.where(is_soft, df["amount"], 0.0)

        # Net Contribution: Net Revenue minus chargeback loss provision
        # For chargebacked transactions: full amount lost + $20 dispute assessment fee
        cb_loss = np.where(df["chargeback_flag"], df["amount"] + 20.0, 0.0)
        df["net_contribution"] = np.round(df["net_revenue"] - cb_loss, 2)

        return df

    def run_cleaning_pipeline(self) -> List[Path]:
        """Processes all raw partitions and saves transformed files to processed directory."""
        start_time = time.time()
        logger.info("======================================================================")
        logger.info("Starting PAYMENTIQ Data Cleaning & Feature Transformation Pipeline")
        logger.info("======================================================================")

        raw_files = sorted(list(self.raw_dir.glob("transactions_part_*.parquet")))
        if not raw_files:
            raise FileNotFoundError(f"No raw transaction files found in {self.raw_dir}")

        processed_files = []
        total_rows = 0

        for i, f in enumerate(raw_files):
            logger.info("Cleaning partition %d/%d: %s...", i + 1, len(raw_files), f.name)
            raw_chunk = pd.read_parquet(f)
            clean_chunk = self.clean_and_transform_chunk(raw_chunk)

            out_filename = self.processed_dir / f"clean_transactions_part_{i+1:03d}.parquet"
            clean_chunk.to_parquet(out_filename, index=False)
            processed_files.append(out_filename)
            total_rows += len(clean_chunk)

        # Copy disputes and support cases to processed
        disputes_file = self.raw_dir / "disputes.parquet"
        if disputes_file.exists():
            dsp = pd.read_parquet(disputes_file)
            dsp.to_parquet(self.processed_dir / "clean_disputes.parquet", index=False)
            logger.info("Processed %d dispute records", len(dsp))

        cases_file = self.raw_dir / "support_cases.parquet"
        if cases_file.exists():
            cases = pd.read_parquet(cases_file)
            cases.to_parquet(self.processed_dir / "clean_support_cases.parquet", index=False)
            logger.info("Processed %d support case records", len(cases))

        elapsed = time.time() - start_time
        logger.info("======================================================================")
        logger.info("Data Cleaning & Feature Transformation Pipeline Complete!")
        logger.info("Total Records Cleaned & Enriched: %d", total_rows)
        logger.info("Output Partitions Saved: %d to %s", len(processed_files), self.processed_dir)
        logger.info("Pipeline Duration: %.2f seconds (%.0f rows/sec)", elapsed, total_rows / max(elapsed, 0.01))
        logger.info("======================================================================")
        return processed_files

if __name__ == "__main__":
    cleaner = DataCleaner()
    cleaner.run_cleaning_pipeline()
