"""
PAYMENTIQ Unified KPI Calculation Engine
Implements mathematically rigorous, cross-platform KPI calculations
conforming strictly to the contracts in config/kpi_definitions.yaml.
"""
import json
import time
import pandas as pd
import numpy as np
from pathlib import Path
from typing import Dict, Any, List

from python.utils.db import db_manager
from python.utils.logger import setup_logger

logger = setup_logger("kpi_engine")

class KPIEngine:
    """Standardized KPI calculator for platform-wide metrics."""

    def __init__(self, reports_dir: str = "reports"):
        self.reports_dir = Path(reports_dir)
        self.reports_dir.mkdir(parents=True, exist_ok=True)

    def calculate_global_kpis(self) -> Dict[str, Any]:
        """Calculates portfolio-wide global KPI values directly from core facts."""
        logger.info("Computing global portfolio KPIs...")
        ddb = db_manager.get_duckdb()

        query = """
            SELECT 
                COUNT(*) AS total_transaction_volume,
                COUNT(CASE WHEN auth_status = 'Approved' THEN 1 END) AS approved_volume,
                COUNT(CASE WHEN auth_status = 'Declined' THEN 1 END) AS declined_volume,
                COUNT(CASE WHEN auth_status = 'Failed' THEN 1 END) AS failed_volume,
                SUM(amount) AS gross_transaction_value,
                SUM(CASE WHEN auth_status = 'Approved' THEN amount ELSE 0 END) AS settled_transaction_value,
                SUM(CASE WHEN auth_status != 'Approved' THEN amount ELSE 0 END) AS transaction_value_at_risk,
                SUM(processing_fee) AS gross_revenue,
                SUM(interchange_fee) AS interchange_cost,
                SUM(scheme_fee) AS scheme_cost,
                SUM(net_revenue) AS net_revenue,
                SUM(net_contribution) AS net_contribution,
                SUM(CASE WHEN is_soft_decline THEN amount ELSE 0 END) AS soft_decline_gtv,
                COUNT(CASE WHEN refund_flag THEN 1 END) AS refund_count,
                SUM(CASE WHEN refund_flag THEN amount ELSE 0 END) AS refund_amount,
                COUNT(CASE WHEN chargeback_flag THEN 1 END) AS chargeback_count,
                SUM(CASE WHEN chargeback_flag THEN amount ELSE 0 END) AS chargeback_amount,
                AVG(latency_ms) AS avg_latency_ms
            FROM core.fact_transactions;
        """
        row = ddb.execute(query).fetchone()
        
        ttv = row[0]
        approved_vol = row[1]
        gtv = float(row[4])
        settled_gtv = float(row[5])
        tvar = float(row[6])
        gross_rev = float(row[7])
        ic_cost = float(row[8])
        scheme_cost = float(row[9])
        net_rev = float(row[10])
        net_contrib = float(row[11])
        soft_gtv = float(row[12])
        cb_count = row[15]
        
        # Calculate derived rate metrics
        auth_rate_pct = round(100.0 * approved_vol / max(ttv, 1), 2)
        decline_rate_pct = round(100.0 * row[2] / max(ttv, 1), 2)
        failure_rate_pct = round(100.0 * row[3] / max(ttv, 1), 2)
        net_take_rate_bps = round(10000.0 * net_rev / max(settled_gtv, 1), 1)
        contribution_margin_pct = round(100.0 * net_contrib / max(net_rev, 1), 2)
        chargeback_bps = round(10000.0 * cb_count / max(approved_vol, 1), 2)
        recoverable_leakage_est = round(soft_gtv * 0.025 * 0.45, 2)

        kpis = {
            "Total_Transaction_Volume": int(ttv),
            "Approved_Volume": int(approved_vol),
            "Gross_Transaction_Value": round(gtv, 2),
            "Settled_Transaction_Value": round(settled_gtv, 2),
            "Transaction_Value_at_Risk": round(tvar, 2),
            "Authorization_Rate_Pct": auth_rate_pct,
            "Decline_Rate_Pct": decline_rate_pct,
            "Failure_Rate_Pct": failure_rate_pct,
            "Gross_Revenue": round(gross_rev, 2),
            "Interchange_Cost": round(ic_cost, 2),
            "Scheme_Cost": round(scheme_cost, 2),
            "Net_Revenue": round(net_rev, 2),
            "Net_Take_Rate_BPS": net_take_rate_bps,
            "Net_Contribution": round(net_contrib, 2),
            "Contribution_Margin_Pct": contribution_margin_pct,
            "Recoverable_Leakage_Estimated": recoverable_leakage_est,
            "Chargeback_Count": int(cb_count),
            "Chargeback_Rate_BPS": chargeback_bps,
            "Average_Latency_MS": round(float(row[17]), 1)
        }
        return kpis

    def calculate_breakdowns(self) -> Dict[str, pd.DataFrame]:
        """Calculates dimensional KPI breakdowns."""
        ddb = db_manager.get_duckdb()
        breakdowns = {}

        # 1. By Payment Method
        q_pm = """
            SELECT 
                pm.method_name AS payment_method,
                COUNT(t.transaction_id) AS total_attempts,
                ROUND(100.0 * COUNT(CASE WHEN t.auth_status = 'Approved' THEN 1 END) / COUNT(*), 2) AS auth_rate_pct,
                ROUND(SUM(t.amount), 2) AS gtv,
                ROUND(SUM(CASE WHEN t.auth_status = 'Approved' THEN t.amount ELSE 0 END), 2) AS settled_gtv,
                ROUND(SUM(t.net_revenue), 2) AS net_revenue,
                ROUND(SUM(t.net_contribution), 2) AS net_contribution
            FROM core.fact_transactions t
            JOIN core.dim_payment_methods pm ON t.payment_method_key = pm.payment_method_key
            GROUP BY pm.method_name
            ORDER BY settled_gtv DESC;
        """
        breakdowns["by_payment_method"] = ddb.execute(q_pm).df()

        # 2. By Merchant Category
        q_mcc = """
            SELECT 
                m.merchant_category,
                COUNT(t.transaction_id) AS total_attempts,
                ROUND(100.0 * COUNT(CASE WHEN t.auth_status = 'Approved' THEN 1 END) / COUNT(*), 2) AS auth_rate_pct,
                ROUND(SUM(t.amount), 2) AS gtv,
                ROUND(SUM(CASE WHEN t.auth_status = 'Approved' THEN t.amount ELSE 0 END), 2) AS settled_gtv,
                ROUND(SUM(t.net_revenue), 2) AS net_revenue,
                ROUND(SUM(t.net_contribution), 2) AS net_contribution,
                COUNT(CASE WHEN t.chargeback_flag THEN 1 END) AS chargebacks
            FROM core.fact_transactions t
            JOIN core.dim_merchants m ON t.merchant_key = m.merchant_key
            GROUP BY m.merchant_category
            ORDER BY settled_gtv DESC;
        """
        breakdowns["by_merchant_category"] = ddb.execute(q_mcc).df()

        # 3. By Country
        q_geo = """
            SELECT 
                m.merchant_country,
                COUNT(t.transaction_id) AS total_attempts,
                ROUND(100.0 * COUNT(CASE WHEN t.auth_status = 'Approved' THEN 1 END) / COUNT(*), 2) AS auth_rate_pct,
                ROUND(SUM(t.amount), 2) AS gtv,
                ROUND(SUM(CASE WHEN t.auth_status = 'Approved' THEN t.amount ELSE 0 END), 2) AS settled_gtv,
                ROUND(SUM(t.net_revenue), 2) AS net_revenue
            FROM core.fact_transactions t
            JOIN core.dim_merchants m ON t.merchant_key = m.merchant_key
            GROUP BY m.merchant_country
            ORDER BY settled_gtv DESC;
        """
        breakdowns["by_country"] = ddb.execute(q_geo).df()

        return breakdowns

    def export_kpi_reports(self) -> Dict[str, Any]:
        """Calculates and exports global and dimensional KPI files."""
        start_time = time.time()
        logger.info("======================================================================")
        logger.info("Executing PAYMENTIQ Unified KPI Calculation Framework")
        logger.info("======================================================================")

        global_kpis = self.calculate_global_kpis()
        breakdowns = self.calculate_breakdowns()

        # Export JSON
        json_path = self.reports_dir / "kpi_summary.json"
        with open(json_path, "w") as f:
            json.dump(global_kpis, f, indent=2)
        logger.info("Saved global KPI metrics to %s", json_path)

        # Export CSVs
        for name, df in breakdowns.items():
            csv_path = self.reports_dir / f"kpi_{name}.csv"
            df.to_csv(csv_path, index=False)
            logger.info("Saved %s breakdown to %s", name, csv_path)

        elapsed = time.time() - start_time
        logger.info("======================================================================")
        logger.info("KPI Framework Calculation Completed in %.2f seconds", elapsed)
        logger.info("======================================================================")
        return global_kpis

if __name__ == "__main__":
    engine = KPIEngine()
    engine.export_kpi_reports()
