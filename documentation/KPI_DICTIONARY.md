# PAYMENTIQ | Enterprise KPI Catalog & Metric Dictionary

**Document Version:** 1.0.0  
**Authority:** PAYMENTIQ Analytics Engineering & Financial Governance  
**Purpose:** Single source of truth for metric definitions across SQL, Python, Power BI DAX, and Executive Reports.  

---

## 1. Metric Catalog Summary Table

| KPI ID | KPI Name | Mathematical Formula | Business Grain | SQL Implementation | Power BI DAX Implementation |
|---|---|---|---|---|---|
| **KPI_01** | Gross Transaction Value (GTV) | $\sum \text{Amount}$ | One attempt | `SUM(amount)` | `SUM(fact_transactions[amount])` |
| **KPI_02** | Settled Transaction Value (STV) | $\sum (\text{Amount} \times \mathbb{I}_{\text{Approved}})$ | One attempt | `SUM(CASE WHEN auth_status = 'Approved' THEN amount ELSE 0 END)` | `CALCULATE(SUM(fact_transactions[amount]), fact_transactions[auth_status] = "Approved")` |
| **KPI_03** | Total Transaction Volume (TTV) | $\sum 1$ | One attempt | `COUNT(*)` | `COUNTROWS(fact_transactions)` |
| **KPI_04** | Authorization Rate % | $\frac{\text{Approved Count}}{\text{Total Attempts}} \times 100\%$ | Portfolio / Segment | `100.0 * COUNT(CASE WHEN auth_status = 'Approved' THEN 1 END) / COUNT(*)` | `DIVIDE([Approved Transactions], [Total Transactions], 0)` |
| **KPI_05** | Gross Revenue (MDR) | $\sum \text{Processing Fee}$ | Settled transaction | `SUM(processing_fee)` | `SUM(fact_transactions[processing_fee])` |
| **KPI_06** | Net Revenue | $\text{Gross Revenue} - \sum (\text{Interchange} + \text{Scheme})$ | Settled transaction | `SUM(net_revenue)` | `[Gross Revenue] - [Interchange Cost] - [Scheme Cost]` |
| **KPI_07** | Net Contribution | $\text{Net Revenue} - \sum \text{Chargeback Losses}$ | Portfolio / Merchant | `SUM(net_contribution)` | `[Net Revenue] - [Chargeback Losses]` |
| **KPI_08** | Net Take Rate (BPS) | $\frac{\text{Net Revenue}}{\text{Settled STV}} \times 10,000$ | Portfolio / Merchant | `10000.0 * SUM(net_revenue) / SUM(settled_gtv)` | `DIVIDE([Net Revenue] * 10000, [Settled Transaction Value (STV)], 0)` |
| **KPI_09** | Transaction Value at Risk (TVaR) | $\sum (\text{Amount} \times \mathbb{I}_{\text{Not Approved}})$ | One attempt | `SUM(CASE WHEN auth_status != 'Approved' THEN amount ELSE 0 END)` | `CALCULATE(SUM(fact_transactions[amount]), fact_transactions[auth_status] <> "Approved")` |
| **KPI_10** | Recoverable Revenue Opportunity | $\sum \text{Soft Decline GTV} \times 2.5\% \times 45\%$ | Aggregate segment | `SUM(CASE WHEN is_soft_decline THEN amount * 0.025 * 0.45 ELSE 0 END)` | `SUM(fact_transactions[soft_decline_amount]) * 0.025 * 0.45` |
| **KPI_11** | Chargeback Ratio (BPS) | $\frac{\text{Dispute Count}}{\text{Approved Volume}} \times 10,000$ | Merchant / Category | `10000.0 * COUNT(d.dispute_id) / COUNT(DISTINCT t.transaction_id)` | `DIVIDE([Dispute Count] * 10000, [Approved Transactions], 0)` |
| **KPI_12** | Contribution Margin % | $\frac{\text{Net Contribution}}{\text{Net Revenue}} \times 100\%$ | Merchant / Portfolio | `100.0 * SUM(net_contribution) / SUM(net_revenue)` | `DIVIDE([Net Contribution], [Net Revenue], 0)` |

---

## 2. In-Depth Metric Specifications

### KPI_01: Gross Transaction Value (GTV)
- **Business Definition:** The total cumulative monetary value of all transaction attempts initiated by cardholders at merchant checkouts.
- **Economic Meaning:** Measures total gross payment demand flowing through the platform gateway.
- **Analytical Limitations:** Includes authorization declines, network timeouts, and fraud attacks; does not reflect funds transferred or captured.

### KPI_02: Settled Transaction Value (STV)
- **Business Definition:** The total monetary value of transactions that successfully obtained issuer authorization and entered the settlement clearing cycle.
- **Economic Meaning:** Represents the true commercial top-line billing base of the payments facilitator.
- **Analytical Limitations:** Subject to post-settlement commercial chargebacks and merchant refunds.

### KPI_04: Authorization Rate %
- **Business Definition:** The percentage of initiated payment attempts that successfully receive an affirmative authorization response from the issuing bank.
- **Operational Meaning:** The primary conversion benchmark for payment gateway efficiency. Industry standard for card-not-present is 85%–92%.
- **Analytical Limitations:** Can be depressed by repeated card-testing bot attacks (Scenario B) or temporary network outages (Scenario A).

### KPI_06: Net Retained Revenue
- **Business Definition:** The net processing margin retained by the payment facilitator after subtracting direct pass-through costs (interchange fees paid to issuers and scheme assessment fees paid to Visa/Mastercard).
- **Economic Meaning:** The gross margin available to cover cloud infrastructure, risk engineering, customer support, and administrative overhead.

### KPI_07: Net Contribution
- **Business Definition:** Net retained revenue minus realized chargeback dispute loss write-offs and processor arbitration fees.
- **Economic Meaning:** The true economic profit contributed by a customer, merchant, or payment rail.

### KPI_10: Recoverable Revenue Opportunity
- **Business Definition:** Estimated net processing fee revenue recaptured by deploying smart retry logic on soft retryable declines (Codes `51`, `91`, `19`).
- **Mathematical Specification:**
  $$\text{Recoverable Revenue} = \left( \sum \text{Soft Decline GTV} \right) \times \text{Net Take Rate (2.5\%)} \times \text{Retry Yield (45\%)}$$
- **Strategic Purpose:** Provides the financial justification for investing in automated account updater and smart retry gateway infrastructure.
