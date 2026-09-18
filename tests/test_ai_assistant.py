"""
PAYMENTIQ Unit and Integration Tests for Grounded AI Analytics ("Ask PAYMENTIQ")
Verifies intent classification across diverse business queries, AST safety validation
against SQL injection attack vectors, and strict zero-hallucination grounding on returned database metrics.
"""
import pytest
import re
import numpy as np
from ai.nl_engine import assistant_engine
from ai.query_whitelist import SQLSafetyValidator, QUERY_CATALOG

SAMPLE_BUSINESS_QUESTIONS = [
    # Intent 1: AUTH_RATE_BY_METHOD
    ("What is our overall authorization rate and total GTV?", "AUTH_RATE_BY_METHOD"),
    ("Show me conversion across payment rails", "AUTH_RATE_BY_METHOD"),
    ("How do digital wallet and credit card authorization rates compare?", "AUTH_RATE_BY_METHOD"),
    ("Which payment method has the highest approval rate?", "AUTH_RATE_BY_METHOD"),
    ("What is the debit card conversion rate?", "AUTH_RATE_BY_METHOD"),
    ("Tell me about card brand performance", "AUTH_RATE_BY_METHOD"),

    # Intent 2: REVENUE_LEAKAGE_SUMMARY
    ("How much revenue are we losing to payment declines?", "REVENUE_LEAKAGE_SUMMARY"),
    ("Tell me about failed payment value at risk", "REVENUE_LEAKAGE_SUMMARY"),
    ("What is our recoverable revenue from soft declines?", "REVENUE_LEAKAGE_SUMMARY"),
    ("What is our total transaction value at risk?", "REVENUE_LEAKAGE_SUMMARY"),
    ("How much money is lost to technical timeouts and insufficient funds?", "REVENUE_LEAKAGE_SUMMARY"),
    ("How much is lost to chargebacks?", "REVENUE_LEAKAGE_SUMMARY"),

    # Intent 3: TOP_LEAKING_MERCHANTS
    ("Which merchants have the highest addressable leakage?", "TOP_LEAKING_MERCHANTS"),
    ("Which merchants are the worst leaking?", "TOP_LEAKING_MERCHANTS"),
    ("Show me the top leaking merchants by declined volume", "TOP_LEAKING_MERCHANTS"),
    ("Who are the highest leakage sellers?", "TOP_LEAKING_MERCHANTS"),

    # Intent 4: RFM_SEGMENT_SUMMARY
    ("What are our customer segments and how much do Champions spend?", "RFM_SEGMENT_SUMMARY"),
    ("Show me customer RFM segments", "RFM_SEGMENT_SUMMARY"),
    ("How much spend comes from loyal customers?", "RFM_SEGMENT_SUMMARY"),
    ("What is the customer distribution across dormant and active cohorts?", "RFM_SEGMENT_SUMMARY"),
    ("Tell me about customer lifetime value by segment", "RFM_SEGMENT_SUMMARY"),

    # Intent 5: MERCHANT_QUADRANT_SUMMARY
    ("What is our merchant opportunity matrix breakdown?", "MERCHANT_QUADRANT_SUMMARY"),
    ("How many merchants are in the core anchor quadrant?", "MERCHANT_QUADRANT_SUMMARY"),
    ("Which merchants represent margin drag?", "MERCHANT_QUADRANT_SUMMARY"),
    ("Show me merchant quadrant distribution", "MERCHANT_QUADRANT_SUMMARY"),

    # Intent 6: SUPPORT_SLA_SUMMARY
    ("What is our average support ticket resolution time?", "SUPPORT_SLA_SUMMARY"),
    ("What is our support SLA breach rate?", "SUPPORT_SLA_SUMMARY"),
    ("Which support ticket category has the highest volume?", "SUPPORT_SLA_SUMMARY"),
    ("What are customer satisfaction csat scores for support?", "SUPPORT_SLA_SUMMARY"),

    # Intent 7: GLOBAL_PORTFOLIO_TOTALS
    ("What is our total portfolio performance?", "GLOBAL_PORTFOLIO_TOTALS"),
    ("Give me the overall summary of 2024 financials", "GLOBAL_PORTFOLIO_TOTALS"),
    ("What is our total platform volume and net contribution?", "GLOBAL_PORTFOLIO_TOTALS")
]

@pytest.mark.parametrize("question,expected_intent", SAMPLE_BUSINESS_QUESTIONS)
def test_intent_classification(question, expected_intent):
    """Verifies that diverse stakeholder questions map to valid analytical intents."""
    intent = assistant_engine.classify_intent(question)
    assert intent == expected_intent, f"Failed for '{question}': got {intent}, expected {expected_intent}"

# --- Security & SQL Injection Protection Tests ---

SQL_INJECTION_VECTORS = [
    "DROP TABLE core.fact_transactions;",
    "SELECT * FROM core.fact_transactions; DELETE FROM core.dim_customers;",
    "UPDATE core.fact_transactions SET amount = 0;",
    "INSERT INTO core.dim_merchants VALUES (1, 'Hacker', '0000');",
    "SELECT * FROM core.fact_transactions -- SQL comment injection",
    "TRUNCATE core.fact_disputes;",
    "ALTER TABLE core.fact_transactions ADD COLUMN backdoor VARCHAR(10);",
    "GRANT ALL PRIVILEGES ON DATABASE paymentiq_dw TO public;",
    "REVOKE ALL ON core.fact_transactions FROM postgres;",
    "EXEC xp_cmdshell('dir');",
    "EXECUTE immediate 'DROP SCHEMA core CASCADE';",
    "SELECT * FROM core.fact_transactions; SELECT * FROM core.dim_merchants;"
]

@pytest.mark.parametrize("attack_vector", SQL_INJECTION_VECTORS)
def test_sql_safety_validator_blocks_injections(attack_vector):
    """Security Rule: Must block all modifying, destructive, or multi-statement injections."""
    is_safe, reason = SQLSafetyValidator.is_safe_query(attack_vector)
    assert not is_safe, f"Security vulnerability! Failed to block injection: {attack_vector}"

def test_sql_safety_validator_permits_whitelisted_queries():
    """Verifies that clean read-only analytical queries pass safety validation."""
    safe_queries = [
        "SELECT * FROM analytics.v_payment_performance_by_method;",
        "SELECT merchant_name, settled_gtv FROM core.dim_merchants;",
        "WITH cte AS (SELECT 1 AS val) SELECT * FROM cte;"
    ]
    for q in safe_queries:
        is_safe, msg = SQLSafetyValidator.is_safe_query(q)
        assert is_safe, f"Safe query wrongly rejected: {q} - {msg}"

# --- Zero-Hallucination Metric Grounding Tests ---

QUERY_INTENTS = list(QUERY_CATALOG.keys())

@pytest.mark.parametrize("intent", QUERY_INTENTS)
def test_intent_query_execution_and_grounding(intent):
    """Rule: Every whitelisted query must execute and return populated ground truth."""
    df = assistant_engine.execute_query(intent)
    assert len(df) > 0, f"Query for intent {intent} returned empty result!"
    res = assistant_engine.synthesize_response("Verification check", intent, df)
    assert len(res["answer"]) > 15
    assert len(res["grounded_data"]) > 0

def test_zero_hallucination_numeric_exact_match():
    """Rule: All monetary values in the AI answer must exist verbatim in the underlying database record."""
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
