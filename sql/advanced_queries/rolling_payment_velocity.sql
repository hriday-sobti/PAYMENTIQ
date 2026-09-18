-- ====================================================================
-- PAYMENTIQ Advanced SQL: Rolling Customer Payment Velocity & Surge Alerts
-- Author: PAYMENTIQ Analytics Engineering
-- Description: Computes rolling 7-day and 30-day transaction frequency and spend velocity
--              per cardholder to detect velocity anomalies and account takeover patterns
-- ====================================================================

WITH customer_tx_windows AS (
    SELECT 
        transaction_id,
        customer_key,
        timestamp,
        amount,
        auth_status,
        -- Rolling 24-hour transaction count
        COUNT(*) OVER (
            PARTITION BY customer_key 
            ORDER BY timestamp 
            RANGE BETWEEN INTERVAL '1 day' PRECEDING AND CURRENT ROW
        ) AS rolling_1d_tx_count,
        -- Rolling 7-day transaction count & spend
        COUNT(*) OVER (
            PARTITION BY customer_key 
            ORDER BY timestamp 
            RANGE BETWEEN INTERVAL '7 days' PRECEDING AND CURRENT ROW
        ) AS rolling_7d_tx_count,
        ROUND(SUM(amount) OVER (
            PARTITION BY customer_key 
            ORDER BY timestamp 
            RANGE BETWEEN INTERVAL '7 days' PRECEDING AND CURRENT ROW
        ), 2) AS rolling_7d_spend,
        -- Rolling 30-day transaction count & spend
        COUNT(*) OVER (
            PARTITION BY customer_key 
            ORDER BY timestamp 
            RANGE BETWEEN INTERVAL '30 days' PRECEDING AND CURRENT ROW
        ) AS rolling_30d_tx_count,
        ROUND(SUM(amount) OVER (
            PARTITION BY customer_key 
            ORDER BY timestamp 
            RANGE BETWEEN INTERVAL '30 days' PRECEDING AND CURRENT ROW
        ), 2) AS rolling_30d_spend,
        -- Historical average ticket size for this customer up to this transaction
        ROUND(AVG(amount) OVER (
            PARTITION BY customer_key 
            ORDER BY timestamp 
            ROWS BETWEEN UNBOUNDED PRECEDING AND 1 PRECEDING
        ), 2) AS prior_avg_amount
    FROM core.fact_transactions
)
SELECT 
    transaction_id,
    customer_key,
    timestamp,
    amount,
    auth_status,
    rolling_1d_tx_count,
    rolling_7d_tx_count,
    rolling_7d_spend,
    rolling_30d_tx_count,
    rolling_30d_spend,
    prior_avg_amount,
    -- Behavioral surge flags
    CASE 
        WHEN rolling_1d_tx_count >= 5 THEN 'Critical Frequency Velocity'
        WHEN rolling_1d_tx_count >= 3 THEN 'Elevated Frequency Velocity'
        WHEN amount > (prior_avg_amount * 4.0) AND prior_avg_amount IS NOT NULL THEN 'Ticket Size Surge (>4x Avg)'
        ELSE 'Normal Velocity'
    END AS velocity_alert_level
FROM customer_tx_windows;
