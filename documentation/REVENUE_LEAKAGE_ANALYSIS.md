# PAYMENTIQ | Revenue Leakage & Value at Risk (TVaR) Analysis

**Analysis Scope:** 1,000,000 Payment Transaction Attempts (2024 Full Year)  
**Total Platform GTV:** $134,531,743.69  
**Total Transaction Value at Risk (TVaR):** $13,411,712.89 (9.97% of GTV)  

---

## 1. Executive Summary
This analysis evaluates financial leakage arising from transaction authorization failures, system timeouts, insufficient funds, and chargeback dispute write-offs. It distinguishes between unrecoverable hard declines and addressable soft declines that represent actionable revenue uplift opportunities.

---

## 2. Financial Leakage Waterfall & Opportunity Assessment

| Component | Monetary Value ($) | % of GTV | Recoverability / Strategic Action |
|---|---|---|---|
| **Gross Transaction Value (GTV)** | `$134,531,743.69` | 100.00% | Total attempted transactional checkout demand |
| **Settled Transaction Value (STV)** | `$121,120,030.80` | 90.03% | Captured volume converted to settled funds |
| **Total Value at Risk (TVaR)** | `$13,411,712.89` | 9.97% | Gross uncaptured transaction volume at checkout |
| **Soft Declines (Addressable)** | `$9,185,249.79` | 6.83% | **Highly Recoverable:** Insufficient funds, network timeout, issuer offline |
| **Hard Declines (Terminal)** | `$4,226,463.10` | 3.14% | **Unrecoverable:** Stolen cards, expired credentials, invalid accounts |
| **Estimated Recoverable Net Revenue** | **`$103,334.06`** | — | **Commercial Prize:** Net retained margin from smart retry logic |
| **Realized Chargeback Losses** | `$156,416.96` | 0.12% | Dispute reversals plus $20 assessment fees |

---

## 3. Merchant Category Leakage Concentration

| Merchant Category | Total GTV ($) | TVaR ($) | Soft Leakage ($) | Recoverable Revenue ($) | TVaR Rate (%) |
|---|---|---|---|---|---|
| Hotels & Travel | $36,780,895.11 | $4,154,277.77 | $2,794,100.34 | **$31,433.63** | 11.29% |
| Consumer Electronics | $27,510,670.54 | $2,860,252.90 | $1,996,968.92 | **$22,465.90** | 10.40% |
| Department Stores & Retail | $22,271,770.48 | $1,962,612.67 | $1,359,533.34 | **$15,294.75** | 8.81% |
| Airlines & Transit | $14,747,370.67 | $1,544,724.66 | $1,055,288.03 | **$11,871.99** | 10.47% |
| Restaurants & Dining | $11,213,489.60 | $963,156.03 | $665,777.31 | **$7,489.99** | 8.59% |
| Grocery & Supermarkets | $9,711,428.51 | $840,754.29 | $570,589.11 | **$6,419.13** | 8.66% |
| Apparel & Fashion | $8,732,897.15 | $768,484.08 | $520,361.46 | **$5,854.07** | 8.80% |
| Digital Goods & Gaming | $3,563,221.63 | $317,450.49 | $222,631.28 | **$2,504.60** | 8.91% |

---

## 4. Key Recommendations & Remediation Playbook

### Playbook 1: Dynamic Smart Retry Routing
- Implement automatic retry routing for Code `91` (Issuer System Unavailable) and Code `19` (Network Timeout) with a secondary card gateway within 400ms.
- Estimated recovery yield: **80% of technical timeouts**, capturing ~$1.2M in GTV.

### Playbook 2: Account Updater & Balance-Aware Retries
- For Code `51` (Insufficient Funds), schedule automated retries aligned with bi-weekly salary cycles (1st and 15th of the month) rather than immediate re-attempts.
- Estimated recovery yield: **35% of liquidity declines**, capturing ~$2.5M in GTV.
