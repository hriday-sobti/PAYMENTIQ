-- ====================================================================
-- PAYMENTIQ Advanced SQL: Merchant Portfolio Pareto & Concentration Analysis
-- Author: PAYMENTIQ Analytics Engineering
-- Description: Measures GTV and Net Contribution concentration using cumulative
--              window functions to identify 80/20 commercial dependencies
-- ====================================================================

WITH merchant_totals AS (
    SELECT 
        m.merchant_key,
        m.merchant_id,
        m.merchant_name,
        m.merchant_category,
        m.pricing_tier,
        COUNT(t.transaction_id) AS total_attempts,
        ROUND(SUM(CASE WHEN t.auth_status = 'Approved' THEN t.amount ELSE 0 END), 2) AS settled_gtv,
        ROUND(SUM(t.net_contribution), 2) AS total_contribution
    FROM core.dim_merchants m
    JOIN core.fact_transactions t ON m.merchant_key = t.merchant_key
    GROUP BY m.merchant_key, m.merchant_id, m.merchant_name, m.merchant_category, m.pricing_tier
),
ranked_merchants AS (
    SELECT 
        *,
        ROW_NUMBER() OVER (ORDER BY settled_gtv DESC) AS volume_rank,
        -- Cumulative running totals
        SUM(settled_gtv) OVER (ORDER BY settled_gtv DESC ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW) AS running_gtv,
        SUM(settled_gtv) OVER () AS total_portfolio_gtv,
        SUM(total_contribution) OVER (ORDER BY settled_gtv DESC ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW) AS running_contribution,
        SUM(total_contribution) OVER () AS total_portfolio_contribution,
        COUNT(*) OVER () AS total_merchants_count
    FROM merchant_totals
)
SELECT 
    merchant_id,
    merchant_name,
    merchant_category,
    pricing_tier,
    volume_rank,
    settled_gtv,
    total_contribution,
    ROUND(100.0 * volume_rank / total_merchants_count, 2) AS merchant_percentile,
    ROUND(100.0 * running_gtv / NULLIF(total_portfolio_gtv, 0), 2) AS cumulative_gtv_pct,
    ROUND(100.0 * running_contribution / NULLIF(total_portfolio_contribution, 0), 2) AS cumulative_contribution_pct,
    -- ABC Pareto Classification Contract
    CASE 
        WHEN (100.0 * running_gtv / NULLIF(total_portfolio_gtv, 0)) <= 70.0 THEN 'Tier A: Top 70% Volume (Core Focus)'
        WHEN (100.0 * running_gtv / NULLIF(total_portfolio_gtv, 0)) <= 90.0 THEN 'Tier B: Next 20% Volume (Mid-Tier)'
        ELSE 'Tier C: Long Tail 10% (Automated Support)'
    END AS pareto_class
FROM ranked_merchants
ORDER BY volume_rank;
