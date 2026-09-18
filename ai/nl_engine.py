"""
PAYMENTIQ Grounded Natural-Language Analytics Engine
Parses business stakeholder questions, maps intents to verified SQL queries,
executes against the data warehouse, and synthesizes grounded executive explanations.
"""
import re
from typing import Dict, Any, List, Optional
import pandas as pd

from python.utils.db import db_manager
from python.utils.logger import setup_logger
from ai.query_whitelist import QUERY_CATALOG, SQLSafetyValidator

logger = setup_logger("nl_engine")

class GroundedAnalyticsEngine:
    """Grounded natural-language analytical assistant for PAYMENTIQ."""
    INTENT_PATTERNS = [
        (r"(top leaking|highest leakage|leaking merchant|worst merchant|merchants?.*leak|leak.*merchants?)", "TOP_LEAKING_MERCHANTS"),
        (r"\b(leakage|recoverable|lost|losing|value at risk|tvar|failed payment|declines?)\b", "REVENUE_LEAKAGE_SUMMARY"),
        (r"\b(auth rate|authorization rate|approval rate|payment method|rails?|wallets?|debits?|credits?|cards?|brands?|conversion)\b", "AUTH_RATE_BY_METHOD"),
        (r"\b(rfm|customer segments?|champions|loyals?|dormants?|clv|customer lifetime value|lifetime value)\b", "RFM_SEGMENT_SUMMARY"),
        (r"\b(merchant quadrants?|opportunity matrix|core anchors?|margin drag)\b", "MERCHANT_QUADRANT_SUMMARY"),
        (r"\b(supports?|tickets?|sla|resolution times?|csat)\b", "SUPPORT_SLA_SUMMARY"),
        (r"\b(total|portfolio|gtv|revenue|overall|summary|performance)\b", "GLOBAL_PORTFOLIO_TOTALS")
    ]

    def __init__(self):
        self.ddb = db_manager.get_duckdb()

    def classify_intent(self, question: str) -> str:
        """Matches user question against analytical intent patterns."""
        q_lower = question.lower()
        for pattern, intent in self.INTENT_PATTERNS:
            if re.search(pattern, q_lower):
                return intent
        return "GLOBAL_PORTFOLIO_TOTALS"

    def execute_query(self, query_id: str) -> pd.DataFrame:
        """Fetches and executes a whitelisted analytical query."""
        if query_id not in QUERY_CATALOG:
            raise ValueError(f"Unknown query ID: {query_id}")

        sql = QUERY_CATALOG[query_id]["sql"]
        is_safe, msg = SQLSafetyValidator.is_safe_query(sql)
        if not is_safe:
            raise PermissionError(f"SQL Safety Violation: {msg}")

        return self.ddb.execute(sql).df()

    def synthesize_response(self, question: str, intent: str, df: pd.DataFrame) -> Dict[str, Any]:
        """Synthesizes factual, grounded prose backed by exact returned data."""
        if df.empty:
            return {
                "question": question,
                "intent": intent,
                "answer": "No records matched your analytical criteria in the data warehouse.",
                "grounded_data": [],
                "source_query": QUERY_CATALOG[intent]["sql"]
            }

        # Format specific grounded explanations based on intent
        if intent == "GLOBAL_PORTFOLIO_TOTALS":
            row = df.iloc[0]
            answer = (
                f"In 2024, PAYMENTIQ processed {row['total_transactions']:,} total transaction attempts, "
                f"generating ${row['gtv']:,.2f} in Gross Transaction Value (GTV) and ${row['settled_gtv']:,.2f} "
                f"in settled volume. The platform achieved an overall authorization rate of {row['auth_rate_pct']:.2f}%, "
                f"delivering ${row['net_revenue']:,.2f} in retained Net Revenue and ${row['net_contribution']:,.2f} in Net Contribution."
            )
        elif intent == "AUTH_RATE_BY_METHOD":
            top_rail = df.iloc[0]
            lowest_rail = df.iloc[-1]
            answer = (
                f"Across payment rails, {top_rail['method_name']} achieved the highest conversion with an authorization rate of "
                f"{top_rail['auth_rate_pct']:.2f}% ({top_rail['approved_count']:,} approvals out of {top_rail['total_attempts']:,} attempts). "
                f"In contrast, {lowest_rail['method_name']} recorded the lowest conversion at {lowest_rail['auth_rate_pct']:.2f}%. "
                f"Average technical latency across all rails is {df['avg_latency_ms'].mean():.1f} ms."
            )
        elif intent == "REVENUE_LEAKAGE_SUMMARY":
            row = df.iloc[0]
            answer = (
                f"Total Transaction Value at Risk (TVaR) from declined and failed transactions stands at ${row['total_transaction_value_at_risk']:,.2f}. "
                f"Of this, soft retryable declines account for ${row['soft_decline_leakage_gtv']:,.2f}, representing an estimated "
                f"${row['estimated_recoverable_net_revenue']:,.2f} in recoverable net revenue opportunity. "
                f"Realized chargeback losses totaled ${row['direct_chargeback_losses']:,.2f}."
            )
        elif intent == "TOP_LEAKING_MERCHANTS":
            top_m = df.iloc[0]
            answer = (
                f"The highest addressable leakage is concentrated in {top_m['merchant_name']} ({top_m['merchant_category']}), "
                f"which experienced ${top_m['addressable_soft_decline_gtv']:,.2f} in soft decline leakage with an authorization rate of "
                f"{top_m['auth_rate_pct']:.2f}%. Implementing smart retry routing for this merchant could recover an estimated "
                f"${top_m['estimated_recoverable_revenue']:,.2f} in net revenue."
            )
        elif intent == "RFM_SEGMENT_SUMMARY":
            top_seg = df.iloc[0]
            answer = (
                f"The {top_seg['rfm_segment']} segment drives the largest share of transactional demand, contributing "
                f"${top_seg['total_segment_gtv']:,.2f} ({top_seg['gtv_share_pct']:.2f}% of portfolio volume) across "
                f"{top_seg['customer_count']:,} cardholders with an average spend of ${top_seg['avg_monetary_value']:,.2f}."
            )
        elif intent == "MERCHANT_QUADRANT_SUMMARY":
            top_q = df.iloc[0]
            answer = (
                f"In the 4-Quadrant Opportunity Matrix, {top_q['opportunity_quadrant']} represents {top_q['merchant_count']} merchants "
                f"generating ${top_q['total_settled_gtv']:,.2f} in settled volume with an average contribution margin of "
                f"{top_q['avg_margin_pct']:.2f}% and an average dispute rate of {top_q['avg_dispute_bps']:.1f} bps."
            )
        elif intent == "SUPPORT_SLA_SUMMARY":
            top_cat = df.iloc[0]
            answer = (
                f"The largest operational customer service driver is '{top_cat['ticket_category']}' with {top_cat['total_cases']:,} tickets. "
                f"The average resolution time is {top_cat['avg_resolution_time_mins']:.1f} minutes, with an SLA breach rate of "
                f"{top_cat['sla_breach_rate_pct']:.1f}% and an average CSAT score of {top_cat['avg_csat_score']:.2f} out of 5.0."
            )
        else:
            answer = f"Analytical query returned {len(df)} records for intent {intent}."

        return {
            "question": question,
            "intent": intent,
            "answer": answer,
            "grounded_data": df.head(10).to_dict(orient="records"),
            "source_query": QUERY_CATALOG[intent]["sql"].strip()
        }

    def ask(self, question: str) -> Dict[str, Any]:
        """End-to-end question answering pipeline."""
        intent = self.classify_intent(question)
        logger.info("Classified question intent: '%s' -> %s", question, intent)
        df = self.execute_query(intent)
        return self.synthesize_response(question, intent, df)

assistant_engine = GroundedAnalyticsEngine()
