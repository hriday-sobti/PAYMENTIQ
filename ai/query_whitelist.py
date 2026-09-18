"""
PAYMENTIQ Grounded Analytics Query Whitelist & Security Validator
Maintains pre-audited, parameterized analytical SQL queries and validates safety.
"""
import re
from typing import Dict, Any, Optional

QUERY_CATALOG: Dict[str, Dict[str, Any]] = {
    "AUTH_RATE_BY_METHOD": {
        "description": "Returns authorization rate and transaction counts by payment method rail",
        "sql": """
            SELECT 
                method_name,
                card_brand,
                total_attempts,
                approved_count,
                auth_rate_pct,
                avg_latency_ms
            FROM analytics.v_payment_performance_by_method
            ORDER BY auth_rate_pct DESC;
        """
    },
    "REVENUE_LEAKAGE_SUMMARY": {
        "description": "Returns overall transaction value at risk, soft decline leakage, and estimated recoverable revenue",
        "sql": """
            SELECT 
                gross_transaction_value,
                settled_gtv,
                total_transaction_value_at_risk,
                soft_decline_leakage_gtv,
                hard_decline_leakage_gtv,
                estimated_recoverable_net_revenue,
                direct_chargeback_losses
            FROM analytics.v_revenue_leakage_waterfall;
        """
    },
    "TOP_LEAKING_MERCHANTS": {
        "description": "Returns top merchants ranked by addressable soft decline leakage",
        "sql": """
            SELECT 
                merchant_name,
                merchant_category,
                auth_rate_pct,
                total_gtv,
                addressable_soft_decline_gtv,
                estimated_recoverable_revenue
            FROM analytics.v_merchant_leakage_ranking
            LIMIT 10;
        """
    },
    "RFM_SEGMENT_SUMMARY": {
        "description": "Returns customer distribution and monetary spend across RFM segments",
        "sql": """
            SELECT 
                rfm_segment,
                customer_count,
                customer_share_pct,
                avg_monetary_value,
                total_segment_gtv,
                gtv_share_pct
            FROM analytics.v_rfm_segment_summary
            ORDER BY total_segment_gtv DESC;
        """
    },
    "MERCHANT_QUADRANT_SUMMARY": {
        "description": "Returns merchant counts and volume by 4-Quadrant Opportunity Matrix",
        "sql": """
            SELECT 
                opportunity_quadrant,
                COUNT(*) AS merchant_count,
                ROUND(SUM(settled_gtv), 2) AS total_settled_gtv,
                ROUND(AVG(contribution_margin_pct), 2) AS avg_margin_pct,
                ROUND(AVG(dispute_rate_bps), 1) AS avg_dispute_bps
            FROM analytics.v_merchant_opportunity_matrix
            GROUP BY opportunity_quadrant
            ORDER BY total_settled_gtv DESC;
        """
    },
    "SUPPORT_SLA_SUMMARY": {
        "description": "Returns support ticket resolution times and SLA breach rates by category",
        "sql": """
            SELECT 
                ticket_category,
                total_cases,
                avg_resolution_time_mins,
                sla_breach_rate_pct,
                avg_csat_score
            FROM analytics.v_operational_support_metrics
            ORDER BY total_cases DESC;
        """
    },
    "GLOBAL_PORTFOLIO_TOTALS": {
        "description": "Returns core global totals: volume, GTV, settled volume, net revenue, net contribution",
        "sql": """
            SELECT 
                COUNT(*) AS total_transactions,
                ROUND(SUM(amount), 2) AS gtv,
                ROUND(SUM(CASE WHEN auth_status = 'Approved' THEN amount ELSE 0 END), 2) AS settled_gtv,
                ROUND(SUM(net_revenue), 2) AS net_revenue,
                ROUND(SUM(net_contribution), 2) AS net_contribution,
                ROUND(100.0 * COUNT(CASE WHEN auth_status = 'Approved' THEN 1 END) / COUNT(*), 2) AS auth_rate_pct
            FROM core.fact_transactions;
        """
    }
}

class SQLSafetyValidator:
    """Validates that candidate SQL queries are strictly read-only and non-destructive."""

    DANGEROUS_KEYWORDS = [
        r"\bDROP\b", r"\bDELETE\b", r"\bTRUNCATE\b", r"\bUPDATE\b",
        r"\bINSERT\b", r"\bALTER\b", r"\bCREATE\b", r"\bGRANT\b",
        r"\bREVOKE\b", r"\bEXEC\b", r"\bEXECUTE\b", r"--", r";.*--", r"/\*.*\*/"
    ]

    @classmethod
    def is_safe_query(cls, sql: str) -> tuple[bool, str]:
        """Checks for injection attacks, multiple statements, or modifying keywords."""
        cleaned = sql.strip()
        if not cleaned.upper().startswith("SELECT") and not cleaned.upper().startswith("WITH"):
            return False, "Query must begin with SELECT or WITH"

        # Check for dangerous keywords
        for pattern in cls.DANGEROUS_KEYWORDS:
            if re.search(pattern, cleaned, re.IGNORECASE):
                return False, f"Prohibited keyword pattern detected: {pattern}"

        # Prevent multiple semicolon-separated statements
        statements = [s for s in cleaned.split(";") if s.strip()]
        if len(statements) > 1:
            return False, "Multiple SQL statements are prohibited"

        return True, "Query verified safe"
