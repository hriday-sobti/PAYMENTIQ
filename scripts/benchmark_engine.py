"""
PAYMENTIQ Database Query Benchmark Utility
Benchmarks query execution latency between PostgreSQL 16 and DuckDB across standard analytical views.
"""
import time
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from sqlalchemy import text
from python.utils.db import db_manager
from python.utils.logger import setup_logger

logger = setup_logger("benchmark")

BENCHMARK_QUERIES = [
    ("Payment Performance by Method", "SELECT * FROM analytics.v_payment_performance_by_method;"),
    ("Revenue Leakage Waterfall", "SELECT * FROM analytics.v_revenue_leakage_waterfall;"),
    ("Customer RFM Segment Summary", "SELECT * FROM analytics.v_rfm_segment_summary;"),
    ("Merchant Opportunity Matrix", "SELECT * FROM analytics.v_merchant_opportunity_matrix;"),
    ("Operational Support Metrics", "SELECT * FROM analytics.v_operational_support_metrics;")
]

def run_benchmarks():
    print("\n" + "="*75)
    print(" PAYMENTIQ Database Query Execution Benchmark (PostgreSQL vs. DuckDB)")
    print("="*75 + "\n")

    pg_engine = db_manager.get_pg_engine()
    ddb = db_manager.get_duckdb()

    results = []

    for name, sql in BENCHMARK_QUERIES:
        # PostgreSQL timing (best of 3)
        pg_times = []
        with pg_engine.connect() as conn:
            for _ in range(3):
                t0 = time.perf_counter()
                conn.execute(text(sql)).fetchall()
                pg_times.append((time.perf_counter() - t0) * 1000.0)
        pg_best = min(pg_times)

        # DuckDB timing (best of 3)
        duck_times = []
        for _ in range(3):
            t0 = time.perf_counter()
            ddb.execute(sql).fetchall()
            duck_times.append((time.perf_counter() - t0) * 1000.0)
        duck_best = min(duck_times)

        speedup = pg_best / max(duck_best, 0.01)
        results.append({
            "Query": name,
            "PostgreSQL (ms)": f"{pg_best:.1f} ms",
            "DuckDB (ms)": f"{duck_best:.1f} ms",
            "DuckDB Speedup": f"{speedup:.1f}x"
        })

    # Print Formatted Table
    header = f"{'ANALYTICAL QUERY':<35} | {'POSTGRESQL':<15} | {'DUCKDB':<15} | {'ACCELERATION'}"
    print(header)
    print("-" * len(header))
    for r in results:
        print(f"{r['Query']:<35} | {r['PostgreSQL (ms)']:<15} | {r['DuckDB (ms)']:<15} | {r['DuckDB Speedup']}")
    print("="*75 + "\n")

if __name__ == "__main__":
    run_benchmarks()
