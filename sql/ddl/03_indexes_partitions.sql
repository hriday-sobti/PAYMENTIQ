-- ====================================================================
-- PAYMENTIQ PostgreSQL Performance Indexes & Partitioning
-- Author: PAYMENTIQ Analytics Engineering
-- Description: B-Tree and composite indexes optimized for analytical queries
-- ====================================================================

-- 1. High-selectivity composite indexes for analytical slicing
CREATE INDEX IF NOT EXISTS idx_fact_tx_merchant_date_status
ON core.fact_transactions (merchant_key, date_key, auth_status);

CREATE INDEX IF NOT EXISTS idx_fact_tx_customer_timestamp
ON core.fact_transactions (customer_key, timestamp);

CREATE INDEX IF NOT EXISTS idx_fact_tx_date_key
ON core.fact_transactions (date_key);

CREATE INDEX IF NOT EXISTS idx_fact_tx_payment_method
ON core.fact_transactions (payment_method_key);

-- 2. Partial indexes for fast operational and risk queries
CREATE INDEX IF NOT EXISTS idx_fact_tx_declines
ON core.fact_transactions (decline_code)
WHERE decline_code IS NOT NULL;

CREATE INDEX IF NOT EXISTS idx_fact_tx_chargebacks
ON core.fact_transactions (chargeback_flag)
WHERE chargeback_flag = TRUE;

CREATE INDEX IF NOT EXISTS idx_fact_tx_high_risk
ON core.fact_transactions (risk_score)
WHERE risk_score >= 600;

-- 3. Indexes on disputes and support cases
CREATE INDEX IF NOT EXISTS idx_fact_dsp_merchant
ON core.fact_disputes (merchant_key, dispute_date_key);

CREATE INDEX IF NOT EXISTS idx_fact_dsp_tx
ON core.fact_disputes (transaction_id);

CREATE INDEX IF NOT EXISTS idx_fact_cases_customer
ON core.fact_support_cases (customer_key, created_date_key);

CREATE INDEX IF NOT EXISTS idx_fact_cases_tx
ON core.fact_support_cases (transaction_id);
