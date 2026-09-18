-- ====================================================================
-- PAYMENTIQ Analytical View: Payment Performance Intelligence
-- Author: PAYMENTIQ Analytics Engineering
-- Description: Multi-dimensional authorization funnels, decline rates,
--              and rolling window operational baselines
-- ====================================================================

CREATE SCHEMA IF NOT EXISTS analytics;

-- 1. Payment Performance by Payment Rail & Card Brand
CREATE OR REPLACE VIEW analytics.v_payment_performance_by_method AS
SELECT 
    pm.payment_method_id,
    pm.method_name,
    pm.card_brand,
    pm.card_type,
    COUNT(t.transaction_id) AS total_attempts,
    COUNT(CASE WHEN t.auth_status = 'Approved' THEN 1 END) AS approved_count,
    COUNT(CASE WHEN t.auth_status = 'Declined' THEN 1 END) AS declined_count,
    COUNT(CASE WHEN t.auth_status = 'Failed' THEN 1 END) AS failed_count,
    ROUND(100.0 * COUNT(CASE WHEN t.auth_status = 'Approved' THEN 1 END) / NULLIF(COUNT(*), 0), 2) AS auth_rate_pct,
    ROUND(100.0 * COUNT(CASE WHEN t.auth_status = 'Declined' THEN 1 END) / NULLIF(COUNT(*), 0), 2) AS decline_rate_pct,
    ROUND(100.0 * COUNT(CASE WHEN t.auth_status = 'Failed' THEN 1 END) / NULLIF(COUNT(*), 0), 2) AS failure_rate_pct,
    ROUND(SUM(t.amount)::numeric, 2) AS gross_transaction_value,
    ROUND(SUM(CASE WHEN t.auth_status = 'Approved' THEN t.amount ELSE 0 END)::numeric, 2) AS settled_transaction_value,
    ROUND(AVG(t.amount)::numeric, 2) AS avg_ticket_size,
    ROUND(AVG(t.latency_ms)::numeric, 1) AS avg_latency_ms,
    ROUND(SUM(t.processing_fee)::numeric, 2) AS gross_revenue,
    ROUND(SUM(t.net_revenue)::numeric, 2) AS net_revenue
FROM core.fact_transactions t
JOIN core.dim_payment_methods pm ON t.payment_method_key = pm.payment_method_key
GROUP BY pm.payment_method_id, pm.method_name, pm.card_brand, pm.card_type;

-- 2. Payment Performance by Merchant Category & 3DS Channel
CREATE OR REPLACE VIEW analytics.v_payment_performance_by_category AS
SELECT 
    m.mcc_code,
    m.merchant_category,
    t.channel,
    t.is_3ds_authenticated,
    COUNT(t.transaction_id) AS total_attempts,
    COUNT(CASE WHEN t.auth_status = 'Approved' THEN 1 END) AS approved_count,
    ROUND(100.0 * COUNT(CASE WHEN t.auth_status = 'Approved' THEN 1 END) / NULLIF(COUNT(*), 0), 2) AS auth_rate_pct,
    ROUND(SUM(t.amount)::numeric, 2) AS total_gtv,
    ROUND(SUM(CASE WHEN t.auth_status = 'Approved' THEN t.amount ELSE 0 END)::numeric, 2) AS settled_gtv,
    ROUND(AVG(t.latency_ms)::numeric, 1) AS avg_latency_ms
FROM core.fact_transactions t
JOIN core.dim_merchants m ON t.merchant_key = m.merchant_key
GROUP BY m.mcc_code, m.merchant_category, t.channel, t.is_3ds_authenticated;

-- 3. Daily Payment Performance with Rolling 7-Day & 30-Day Baselines
CREATE OR REPLACE VIEW analytics.v_daily_payment_trends AS
WITH daily_metrics AS (
    SELECT 
        d.date_key,
        d.full_date,
        d.year,
        d.month,
        d.day_name,
        d.is_weekend,
        COUNT(t.transaction_id) AS daily_attempts,
        COUNT(CASE WHEN t.auth_status = 'Approved' THEN 1 END) AS daily_approved,
        ROUND(SUM(t.amount)::numeric, 2) AS daily_gtv,
        ROUND(SUM(CASE WHEN t.auth_status = 'Approved' THEN t.amount ELSE 0 END)::numeric, 2) AS daily_settled_gtv,
        ROUND(SUM(t.net_revenue)::numeric, 2) AS daily_net_revenue,
        ROUND(AVG(t.latency_ms)::numeric, 1) AS daily_avg_latency_ms
    FROM core.dim_dates d
    LEFT JOIN core.fact_transactions t ON d.date_key = t.date_key
    WHERE d.year = 2024
    GROUP BY d.date_key, d.full_date, d.year, d.month, d.day_name, d.is_weekend
)
SELECT 
    full_date,
    date_key,
    day_name,
    is_weekend,
    daily_attempts,
    daily_approved,
    ROUND(100.0 * daily_approved / NULLIF(daily_attempts, 0), 2) AS daily_auth_rate_pct,
    daily_gtv,
    daily_settled_gtv,
    daily_net_revenue,
    daily_avg_latency_ms,
    -- 7-Day Rolling Average Authorization Rate
    ROUND(
        (AVG(100.0 * daily_approved / NULLIF(daily_attempts, 0)) 
        OVER (ORDER BY full_date ROWS BETWEEN 6 PRECEDING AND CURRENT ROW))::numeric, 
        2
    ) AS rolling_7d_auth_rate_pct,
    -- 30-Day Rolling Average Authorization Rate
    ROUND(
        (AVG(100.0 * daily_approved / NULLIF(daily_attempts, 0)) 
        OVER (ORDER BY full_date ROWS BETWEEN 29 PRECEDING AND CURRENT ROW))::numeric, 
        2
    ) AS rolling_30d_auth_rate_pct,
    -- 7-Day Rolling Sum Settled Volume
    ROUND(
        (SUM(daily_settled_gtv) 
        OVER (ORDER BY full_date ROWS BETWEEN 6 PRECEDING AND CURRENT ROW))::numeric, 
        2
    ) AS rolling_7d_settled_gtv
FROM daily_metrics;
