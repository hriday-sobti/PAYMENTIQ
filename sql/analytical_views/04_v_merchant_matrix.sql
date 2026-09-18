-- ====================================================================
-- PAYMENTIQ Analytical View: Merchant Economics & Opportunity Matrix
-- Author: PAYMENTIQ Analytics Engineering
-- Description: Unit economics per merchant, dispute basis points,
--              contribution margins, and 4-Quadrant Opportunity Matrix
-- ====================================================================

CREATE SCHEMA IF NOT EXISTS analytics;

CREATE OR REPLACE VIEW analytics.v_merchant_opportunity_matrix AS
WITH merchant_base AS (
    SELECT 
        m.merchant_key,
        m.merchant_id,
        m.merchant_name,
        m.mcc_code,
        m.merchant_category,
        m.merchant_country,
        m.pricing_tier,
        m.acquirer_markup_bps,
        COUNT(t.transaction_id) AS total_attempts,
        COUNT(CASE WHEN t.auth_status = 'Approved' THEN 1 END) AS approved_count,
        ROUND(100.0 * COUNT(CASE WHEN t.auth_status = 'Approved' THEN 1 END) / NULLIF(COUNT(t.transaction_id), 0), 2) AS auth_rate_pct,
        ROUND(SUM(t.amount), 2) AS total_gtv,
        ROUND(SUM(CASE WHEN t.auth_status = 'Approved' THEN t.amount ELSE 0 END), 2) AS settled_gtv,
        ROUND(SUM(t.processing_fee), 2) AS gross_revenue,
        ROUND(SUM(t.interchange_fee + t.scheme_fee), 2) AS pass_through_costs,
        ROUND(SUM(t.net_revenue), 2) AS net_revenue,
        COUNT(CASE WHEN t.chargeback_flag THEN 1 END) AS dispute_count,
        ROUND(SUM(CASE WHEN t.chargeback_flag THEN t.amount + 20.0 ELSE 0 END), 2) AS chargeback_losses,
        ROUND(SUM(t.net_contribution), 2) AS net_contribution
    FROM core.dim_merchants m
    JOIN core.fact_transactions t ON m.merchant_key = t.merchant_key
    GROUP BY m.merchant_key, m.merchant_id, m.merchant_name, m.mcc_code, m.merchant_category, m.merchant_country, m.pricing_tier, m.acquirer_markup_bps
),
merchant_ratios AS (
    SELECT 
        *,
        -- Dispute rate in basis points (1 bp = 0.01%)
        ROUND(10000.0 * dispute_count / NULLIF(approved_count, 0), 1) AS dispute_rate_bps,
        -- Net Contribution Margin %
        ROUND(100.0 * net_contribution / NULLIF(net_revenue, 0), 2) AS contribution_margin_pct
    FROM merchant_base
),
portfolio_benchmarks AS (
    SELECT 
        PERCENTILE_CONT(0.50) WITHIN GROUP (ORDER BY settled_gtv) AS median_gtv,
        PERCENTILE_CONT(0.50) WITHIN GROUP (ORDER BY contribution_margin_pct) AS median_margin_pct
    FROM merchant_ratios
)
SELECT 
    r.merchant_key,
    r.merchant_id,
    r.merchant_name,
    r.mcc_code,
    r.merchant_category,
    r.merchant_country,
    r.pricing_tier,
    r.acquirer_markup_bps,
    r.total_attempts,
    r.approved_count,
    r.auth_rate_pct,
    r.total_gtv,
    r.settled_gtv,
    r.gross_revenue,
    r.pass_through_costs,
    r.net_revenue,
    r.dispute_count,
    r.dispute_rate_bps,
    r.chargeback_losses,
    r.net_contribution,
    r.contribution_margin_pct,
    -- 4-Quadrant Opportunity Matrix Categorization Contract
    CASE 
        WHEN r.dispute_rate_bps > 90.0 THEN 'High Risk / Scheme Monitoring'
        WHEN r.settled_gtv >= b.median_gtv AND r.contribution_margin_pct >= b.median_margin_pct THEN 'Core Anchor (Protect & Expand)'
        WHEN r.settled_gtv < b.median_gtv AND r.contribution_margin_pct >= b.median_margin_pct THEN 'Growth Prospect (Incentivize Scale)'
        WHEN r.settled_gtv >= b.median_gtv AND r.contribution_margin_pct < b.median_margin_pct THEN 'Margin Drag (Renegotiate Markup)'
        ELSE 'Review / Low Yield Portfolio'
    END AS opportunity_quadrant
FROM merchant_ratios r
CROSS JOIN portfolio_benchmarks b;
