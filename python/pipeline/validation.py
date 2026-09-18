"""
PAYMENTIQ Automated Data Quality & Profiling Engine
Validates completeness, domain validity, uniqueness, financial consistency,
and referential integrity across all transactional and dimensional records.
"""
import json
import numpy as np
import pandas as pd
from pathlib import Path
from typing import Dict, Any, List, Tuple

from python.utils.logger import setup_logger

logger = setup_logger("data_validator")

class DataQualityValidator:
    """Comprehensive data quality assertion engine with structured audit reporting."""

    def __init__(self, raw_dir: str = "data/raw", ref_dir: str = "data/reference"):
        self.raw_dir = Path(raw_dir)
        self.ref_dir = Path(ref_dir)
        self.audit_results: Dict[str, Any] = {
            "validation_timestamp": pd.Timestamp.now().isoformat(),
            "status": "PASS",
            "checks": [],
            "profiling": {},
            "summary": {"total_checks": 0, "passed": 0, "failed": 0, "warnings": 0}
        }

    def _record_check(self, check_id: str, name: str, category: str, passed: bool, details: str, severity: str = "ERROR"):
        """Records an individual validation rule outcome."""
        self.audit_results["summary"]["total_checks"] += 1
        if passed:
            self.audit_results["summary"]["passed"] += 1
            status = "PASSED"
        else:
            if severity == "ERROR":
                self.audit_results["summary"]["failed"] += 1
                self.audit_results["status"] = "FAIL"
                status = "FAILED"
            else:
                self.audit_results["summary"]["warnings"] += 1
                status = "WARNING"

        logger.info("[%s] %s: %s - %s", status, check_id, name, details)
        self.audit_results["checks"].append({
            "check_id": check_id,
            "name": name,
            "category": category,
            "status": status,
            "severity": severity,
            "details": details
        })

    def run_all_checks(self) -> Dict[str, Any]:
        """Executes all data quality rules across dimensions, transactions, and disputes."""
        logger.info("======================================================================")
        logger.info("Executing PAYMENTIQ Data Quality & Integrity Validation Suite")
        logger.info("======================================================================")

        # Load reference dimensions
        cust_df = pd.read_parquet(self.ref_dir / "dim_customers.parquet")
        merch_df = pd.read_parquet(self.ref_dir / "dim_merchants.parquet")
        pm_df = pd.read_parquet(self.ref_dir / "dim_payment_methods.parquet")
        dec_df = pd.read_parquet(self.ref_dir / "dim_decline_codes.parquet")
        date_df = pd.read_parquet(self.ref_dir / "dim_dates.parquet")

        # Load transactions
        tx_files = sorted(list(self.raw_dir.glob("transactions_part_*.parquet")))
        if not tx_files:
            raise FileNotFoundError(f"No transaction partition files found in {self.raw_dir}")

        logger.info("Loading %d transaction partition files...", len(tx_files))
        tx_dfs = [pd.read_parquet(f) for f in tx_files]
        tx_df = pd.concat(tx_dfs, ignore_index=True)
        n_records = len(tx_df)
        logger.info("Loaded %d transaction records for validation", n_records)

        # -------------------------------------------------------------------
        # Rule Category 1: Completeness & Null Value Checks
        # -------------------------------------------------------------------
        mandatory_cols = [
            "transaction_id", "customer_key", "merchant_key", "date_key",
            "timestamp", "amount", "currency", "payment_method_key",
            "auth_status", "processing_fee", "interchange_fee", "scheme_fee"
        ]
        null_counts = tx_df[mandatory_cols].isnull().sum()
        has_nulls = (null_counts > 0).any()
        self._record_check(
            "DQ_01",
            "Mandatory Columns Nullness Check",
            "Completeness",
            not has_nulls,
            f"Zero nulls across mandatory columns: {dict(null_counts)}" if not has_nulls else f"Nulls found: {dict(null_counts[null_counts > 0])}"
        )

        # -------------------------------------------------------------------
        # Rule Category 2: Uniqueness Checks
        # -------------------------------------------------------------------
        n_unique_tx = tx_df["transaction_id"].nunique()
        is_unique_tx = (n_unique_tx == n_records)
        self._record_check(
            "DQ_02",
            "Transaction ID Primary Key Uniqueness",
            "Uniqueness",
            is_unique_tx,
            f"Distinct transaction IDs: {n_unique_tx} / {n_records} ({n_records - n_unique_tx} duplicates)"
        )

        # -------------------------------------------------------------------
        # Rule Category 3: Financial Consistency & Bounds Checks
        # -------------------------------------------------------------------
        # Positive amounts
        invalid_amounts = (tx_df["amount"] <= 0.0).sum()
        self._record_check(
            "DQ_03",
            "Transaction Amount Positivity ($ > 0.00)",
            "Financial Consistency",
            (invalid_amounts == 0),
            f"Non-positive amounts detected: {invalid_amounts}"
        )

        # Fee sanity (fees must be >= 0 and < amount)
        negative_fees = (
            (tx_df["processing_fee"] < 0) |
            (tx_df["interchange_fee"] < 0) |
            (tx_df["scheme_fee"] < 0)
        ).sum()
        self._record_check(
            "DQ_04",
            "Non-negative Fee Checks",
            "Financial Consistency",
            (negative_fees == 0),
            f"Negative fees detected: {negative_fees}"
        )

        excessive_fees = (tx_df["processing_fee"] >= tx_df["amount"]).sum()
        self._record_check(
            "DQ_05",
            "Processing Fee Less Than Transaction Amount",
            "Financial Consistency",
            (excessive_fees == 0),
            f"Processing fees exceeding transaction amount: {excessive_fees}"
        )

        # -------------------------------------------------------------------
        # Rule Category 4: Status & Decline Code Integrity
        # -------------------------------------------------------------------
        # Approved transactions must have NULL decline codes and reasons
        app_with_decline = (
            (tx_df["auth_status"] == "Approved") &
            (tx_df["decline_code"].notnull() | tx_df["decline_reason"].notnull())
        ).sum()
        self._record_check(
            "DQ_06",
            "Approved Transactions Decline Code Nullness",
            "Domain Validity",
            (app_with_decline == 0),
            f"Approved transactions with non-null decline codes: {app_with_decline}"
        )

        # Non-approved transactions must have valid decline codes
        declined_no_code = (
            (tx_df["auth_status"] != "Approved") &
            (tx_df["decline_code"].isnull() | tx_df["decline_reason"].isnull())
        ).sum()
        self._record_check(
            "DQ_07",
            "Declined Transactions Must Possess Valid Decline Codes",
            "Domain Validity",
            (declined_no_code == 0),
            f"Declined transactions missing decline codes: {declined_no_code}"
        )

        # -------------------------------------------------------------------
        # Rule Category 5: Referential Integrity Checks
        # -------------------------------------------------------------------
        valid_cust_keys = set(cust_df["customer_key"])
        orphaned_cust = (~tx_df["customer_key"].isin(valid_cust_keys)).sum()
        self._record_check(
            "DQ_08",
            "Customer Foreign Key Referential Integrity",
            "Referential Integrity",
            (orphaned_cust == 0),
            f"Transactions with invalid customer_key: {orphaned_cust}"
        )

        valid_merch_keys = set(merch_df["merchant_key"])
        orphaned_merch = (~tx_df["merchant_key"].isin(valid_merch_keys)).sum()
        self._record_check(
            "DQ_09",
            "Merchant Foreign Key Referential Integrity",
            "Referential Integrity",
            (orphaned_merch == 0),
            f"Transactions with invalid merchant_key: {orphaned_merch}"
        )

        valid_pm_keys = set(pm_df["payment_method_key"])
        orphaned_pm = (~tx_df["payment_method_key"].isin(valid_pm_keys)).sum()
        self._record_check(
            "DQ_10",
            "Payment Method Foreign Key Referential Integrity",
            "Referential Integrity",
            (orphaned_pm == 0),
            f"Transactions with invalid payment_method_key: {orphaned_pm}"
        )

        valid_date_keys = set(date_df["date_key"])
        orphaned_dates = (~tx_df["date_key"].isin(valid_date_keys)).sum()
        self._record_check(
            "DQ_11",
            "Calendar Date Foreign Key Referential Integrity",
            "Referential Integrity",
            (orphaned_dates == 0),
            f"Transactions with invalid date_key: {orphaned_dates}"
        )

        # -------------------------------------------------------------------
        # Rule Category 6: Disputes & Support Cases Referential Integrity
        # -------------------------------------------------------------------
        valid_tx_ids = set(tx_df["transaction_id"])
        
        disputes_file = self.raw_dir / "disputes.parquet"
        if disputes_file.exists():
            dsp_df = pd.read_parquet(disputes_file)
            orphaned_dsp = (~dsp_df["transaction_id"].isin(valid_tx_ids)).sum()
            self._record_check(
                "DQ_12",
                "Dispute Transaction ID Referential Integrity",
                "Referential Integrity",
                (orphaned_dsp == 0),
                f"Disputes referencing non-existent transaction IDs: {orphaned_dsp}"
            )

        cases_file = self.raw_dir / "support_cases.parquet"
        if cases_file.exists():
            cases_df = pd.read_parquet(cases_file)
            orphaned_cases = (~cases_df["transaction_id"].isin(valid_tx_ids)).sum()
            self._record_check(
                "DQ_13",
                "Support Cases Transaction ID Referential Integrity",
                "Referential Integrity",
                (orphaned_cases == 0),
                f"Support cases referencing non-existent transaction IDs: {orphaned_cases}"
            )

        # -------------------------------------------------------------------
        # Comprehensive Data Profiling Metrics
        # -------------------------------------------------------------------
        amt = tx_df["amount"]
        lat = tx_df["latency_ms"]
        self.audit_results["profiling"] = {
            "total_records": int(n_records),
            "total_gtv": float(amt.sum()),
            "mean_amount": float(amt.mean()),
            "median_amount": float(amt.median()),
            "p25_amount": float(amt.quantile(0.25)),
            "p75_amount": float(amt.quantile(0.75)),
            "p95_amount": float(amt.quantile(0.95)),
            "p99_amount": float(amt.quantile(0.99)),
            "max_amount": float(amt.max()),
            "amount_skewness": float(amt.skew()),
            "mean_latency_ms": float(lat.mean()),
            "median_latency_ms": float(lat.median()),
            "p95_latency_ms": float(lat.quantile(0.95)),
            "auth_rate_pct": float(100.0 * (tx_df["auth_status"] == "Approved").mean()),
            "refund_rate_pct": float(100.0 * tx_df["refund_flag"].mean()),
            "chargeback_rate_pct": float(100.0 * tx_df["chargeback_flag"].mean()),
            "fraud_rate_pct": float(100.0 * tx_df["fraud_flag"].mean()),
            "status_distribution": tx_df["auth_status"].value_counts().to_dict(),
            "channel_distribution": tx_df["channel"].value_counts().to_dict()
        }

        # Save JSON audit report
        reports_dir = Path("reports")
        reports_dir.mkdir(parents=True, exist_ok=True)
        json_path = reports_dir / "data_quality_report.json"
        with open(json_path, "w") as f:
            json.dump(self.audit_results, f, indent=2)
        logger.info("Saved structured audit report to %s", json_path)

        # Save Markdown documentation
        doc_path = Path("documentation/DATA_QUALITY_REPORT.md")
        self._write_markdown_report(doc_path)
        logger.info("Saved Markdown documentation report to %s", doc_path)

        logger.info("======================================================================")
        logger.info(
            "Validation Completed: %d/%d Checks Passed (Status: %s)",
            self.audit_results["summary"]["passed"],
            self.audit_results["summary"]["total_checks"],
            self.audit_results["status"]
        )
        logger.info("======================================================================")
        return self.audit_results

    def _write_markdown_report(self, filepath: Path):
        """Generates clean Markdown documentation of data quality validation results."""
        p = self.audit_results["profiling"]
        s = self.audit_results["summary"]

        md_content = f"""# PAYMENTIQ | Data Quality & Integrity Validation Report

**Execution Timestamp:** {self.audit_results["validation_timestamp"]}  
**Overall Validation Status:** **{self.audit_results["status"]}**  
**Checks Passed:** {s["passed"]} / {s["total_checks"]} ({100.0 * s["passed"] / max(s["total_checks"], 1):.1f}%)  

---

## 1. Executive Summary
The automated data quality engine evaluated all dimensional, transactional, and dispute records against 13 enterprise data quality rules across completeness, uniqueness, domain validity, financial consistency, and referential integrity.

---

## 2. Rule Execution Results Table

| Check ID | Rule Name | Category | Severity | Status | Details |
|---|---|---|---|---|---|
"""
        for c in self.audit_results["checks"]:
            md_content += f"| `{c['check_id']}` | {c['name']} | {c['category']} | {c['severity']} | **{c['status']}** | {c['details']} |\n"

        md_content += f"""
---

## 3. Dataset Statistical Profiling Summary

- **Total Transactions Validated:** {p['total_records']:,}
- **Total Gross Transaction Value (GTV):** ${p['total_gtv']:,.2f}
- **Mean Transaction Amount:** ${p['mean_amount']:.2f}
- **Median Transaction Amount:** ${p['median_amount']:.2f}
- **75th Percentile Amount:** ${p['p75_amount']:.2f}
- **95th Percentile Amount:** ${p['p95_amount']:.2f}
- **99th Percentile Amount:** ${p['p99_amount']:.2f}
- **Maximum Transaction Amount:** ${p['max_amount']:,.2f}
- **Amount Distribution Skewness:** {p['amount_skewness']:.2f} (positive right skew as expected for commercial transactions)
- **Mean Processing Latency:** {p['mean_latency_ms']:.1f} ms
- **95th Percentile Latency:** {p['p95_latency_ms']:.1f} ms
- **Authorization Rate:** {p['auth_rate_pct']:.2f}%
- **Refund Rate:** {p['refund_rate_pct']:.2f}%
- **Chargeback Rate:** {p['chargeback_rate_pct']:.4f}%
- **Latent Fraud Rate:** {p['fraud_rate_pct']:.4f}%

---

## 4. Status Breakdown
"""
        for status, count in p["status_distribution"].items():
            pct = 100.0 * count / p["total_records"]
            md_content += f"- **{status}:** {count:,} ({pct:.2f}%)\n"

        filepath.parent.mkdir(parents=True, exist_ok=True)
        with open(filepath, "w") as f:
            f.write(md_content)

if __name__ == "__main__":
    validator = DataQualityValidator()
    validator.run_all_checks()
