# PAYMENTIQ | Documented Business & Technical Assumptions

**Document Version:** 1.0.0  
**Status:** Approved Economic Framework  

---

## 1. Commercial & Financial Assumptions

1. **Merchant Discount Rate (Gross Fee):** Billed to merchants based on card rail and contract tier:
   - Consumer Credit: Interchange (160–165 bps) + Scheme (13–14 bps) + Acquirer Markup (20–45 bps).
   - Consumer Debit: Interchange (60–65 bps) + Scheme (11–12 bps) + Acquirer Markup (15–30 bps).
   - Digital Wallets: Interchange (145 bps) + Scheme (15 bps) + Acquirer Markup (22 bps).
   - Commercial / Amex: Interchange (235 bps) + Scheme (18 bps) + Acquirer Markup (30 bps).
   - Instant Bank Transfer (A2A): Interchange (35 bps) + Scheme (8 bps) + Acquirer Markup (15 bps).

2. **Pass-Through Fee Mechanics:** Interchange fees and card network scheme fees are assumed to be non-negotiable direct pass-through costs payable to card issuing banks and payment networks (Visa, Mastercard, American Express).

3. **Chargeback Cost Structure:** Every realized chargeback dispute is assumed to write off 100% of the original settled transaction amount plus a non-refundable **$20.00 dispute administration assessment fee** imposed by the card network.

4. **Recoverable Leakage Parameters:**
   - Soft technical declines (Code `91` Issuer Unavailable, Code `19` Network Timeout) are assumed to have an **80% recovery yield** when re-routed through secondary gateways within 400 milliseconds.
   - Soft issuer declines (Code `51` Insufficient Funds) are assumed to have a **35% recovery yield** when retried with a 24-to-48 hour delay.
   - Blended addressable recovery yield across all soft declines is modeled conservatively at **45.0%**.
   - Net processing take rate on recovered volume is assumed at **2.50% (250 bps)**.

5. **Discount Rate for CLV:** Future cash flows are discounted using a monthly discount rate of $d = 0.01$ (1.0% per month, compounding to ~12.7% annual Weighted Average Cost of Capital).

---

## 2. Operational & Technical Assumptions

1. **Transaction Lifecycle Grain:** Each record in `core.fact_transactions` represents an atomic transaction authorization attempt. Retries receive an incremented `retry_attempt` counter.
2. **Customer Service SLA:** Standard operational SLA target for resolving payment dispute tickets is set at **240 minutes (4.0 hours)**. Any ticket exceeding this threshold is flagged as an SLA breach.
3. **Card Scheme Dispute Threshold:** In alignment with Visa Acquirer Monitoring Program (VAMP) and Mastercard Excessive Chargeback Program (ECP), any merchant exceeding **90 to 100 basis points (0.90%–1.00%)** in monthly dispute ratios is flagged for immediate mandatory risk intervention.
