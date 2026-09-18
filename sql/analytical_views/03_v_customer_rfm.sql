-- ====================================================================
-- PAYMENTIQ Analytical View: Customer RFM Segmentation & Behavior
-- Author: PAYMENTIQ Analytics Engineering
-- Description: Quintile-based RFM scoring, behavioral segment assignment,
--              and customer lifetime value aggregates
-- ====================================================================

CREATE SCHEMA IF NOT EXISTS analytics;

-- 1. Base Customer Transaction Aggregates (Observation Window: 2024 Full Year)
CREATE OR REPLACE VIEW analytics.v_customer_rfm_scores AS
WITH customer_raw_metrics AS (
    SELECT 
        c.customer_key,
        c.customer_id,
        c.customer_country,
        c.customer_segment,
        c.acquisition_channel,
        c.risk_tier,
        -- Recency: Days between last transaction and year-end (2024-12-31)
        DATE_PART('day', '2024-12-31 23:59:59'::timestamp - MAX(t.timestamp)) AS recency_days,
        -- Frequency: Count of successfully approved transactions
        COUNT(CASE WHEN t.auth_status = 'Approved' THEN 1 END) AS frequency_count,
        -- Monetary Value: Total settled transaction amount
        ROUND(COALESCE(SUM(CASE WHEN t.auth_status = 'Approved' THEN t.amount ELSE 0 END), 0), 2) AS monetary_value,
        -- Net Contribution: Retained revenue minus chargebacks
        ROUND(COALESCE(SUM(t.net_contribution), 0), 2) AS historical_contribution,
        -- First & Last Transaction Dates
        MIN(t.timestamp)::date AS first_tx_date,
        MAX(t.timestamp)::date AS last_tx_date
    FROM core.dim_customers c
    JOIN core.fact_transactions t ON c.customer_key = t.customer_key
    GROUP BY c.customer_key, c.customer_id, c.customer_country, c.customer_segment, c.acquisition_channel, c.risk_tier
),
rfm_quintiles AS (
    SELECT 
        *,
        -- R_Score: Lower recency days = higher score (5 = most recent)
        NTILE(5) OVER (ORDER BY recency_days ASC) AS r_score,
        -- F_Score: Higher frequency = higher score (5 = most frequent)
        NTILE(5) OVER (ORDER BY frequency_count ASC) AS f_score,
        -- M_Score: Higher monetary value = higher score (5 = highest spend)
        NTILE(5) OVER (ORDER BY monetary_value ASC) AS m_score
    FROM customer_raw_metrics
)
SELECT 
    customer_key,
    customer_id,
    customer_country,
    customer_segment,
    acquisition_channel,
    risk_tier,
    recency_days,
    frequency_count,
    monetary_value,
    historical_contribution,
    first_tx_date,
    last_tx_date,
    r_score,
    f_score,
    m_score,
    (r_score::text || f_score::text || m_score::text) AS rfm_cell,
    -- Behavioral Segment Categorization Contract
    CASE 
        WHEN r_score >= 4 AND f_score >= 4 AND m_score >= 4 THEN 'Champions'
        WHEN r_score >= 3 AND f_score >= 3 AND m_score >= 3 THEN 'Loyal Customers'
        WHEN r_score >= 4 AND f_score <= 2 AND m_score >= 3 THEN 'Recent High Spenders'
        WHEN r_score >= 4 AND f_score <= 2 AND m_score <= 2 THEN 'New Active Customers'
        WHEN r_score <= 2 AND f_score >= 3 AND m_score >= 3 THEN 'At Risk / Churn Alert'
        WHEN r_score <= 2 AND f_score >= 4 AND m_score >= 4 THEN 'Can Not Lose Them'
        WHEN r_score <= 2 AND f_score <= 2 AND m_score <= 2 THEN 'Hibernating / Dormant'
        ELSE 'Standard Retail Active'
    END AS rfm_segment
FROM rfm_quintiles;

-- 2. RFM Segment Distribution & Value Concentration
CREATE OR REPLACE VIEW analytics.v_rfm_segment_summary AS
SELECT 
    rfm_segment,
    COUNT(customer_key) AS customer_count,
    ROUND(100.0 * COUNT(customer_key) / NULLIF(SUM(COUNT(customer_key)) OVER (), 0), 2) AS customer_share_pct,
    ROUND(AVG(recency_days)::numeric, 1) AS avg_recency_days,
    ROUND(AVG(frequency_count)::numeric, 1) AS avg_frequency,
    ROUND(AVG(monetary_value)::numeric, 2) AS avg_monetary_value,
    ROUND(SUM(monetary_value), 2) AS total_segment_gtv,
    ROUND(100.0 * SUM(monetary_value) / NULLIF(SUM(SUM(monetary_value)) OVER (), 0), 2) AS gtv_share_pct,
    ROUND(SUM(historical_contribution), 2) AS total_segment_contribution
FROM analytics.v_customer_rfm_scores
GROUP BY rfm_segment
ORDER BY total_segment_gtv DESC;
