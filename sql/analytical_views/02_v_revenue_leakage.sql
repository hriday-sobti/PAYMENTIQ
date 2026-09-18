-- ====================================================================
-- PAYMENTIQ Analytical View: Revenue Leakage Intelligence
-- Author: PAYMENTIQ Analytics Engineering
-- Description: Quantifies payment failure leakage, addressable recoverability,
--              chargeback loss provisions, and merchant leakage rankings
-- ====================================================================

CREATE SCHEMA IF NOT EXISTS analytics;

-- 1. Comprehensive Revenue Leakage Waterfall Summary
CREATE OR REPLACE VIEW analytics.v_revenue_leakage_waterfall AS
SELECT 
    COUNT(t.transaction_id) AS total_attempts,
    ROUND(SUM(t.amount), 2) AS gross_transaction_value,
    -- Settled vs. Declined Value
    ROUND(SUM(CASE WHEN t.auth_status = 'Approved' THEN t.amount ELSE 0 END), 2) AS settled_gtv,
    ROUND(SUM(CASE WHEN t.auth_status != 'Approved' THEN t.amount ELSE 0 END), 2) AS total_transaction_value_at_risk,
    -- Soft (Addressable) vs Hard (Structural) Declines
    ROUND(SUM(CASE WHEN dc.is_retryable THEN t.amount ELSE 0 END), 2) AS soft_decline_leakage_gtv,
    ROUND(SUM(CASE WHEN dc.is_retryable = FALSE AND t.auth_status != 'Approved' THEN t.amount ELSE 0 END), 2) AS hard_decline_leakage_gtv,
    -- Addressable Recoverable Revenue Estimation
    -- Formula: Soft Decline GTV * 2.5% Blended Net Take Rate * 45% Industry Smart Retry Yield
    ROUND(SUM(CASE WHEN dc.is_retryable THEN t.amount * 0.025 * 0.45 ELSE 0 END), 2) AS estimated_recoverable_net_revenue,
    -- Realized Chargeback Losses and Administrative Fees
    COUNT(d.dispute_id) AS total_disputes_count,
    ROUND(COALESCE(SUM(d.dispute_amount), 0), 2) AS direct_chargeback_losses,
    ROUND(COALESCE(SUM(d.chargeback_fee), 0), 2) AS dispute_assessment_fees,
    ROUND(COALESCE(SUM(d.dispute_amount + d.chargeback_fee), 0), 2) AS total_chargeback_burden
FROM core.fact_transactions t
LEFT JOIN core.dim_decline_codes dc ON t.decline_code = dc.decline_code
LEFT JOIN core.fact_disputes d ON t.transaction_id = d.transaction_id;

-- 2. Decline Code Root-Cause Leakage Breakdown
CREATE OR REPLACE VIEW analytics.v_decline_code_leakage AS
SELECT 
    COALESCE(dc.decline_code, 'UN') AS decline_code,
    COALESCE(dc.decline_reason, 'Unspecified Failure') AS decline_reason,
    COALESCE(dc.decline_type, 'Unknown') AS decline_type,
    COALESCE(dc.is_retryable, FALSE) AS is_retryable,
    dc.recommended_action,
    COUNT(t.transaction_id) AS decline_count,
    ROUND(SUM(t.amount), 2) AS total_declined_amount,
    ROUND(AVG(t.amount), 2) AS avg_declined_amount,
    -- Share of total declined value
    ROUND(100.0 * SUM(t.amount) / NULLIF(SUM(SUM(t.amount)) OVER (), 0), 2) AS pct_of_total_declined_value,
    -- Potential recoverable revenue
    ROUND(SUM(CASE WHEN dc.is_retryable THEN t.amount * 0.025 * 0.45 ELSE 0 END), 2) AS potential_recovered_revenue
FROM core.fact_transactions t
JOIN core.dim_decline_codes dc ON t.decline_code = dc.decline_code
WHERE t.auth_status != 'Approved'
GROUP BY dc.decline_code, dc.decline_reason, dc.decline_type, dc.is_retryable, dc.recommended_action
ORDER BY total_declined_amount DESC;

-- 3. Top 20 Leaking Merchants by Addressable Leakage
CREATE OR REPLACE VIEW analytics.v_merchant_leakage_ranking AS
SELECT 
    m.merchant_id,
    m.merchant_name,
    m.merchant_category,
    m.merchant_country,
    m.pricing_tier,
    COUNT(t.transaction_id) AS total_attempts,
    COUNT(CASE WHEN t.auth_status = 'Approved' THEN 1 END) AS approved_count,
    ROUND(100.0 * COUNT(CASE WHEN t.auth_status = 'Approved' THEN 1 END) / NULLIF(COUNT(*), 0), 2) AS auth_rate_pct,
    ROUND(SUM(t.amount), 2) AS total_gtv,
    ROUND(SUM(CASE WHEN t.auth_status != 'Approved' THEN t.amount ELSE 0 END), 2) AS total_tvar,
    ROUND(SUM(CASE WHEN dc.is_retryable THEN t.amount ELSE 0 END), 2) AS addressable_soft_decline_gtv,
    ROUND(SUM(CASE WHEN dc.is_retryable THEN t.amount * 0.025 * 0.45 ELSE 0 END), 2) AS estimated_recoverable_revenue,
    DENSE_RANK() OVER (ORDER BY SUM(CASE WHEN dc.is_retryable THEN t.amount ELSE 0 END) DESC) AS leakage_rank
FROM core.fact_transactions t
JOIN core.dim_merchants m ON t.merchant_key = m.merchant_key
LEFT JOIN core.dim_decline_codes dc ON t.decline_code = dc.decline_code
GROUP BY m.merchant_id, m.merchant_name, m.merchant_category, m.merchant_country, m.pricing_tier
ORDER BY addressable_soft_decline_gtv DESC;
