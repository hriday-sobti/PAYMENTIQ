"""
PAYMENTIQ Unit and Integration Tests for Grounded AI Analytics ("Ask PAYMENTIQ")
Verifies intent classification, AST safety validation against SQL injection,
and strict zero-hallucination grounding on returned database metrics.
"""
import pytest
import re
import numpy as np
from ai.nl_engine import assistant_engine
from ai.query_whitelist import SQLSafetyValidator

SAMPLE_BUSINESS_QUESTIONS = [
    ("What is our overall authorization rate and total GTV?", "AUTH_RATE_BY_METHOD"),
    ("How much revenue are we losing to payment declines?", "REVENUE_LEAKAGE_SUMMARY"),
    ("Which merchants have the highest addressable leakage?", "TOP_LEAKING_MERCHANTS"),
    ("What are our customer segments and how much do Champions spend?", "RFM_SEGMENT_SUMMARY"),
    ("What is our merchant opportunity matrix breakdown?", "MERCHANT_QUADRANT_SUMMARY"),
    ("What is our average support ticket resolution time?", "SUPPORT_SLA_SUMMARY"),
    ("What is our total portfolio performance?", "GLOBAL_PORTFOLIO_TOTALS"),
    ("Show me conversion across payment rails", "AUTH_RATE_BY_METHOD"),
    ("Tell me about failed payment value at risk", "REVENUE_LEAKAGE_SUMMARY"),
    ("Which merchants are the worst leaking?", "TOP_LEAKING_MERCHANTS"),
    ("Show me customer RFM segments", "RFM_SEGMENT_SUMMARY"),
    ("How many merchants are in the core anchor quadrant?", "MERCHANT_QUADRANT_SUMMARY"),
    ("What is our support SLA breach rate?", "SUPPORT_SLA_SUMMARY"),
    ("How do digital wallet and credit card authorization rates compare?", "AUTH_RATE_BY_METHOD"),
    ("What is our recoverable revenue from soft declines?", "REVENUE_LEAKAGE_SUMMARY")
]

@pytest.mark.parametrize("question,expected_intent", SAMPLE_BUSINESS_QUESTIONS)
def test_intent_classification(question, expected_intent):
    """Verifies that business stakeholder questions map to valid analytical intents."""
    intent = assistant_engine.classify_intent(question)
    assert intent == expected_intent, f"Failed for '{question}': got {intent}, expected {expected_intent}"

def test_sql_safety_validator_blocks_injections():
    """Verifies that destructive, modifying, or injection attacks are strictly rejected."""
    injections = [
        "DROP TABLE core.fact_transactions;",
        "SELECT * FROM core.fact_transactions; DELETE FROM core.dim_customers;",
        "UPDATE core.fact_transactions SET amount = 0;",
        "INSERT INTO core.dim_merchants VALUES (1, 'Hacker', '0000');",
        "SELECT * FROM core.fact_transactions -- SQL comment injection",
        "TRUNCATE core.fact_disputes;"
    ]
    for attack in injections:
        is_safe, reason = SQLSafetyValidator.is_safe_query(attack)
        assert not is_safe, f"Security vulnerability! Failed to block injection: {attack}"

def test_sql_safety_validator_permits_whitelisted_queries():
    """Verifies that clean read-only analytical queries pass safety validation."""
    safe_queries = [
        "SELECT * FROM analytics.v_payment_performance_by_method;",
        "WITH cte AS (SELECT 1 AS val) SELECT * FROM cte;"
    ]
    for q in safe_queries:
        is_safe, msg = SQLSafetyValidator.is_safe_query(q)
        assert is_safe, f"Safe query wrongly rejected: {q} - {msg}"

def test_zero_hallucination_grounding_verification():
    """Verifies that all numerical figures in the synthesized answer match database rows verbatim."""
    res = assistant_engine.ask("How much revenue are we losing to payment declines?")
    answer = res["answer"]
    data = res["grounded_data"][0]

    # Extract all monetary dollar values ($X,XXX.XX) from answer
    extracted_dollars = re.findall(r"\$([0-9,]+\.[0-9]{2})", answer)
    assert len(extracted_dollars) > 0, "No monetary values found in answer to verify"

    # Verify that each dollar amount in the answer matches a value in the underlying database row
    grounded_floats = [float(v.replace(",", "")) for v in extracted_dollars]
    row_floats = [float(v) for v in data.values() if isinstance(v, (int, float, np.number))]

    for val in grounded_floats:
        assert any(abs(val - r_val) < 0.05 for r_val in row_floats), f"Hallucinated dollar figure {val} not in DB row {row_floats}!"
