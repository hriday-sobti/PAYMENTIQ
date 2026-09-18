-- ====================================================================
-- PAYMENTIQ Analytical View: Operational SLA & System Latency Intelligence
-- Author: PAYMENTIQ Analytics Engineering
-- Description: Customer support ticket resolution performance, SLA compliance,
--              CSAT scores, and technical processing latency bottlenecks
-- ====================================================================

CREATE SCHEMA IF NOT EXISTS analytics;

-- 1. Support Ticket SLA & Operational Resolution Performance
CREATE OR REPLACE VIEW analytics.v_operational_support_metrics AS
SELECT 
    sc.category AS ticket_category,
    sc.severity,
    COUNT(sc.case_id) AS total_cases,
    COUNT(CASE WHEN sc.status = 'Resolved' THEN 1 END) AS resolved_count,
    COUNT(CASE WHEN sc.status = 'Escalated' THEN 1 END) AS escalated_count,
    COUNT(CASE WHEN sc.sla_breached_flag THEN 1 END) AS sla_breaches,
    ROUND(100.0 * COUNT(CASE WHEN sc.sla_breached_flag THEN 1 END) / NULLIF(COUNT(sc.case_id), 0), 2) AS sla_breach_rate_pct,
    ROUND(AVG(sc.resolution_time_minutes)::numeric, 1) AS avg_resolution_time_mins,
    ROUND(PERCENTILE_CONT(0.50) WITHIN GROUP (ORDER BY sc.resolution_time_minutes)::numeric, 1) AS median_resolution_time_mins,
    ROUND(PERCENTILE_CONT(0.95) WITHIN GROUP (ORDER BY sc.resolution_time_minutes)::numeric, 1) AS p95_resolution_time_mins,
    ROUND(AVG(sc.csat_score)::numeric, 2) AS avg_csat_score
FROM core.fact_support_cases sc
GROUP BY sc.category, sc.severity;

-- 2. Technical Processing Latency by Merchant Country & Channel
CREATE OR REPLACE VIEW analytics.v_technical_latency_summary AS
SELECT 
    m.merchant_country,
    t.channel,
    t.device_type,
    COUNT(t.transaction_id) AS tx_count,
    ROUND(AVG(t.latency_ms)::numeric, 1) AS avg_latency_ms,
    ROUND(PERCENTILE_CONT(0.50) WITHIN GROUP (ORDER BY t.latency_ms)::numeric, 1) AS median_latency_ms,
    ROUND(PERCENTILE_CONT(0.95) WITHIN GROUP (ORDER BY t.latency_ms)::numeric, 1) AS p95_latency_ms,
    ROUND(PERCENTILE_CONT(0.99) WITHIN GROUP (ORDER BY t.latency_ms)::numeric, 1) AS p99_latency_ms,
    COUNT(CASE WHEN t.latency_ms > 1000 THEN 1 END) AS high_latency_tx_count,
    ROUND(100.0 * COUNT(CASE WHEN t.latency_ms > 1000 THEN 1 END) / NULLIF(COUNT(t.transaction_id), 0), 2) AS high_latency_rate_pct
FROM core.fact_transactions t
JOIN core.dim_merchants m ON t.merchant_key = m.merchant_key
GROUP BY m.merchant_country, t.channel, t.device_type;
