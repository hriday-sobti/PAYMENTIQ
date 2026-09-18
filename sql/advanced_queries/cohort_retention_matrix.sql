-- ====================================================================
-- PAYMENTIQ Advanced SQL: Customer Monthly Cohort Retention Matrix
-- Author: PAYMENTIQ Analytics Engineering
-- Description: Generates triangular cohort retention matrix tracking customer
--              activity retention rate by acquisition month across 12 months
-- ====================================================================

WITH customer_first_purchase AS (
    -- Identify acquisition month (first approved transaction month)
    SELECT 
        customer_key,
        DATE_TRUNC('month', MIN(timestamp))::date AS cohort_month
    FROM core.fact_transactions
    WHERE auth_status = 'Approved'
    GROUP BY customer_key
),
customer_monthly_activity AS (
    -- Identify all subsequent active transaction months per customer
    SELECT DISTINCT
        t.customer_key,
        DATE_TRUNC('month', t.timestamp)::date AS activity_month
    FROM core.fact_transactions t
    WHERE t.auth_status = 'Approved'
),
cohort_pairs AS (
    -- Calculate month index (0 to 11) between cohort month and activity month
    SELECT 
        c.cohort_month,
        a.activity_month,
        (EXTRACT(YEAR FROM a.activity_month) - EXTRACT(YEAR FROM c.cohort_month)) * 12 +
        (EXTRACT(MONTH FROM a.activity_month) - EXTRACT(MONTH FROM c.cohort_month)) AS month_number,
        COUNT(DISTINCT c.customer_key) AS active_customers
    FROM customer_first_purchase c
    JOIN customer_monthly_activity a ON c.customer_key = a.customer_key
    WHERE a.activity_month >= c.cohort_month
    GROUP BY c.cohort_month, a.activity_month
),
cohort_sizes AS (
    -- Size of cohort in Month 0
    SELECT 
        cohort_month,
        active_customers AS initial_cohort_size
    FROM cohort_pairs
    WHERE month_number = 0
)
SELECT 
    p.cohort_month,
    s.initial_cohort_size,
    p.month_number,
    p.active_customers,
    ROUND(100.0 * p.active_customers / NULLIF(s.initial_cohort_size, 0), 2) AS retention_rate_pct
FROM cohort_pairs p
JOIN cohort_sizes s ON p.cohort_month = s.cohort_month
ORDER BY p.cohort_month, p.month_number;
