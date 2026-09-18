# PAYMENTIQ | Operational Incident & Root-Cause Analysis (RCA) Report

**Framework:** Observation $\\rightarrow$ Segmentation $\\rightarrow$ Contribution $\\rightarrow$ Driver $\\rightarrow$ Financial Impact $\\rightarrow$ Action  
**Report Version:** 1.0.0  

---

## 1. Executive Summary
This report applies structured root-cause analysis (RCA) to investigate two major anomalous operational disruptions identified during the 2024 operating year, alongside an evaluation of customer support resolution efficiency.

---

## 2. Investigation Case Study 1: European Acquirer Link Degradation (August 12–16, 2024)

### Step 1: Observation
- Platform-wide authorization rate dropped by **~420 bps** during the week of August 12, 2024.

### Step 2: Segmentation
- Isolating by country reveals the degradation was 100% concentrated in **Germany (DE)** and **France (FR)**.
- US and UK authorization rates remained normal at **~91.5%**, while DE/FR authorization collapsed to **~58.2%**.

### Step 3: Driver & Technical Failure Mechanism
- Average processing latency in the European routing corridor escalated from a baseline of **175 ms** to over **2,800 ms**.
- **94% of failures** were tagged with Code `91` (*Issuer System Unavailable*) and Code `19` (*Network Timeout*), indicating primary routing gateway packet loss rather than cardholder insolvency.

### Step 4: Financial Impact
- **$1,420,000 in Transaction Value at Risk (TVaR)** was lost during the 5-day disruption window.
- Direct retained net revenue leakage: **~$35,500**.

### Step 5: Actionable Remediation
- Configure dynamic multi-acquirer failover routing: if secondary latency exceeds 600ms or Code `91` exceeds 5% in a 5-minute rolling window, automatically route traffic to secondary European banking partners.

---

## 3. Investigation Case Study 2: Digital Goods Card-Testing Attack (May 8–10, 2024)

### Step 1: Observation
- Digital Goods & Gaming (`MCC 5999`) experienced a **4.5x transaction volume surge** coinciding with authorization rates plunging to **~18.5%**.

### Step 2: Segmentation & Contribution
- Concentrated primarily in Card-Not-Present mobile and web checkout. Average ticket size dropped from **$24.50** to **$1.85**.

### Step 3: Driver & Mechanism
- Coordinated botnet execution of automated card-testing scripts testing stolen card bins with micro-transactions.
- Primary decline codes: Code `14` (*Invalid Card Number*) and Code `05` (*Do Not Honor*).

### Step 4: Financial Impact
- Direct processing network fee overhead incurred on failed authorization attempts: **~$18,200**.
- Elevated chargeback risk on the small fraction (~18%) of authorizations that initially succeeded.

### Step 5: Actionable Remediation
- Implement CAPTCHA challenge and velocity rate-limiting: block device fingerprints or IP subnets submitting $\ge 3$ declined attempts in under 60 seconds.

---

## 4. Operational Customer Support & SLA Performance

| Ticket Category | Total Cases | Share (%) | Avg Resolution (Mins) | SLA Breach Rate (%) | Avg CSAT (1-5) |
|---|---|---|---|---|---|
| Decline / Authorization Failure Inquiry | 1,180 | 53.6% | 155.2 m | **16.1%** | 3.59 |
| Suspected Duplicate Charge | 482 | 21.9% | 161.7 m | **19.3%** | 3.55 |
| Refund Processing Status | 305 | 13.8% | 161.1 m | **17.7%** | 3.59 |
| Account Security / Card Verification | 236 | 10.7% | 169.2 m | **16.5%** | 3.59 |

---

## 5. Operational Summary
- **Decline / Authorization Inquiries** represent **~55% of all support tickets**, directly highlighting that payment friction at checkout is the single largest operational cost driver in customer support.
- Enhancing automated customer messaging during soft declines (e.g. informing cardholders that a retry will occur automatically) can deflect up to 40% of tier-1 support tickets.
