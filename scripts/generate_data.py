"""
PAYMENTIQ Data Generation CLI Shortcut
Usage:
    python scripts/generate_data.py --scale DEV
    python scripts/generate_data.py --scale TEST
    python scripts/generate_data.py --scale FULL
"""
import sys
import argparse
from pathlib import Path

# Add project root to sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from python.generator.generator import run_generation

def main():
    parser = argparse.ArgumentParser(description="PAYMENTIQ Synthetic Data Generator")
    parser.add_argument("--scale", type=str, default="DEV", choices=["DEV", "TEST", "FULL"], help="Scale tier (DEV: 100K, TEST: 1M, FULL: 5M+)")
    parser.add_argument("--seed", type=int, default=42, help="Deterministic random seed")
    parser.add_argument("--output", type=str, default="data/raw", help="Output directory")
    args = parser.parse_args()

    run_generation(scale=args.scale, seed=args.seed, output_dir=args.output)

if __name__ == "__main__":
    main()
