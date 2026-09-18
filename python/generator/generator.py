"""
PAYMENTIQ Master Synthetic Data Generation Orchestrator
CLI entrypoint to generate configurable multi-tier datasets (DEV: 100K, TEST: 1M, FULL: 5M+).
"""
import os
import sys
import time
import argparse
import datetime
import yaml
import psutil
import pandas as pd
from pathlib import Path

from python.utils.logger import setup_logger
from python.generator.entities import EntityGenerator
from python.generator.transactions import TransactionGenerator
from python.generator.disputes_and_cases import OperationalEventsGenerator

logger = setup_logger("master_generator")

def run_generation(scale: str = "DEV", seed: int = 42, output_dir: str = "data/raw", config_path: str = "config/config.yaml"):
    """Orchestrates end-to-end synthetic dataset generation across all entities."""
    start_time = time.time()
    logger.info("======================================================================")
    logger.info("Starting PAYMENTIQ Synthetic Data Generation | Scale: %s | Seed: %d", scale, seed)
    logger.info("======================================================================")

    # Load configuration
    with open(config_path, "r") as f:
        config = yaml.safe_load(f)

    if scale not in config["scales"]:
        raise ValueError(f"Unknown scale '{scale}'. Available: {list(config['scales'].keys())}")

    scale_cfg = config["scales"][scale]
    n_transactions = scale_cfg["transactions"]
    n_customers = scale_cfg["customers"]
    n_merchants = scale_cfg["merchants"]
    start_date = datetime.date.fromisoformat(scale_cfg["start_date"])
    end_date = datetime.date.fromisoformat(scale_cfg["end_date"])
    chunk_size = config.get("chunk_size", 100000)

    raw_dir = Path(output_dir)
    raw_dir.mkdir(parents=True, exist_ok=True)
    ref_dir = Path("data/reference")
    ref_dir.mkdir(parents=True, exist_ok=True)

    # Step 1: Generate & Save Dimension Tables
    logger.info("--- Step 1: Generating Relational Dimensional Entities ---")
    entity_gen = EntityGenerator(seed=seed)
    entity_gen.generate_and_save_all(output_dir=str(ref_dir), n_customers=n_customers, n_merchants=n_merchants)

    # Step 2: Stream Transaction Chunks to Parquet
    logger.info("--- Step 2: Generating %d Transactions in Chunks of %d ---", n_transactions, chunk_size)
    tx_gen = TransactionGenerator(entities_dir=str(ref_dir), seed=seed)

    n_chunks = (n_transactions + chunk_size - 1) // chunk_size
    total_generated = 0
    total_gtv = 0.0
    total_approved = 0
    all_chunk_files = []
    
    # Keep track of a sample for disputes/cases generation
    sample_txs = []

    for i in range(n_chunks):
        rows_in_chunk = min(chunk_size, n_transactions - total_generated)
        logger.info("Generating transaction chunk %d/%d (%d rows)...", i + 1, n_chunks, rows_in_chunk)
        
        chunk_df = tx_gen.generate_chunk(n_rows=rows_in_chunk, start_date=start_date, end_date=end_date)
        
        chunk_filename = raw_dir / f"transactions_part_{i+1:03d}.parquet"
        chunk_df.to_parquet(chunk_filename, index=False)
        all_chunk_files.append(chunk_filename)

        total_generated += len(chunk_df)
        total_gtv += chunk_df["amount"].sum()
        total_approved += (chunk_df["auth_status"] == "Approved").sum()

        # Collect sample for operational events
        if len(sample_txs) < 200000:
            sample_txs.append(chunk_df)

        # Log memory usage
        process = psutil.Process()
        mem_mb = process.memory_info().rss / (1024 * 1024)
        logger.info("Chunk %d written. Current memory usage: %.1f MB", i + 1, mem_mb)

    # Step 3: Generate Disputes and Support Cases
    logger.info("--- Step 3: Generating Operational Disputes & Customer Support Cases ---")
    combined_sample = pd.concat(sample_txs, ignore_index=True)
    ops_gen = OperationalEventsGenerator(seed=seed)

    disputes_df = ops_gen.generate_disputes(combined_sample)
    disputes_path = raw_dir / "disputes.parquet"
    disputes_df.to_parquet(disputes_path, index=False)
    logger.info("Saved %d dispute records to %s", len(disputes_df), disputes_path)

    support_cases_df = ops_gen.generate_support_cases(combined_sample)
    cases_path = raw_dir / "support_cases.parquet"
    support_cases_df.to_parquet(cases_path, index=False)
    logger.info("Saved %d support case records to %s", len(support_cases_df), cases_path)

    # Step 4: Summary & Benchmark Report
    elapsed = time.time() - start_time
    auth_rate = (total_approved / total_generated) * 100.0 if total_generated > 0 else 0.0

    logger.info("======================================================================")
    logger.info("PAYMENTIQ Synthetic Data Generation Complete!")
    logger.info("Total Transactions Generated: %d", total_generated)
    logger.info("Total Gross Transaction Value (GTV): $%s", f"{total_gtv:,.2f}")
    logger.info("Overall Authorization Rate: %.2f%%", auth_rate)
    logger.info("Total Disputes Generated: %d", len(disputes_df))
    logger.info("Total Support Cases Generated: %d", len(support_cases_df))
    logger.info("Execution Time: %.2f seconds (%.0f rows/sec)", elapsed, total_generated / max(elapsed, 0.01))
    logger.info("======================================================================")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="PAYMENTIQ Synthetic Data Generator")
    parser.add_argument("--scale", type=str, default="DEV", choices=["DEV", "TEST", "FULL"], help="Scale tier")
    parser.add_argument("--seed", type=int, default=42, help="Random seed")
    parser.add_argument("--output", type=str, default="data/raw", help="Output directory")
    args = parser.parse_args()

    run_generation(scale=args.scale, seed=args.seed, output_dir=args.output)
