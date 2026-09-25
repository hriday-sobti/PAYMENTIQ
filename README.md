# PAYMENTIQ | End-to-End Payment Transaction Intelligence & Business Analytics Platform

[![Python](https://img.shields.io/badge/Python-3.14-blue.svg)](https://www.python.org/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-16.6-336791.svg)](https://www.postgresql.org/)
[![DuckDB](https://img.shields.io/badge/DuckDB-1.5.5-FFF000.svg)](https://duckdb.org/)
[![Power BI](https://img.shields.io/badge/Power_BI-PBIP_Project-F2C811.svg)](https://powerbi.microsoft.com/)
[![Tests](https://img.shields.io/badge/Tests-197_Passed-brightgreen.svg)](tests/)
[![Reconciliation](https://img.shields.io/badge/Reconciliation-0.00%25_Variance-success.svg)](documentation/RECONCILIATION_REPORT.md)

---

## 📄 Executive Analytics Review (6-Page Publication Briefing)
👉 **[View the PAYMENTIQ Executive Analytics Review (PDF)](./reports/PAYMENTIQ_Executive_Review.pdf)**  
*A high-resolution 6-page C-suite document detailing checkout attrition funnels, fee economics, customer/merchant segmentation, and prioritized commercial action plans.*

---

## 🚀 Key Interactive Deliverables

| Deliverable | Format | Direct Access Link | Description |
|---|---|---|---|
| **📊 Interactive Power BI Dashboard** | Power BI Project (`.pbip` / TMDL) | [`powerbi/PAYMENTIQ.pbip`](./powerbi/PAYMENTIQ.pbip) | 6-page interactive executive suite with 30+ audited DAX measures and star schema relationships. |
| **📄 Executive Review Document** | Publication PDF (ReportLab) | [`reports/PAYMENTIQ_Executive_Review.pdf`](./reports/PAYMENTIQ_Executive_Review.pdf) | 6-page strategic briefing with embedded diagnostic figures, P&L waterfalls, and ROI roadmaps. |
| **🔗 Primary Source Repository** | GitHub / Open Source | [`https://github.com/hriday-sobti/PAYMENTIQ`](https://github.com/hriday-sobti/PAYMENTIQ) | Complete, reproducible repository with 197 automated tests passing in 15 seconds. |
| **📑 Master Analytical Case Study** | Comprehensive Markdown | [`documentation/PAYMENTIQ_ANALYTICAL_CASE_STUDY.md`](./documentation/PAYMENTIQ_ANALYTICAL_CASE_STUDY.md) | Exhaustive chart-by-chart deep dives, narrative transitions, and stakeholder value maps. |

---

> **PAYMENTIQ** is an enterprise-grade payment transaction intelligence platform that processes multi-million transaction event streams to identify revenue leakage, customer behavior, merchant performance, payment failure modes, fraud signals, and operational bottlenecks using **Python, Advanced SQL, PostgreSQL, DuckDB, Power BI, and Conversational Analytics**.

---

## 1. Executive Summary & Business Problem

### The Challenge
A global payments facilitator processes millions of commercial card and alternative payment transactions monthly. Executive leadership requires an integrated, reproducible analytics platform to answer:
1. **What is happening?** What is our top-line transactional throughput, conversion funnel, and retained margin?
2. **Where is value leaking?** How much Gross Transaction Value (GTV) is lost to authorization failures, and what portion is addressable via smart retry logic?
3. **Who matters most?** Which customer segments drive the majority of long-term economic value (CLV), and which merchants represent portfolio concentration risk?
4. **Why did performance change?** When authorization dips occur, what are the precise root causes (gateway latency vs. cardholder insolvency vs. bot attacks)?
5. **What should management investigate next?** What prioritized commercial and operational actions yield the highest verified return on investment?

### The Core Finding
In 2024, the platform processed **1,000,000 transaction attempts**, representing **$134,531,743.69 in Gross Transaction Value (GTV)**. Of this demand, **$121,120,030.80 successfully converted to settled funds** (911,844 approvals), delivering an overall platform **authorization rate of 91.18%** and **$803,472.60 in Net Retained Revenue**.

However, forensic decomposition reveals that **$13,411,712.89 in Gross Transaction Value failed or was declined at checkout** (Transaction Value at Risk, or TVaR). Crucially, 68.5% ($9.19M) of this uncaptured volume stems from **addressable soft declines**—specifically insufficient funds and temporary gateway timeouts. By deploying automated, balance-aware smart retry routing, the business has an empirical, addressable opportunity to recapture **+$103,334.06 in incremental net revenue** ($4.13M settled GTV).

<p align="center">
  <img src="reports/figures/eda_monthly_volume_trend.png" width="720" alt="2024 Monthly Volume & Net Revenue Trend" />
  <br/><em>Figure: 2024 Monthly Settled Volume ($M) and Net Retained Revenue ($K) Trajectory</em>
</p>

---

## 2. What PAYMENTIQ Adds: Baseline vs. Advanced Platform

Traditional payment reporting in many mid-market fintechs relies on static monthly CSV exports, basic sales dashboards, and monolithic decline metrics. PAYMENTIQ fundamentally transforms this workflow:

| Analytical Dimension | Conventional / Baseline Approach | PAYMENTIQ Advanced Implementation | Strategic Business Value |
|---|---|---|---|
| **Data Architecture** | Single flat CSV or disconnected spreadsheets. | Normalized PostgreSQL 16 star schema coupled with DuckDB in-memory columnar acceleration. | Sub-second query execution on 1M+ rows; 0.00% cross-layer financial drift. |
| **Checkout Funnel** | Treats all declined transactions as lost revenue. | Multi-tier decline taxonomy mapping ISO 8583 codes into Soft (retryable) vs. Hard (terminal) buckets. | Isolates $9.19M in recoverable soft volume, establishing a +$103.3K net revenue recapture case. |
| **Financial Economics** | Focuses solely on gross processing fees (MDR). | Full P&L waterfall separating MDR, pass-through interchange costs, scheme assessment fees, and chargeback losses. | Exposes true economic Net Operating Contribution ($647K) and net take rate (66.3 bps). |
| **Customer Retention** | Basic monthly active user (MAU) counts. | 12-Month triangular acquisition cohort retention matrix and quintile-based RFM behavioral segmentation. | Proves that Month 1 retention drops to 42.1% before stabilizing at 18–22%; isolates the 16.4% "At Risk" tier. |
| **Merchant Strategy** | Ranks merchants purely by total sales volume. | 4-Quadrant Merchant Opportunity Matrix (Volume vs. Net Contribution Margin %) + HHI concentration. | Identifies 118 "Margin Drag" merchants for contract renegotiation from flat rate to IC+ pricing (+45K contribution). |
| **Threat Detection** | Retrospective fraud rules after chargebacks clear (60-day lag). | Unsupervised Isolation Forest model (PR-AUC = 0.502) detecting card-testing attacks without label leakage. | Flags micro-transaction bot attacks in real time, preventing processor fee penalties. |
| **Statistical Rigor** | Intuitive assumptions regarding authentication friction. | Formal Two-Sample Pooled Proportion Z-Test ($Z = 45.67, p < 10^{-15}$) comparing 3DS vs. non-3DS rails. | Proves a verified +342 bps authorization lift for 3DS transactions, shifting chargeback liability. |
| **Forecasting** | Linear extrapolation or static budget targets. | Holt-Winters Triple Exponential Smoothing (additive trend + 7-day seasonality) with 80/20 temporal backtesting. | Highly accurate Q1 2025 projection (Volume MAPE 1.53%, GTV MAPE 3.25%). |
| **Stakeholder Access** | Static slide decks requiring manual analyst updates. | 6-page interactive Power BI Project (`.pbip`) + AST-validated natural-language query console (`Ask PAYMENTIQ`). | Democratizes ad-hoc query capabilities with verified deterministic metric grounding. |

---

## 3. Platform Architecture & Data Flow

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                       PAYMENTIQ PIPELINE ARCHITECTURE                       │
└─────────────────────────────────────────────────────────────────────────────┘

  [ Event Generation Engine ] ───────> [ Data Quality & Profiling ]
  - Vectorized Parametric Distributions  - 13 Automated Business Rules
  - Calibrated Merchant Category Codes   - Schema & Null Invariant Checks
  - Injected Operational Incidents       - Type Downcasting & Enrichment
                 │                                      │
                 ▼                                      ▼
  [ PostgreSQL 16 Warehouse ] ────────> [ DuckDB In-Memory Engine ]
  - Core Dimensional Star Schema         - Columnar Parquet Acceleration
  - Composite Performance Indexes        - Vectorized Sub-Second Queries
  - Full Referential Integrity (PK/FK)   - Identical Analytical Views
                 │                                      │
                 ▼                                      ▼
  [ Advanced Analytics & ML ] ─────────> [ Power BI Executive Suite ]
  - RFM & 12-Month Cohort Matrices       - 6-Page Interactive Cockpit
  - Holt-Winters 90-Day Forecasting      - 30+ Audited DAX Measures
  - Isolation Forest Anomaly Engine      - Star Schema Semantic Model
  - Two-Sample Proportion Z-Test         - Complete .pbip / TMDL Source
                 │                                      │
                 ▼                                      ▼
  [ Conversational NLQ Console ] ─────────> [ Executive Review PDF ]
  - Natural-Language "Ask PAYMENTIQ"     - 6-Page Publication Document
  - AST-Validated SQL Compilation        - Observation-Driver-Action
  - Deterministic Metric Verification    - Embedded High-Res Figures
```

---

## 4. Dimensional Star Schema & Data Model

```
              ┌─────────────────────┐
              │  dim_customers      │
              │  customer_key (PK)  │
              │  customer_segment   │
              │  customer_country   │
              └──────────┬──────────┘
                         │ 1
                         │ *
┌─────────────────────┐  │   ┌─────────────────────┐
│  dim_merchants      │  │   │  dim_dates          │
│  merchant_key (PK)  ├──┼───┤  date_key (PK)      │
│  merchant_category  │  │   │  full_date, year... │
│  pricing_tier       │  │   └──────────┬──────────┘
└──────────┬──────────┘  │              │ 1
           │ 1           │              │ *
           │ *           │              │ *
    ┌──────┴─────────────┴──────────────┴──────┐
    │          fact_transactions               │
    │  transaction_id (PK), date_key (FK)      │
    │  customer_key (FK), merchant_key (FK)    │
    │  payment_method_key (FK), decline_code   │
    │  amount, processing_fee, interchange_fee │
    │  scheme_fee, net_revenue, latency_ms...  │
    └──────┬────────────────────────────┬──────┘
           │ *                          │ *
           │ 1                          │ 1
┌──────────┴───────────────┐ ┌──────────┴───────────────┐
│  dim_payment_methods     │ │  dim_decline_codes       │
│  payment_method_key (PK) │ │  decline_code (PK)       │
│  method_name, card_brand │ │  decline_reason, soft/hard│
└──────────────────────────┘ └──────────────────────────┘
```

### Table Grains
- **`core.fact_transactions` (1,000,000 rows):** Grain = exactly one transaction authorization attempt.
- **`core.fact_disputes` (1,110 rows):** Grain = exactly one formal chargeback dispute event.
- **`core.fact_support_cases` (2,203 rows):** Grain = exactly one customer service ticket.
- **`core.dim_customers` (40,000 rows):** Grain = one cardholder account.
- **`core.dim_merchants` (1,000 rows):** Grain = one contracted commercial seller.
- **`core.dim_dates` (1,826 rows):** Grain = one calendar day (2022–2026).
- **`core.dim_payment_methods` (9 rows):** Grain = one payment rail and card scheme configuration.
- **`core.dim_decline_codes` (8 rows):** Grain = one ISO 8583 response code.

---

## 5. Centralized KPI Framework & Reconciled Results

All metrics strictly obey the centralized contracts defined in [`config/kpi_definitions.yaml`](config/kpi_definitions.yaml) and reconcile across Python, SQL, DuckDB, Power BI, and the Executive PDF:

| Metric | Business Definition | Mathematical Formula | 2024 Verified Value |
|---|---|---|---|
| **Gross Transaction Value (GTV)** | Total initiated checkout volume | $\sum \text{Amount}$ | **$134,531,743.69** |
| **Settled Volume (STV)** | Successfully authorized volume | $\sum (\text{Amount} \times \mathbb{I}_{\text{Approved}})$ | **$121,120,030.80** |
| **Total Transaction Volume** | Count of all transaction attempts | $\sum 1$ | **1,000,000 attempts** |
| **Approved Transactions** | Count of successful authorizations | $\sum \mathbb{I}_{\text{Approved}}$ | **911,844 approvals** |
| **Authorization Rate %** | Operational gateway conversion rate | $\frac{\text{Approved}}{\text{Total}} \times 100\%$ | **91.18%** |
| **Gross Revenue (MDR)** | Gross fees billed to merchants | $\sum \text{Processing Fee}$ | **$2,621,500.73** |
| **Interchange Cost** | Pass-through fees paid to issuing banks | $\sum \text{Interchange Fee}$ | **$1,637,102.62** |
| **Scheme Assessment Cost** | Pass-through fees paid to Visa/MC | $\sum \text{Scheme Fee}$ | **$180,925.51** |
| **Net Retained Revenue** | Retained processing margin | $\text{Gross Revenue} - \text{Pass Throughs}$ | **$803,472.60** |
| **Net Take Rate (BPS)** | Retained margin basis points | $\frac{\text{Net Revenue}}{\text{Settled STV}} \times 10,000$ | **66.3 bps** |
| **Net Contribution** | Retained profit after chargeback losses | $\text{Net Revenue} - \sum \text{Dispute Losses}$ | **$647,055.64** |
| **Contribution Margin %** | Share of net revenue retained as profit| $\frac{\text{Net Contribution}}{\text{Net Revenue}} \times 100\%$ | **80.53%** |
| **Value at Risk (TVaR)** | Gross uncaptured failed checkout volume| $\sum (\text{Amount} \times \mathbb{I}_{\text{Not Approved}})$ | **$13,411,712.89** |
| **Recoverable Net Leakage** | Addressable margin from smart retries | $\text{Soft GTV} \times 2.5\% \times 45\%$ | **$103,334.06** |
| **Chargeback Dispute Rate** | Dispute frequency in basis points | $\frac{\text{Disputes}}{\text{Approved}} \times 10,000$ | **12.17 bps** (Compliant) |
| **Average Network Latency** | End-to-end authorization round trip | $\text{Mean}(\text{Latency})$ | **201.0 ms** |

---

## 6. Power BI Decision Suite: 6-Page Interactive Walkthrough

The platform includes a complete, source-controlled Power BI Project ([`powerbi/PAYMENTIQ.pbip`](powerbi/PAYMENTIQ.pbip)) containing the Tabular Model Definition ([`model.bim`](powerbi/PAYMENTIQ.Dataset/model.bim)), report visual configurations ([`report.json`](powerbi/PAYMENTIQ.Report/report.json)), and pre-computed datasets in [`powerbi/export_data/`](powerbi/export_data/):

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                   PAYMENTIQ POWER BI 6-PAGE EXECUTIVE SUITE                 │
├──────────────────────┬──────────────────────┬───────────────────────────────┤
│ Page 1: Executive    │ Page 2: Payment      │ Page 3: Customer              │
│ Overview             │ Performance          │ Intelligence                  │
│ - KPI Metric Cards   │ - Conversion Funnel  │ - RFM Segment Distribution    │
│ - Monthly Trajectory │ - Rail Auth Matrix   │ - 12-Month Cohort Triangle    │
│ - Regional Scorecard │ - Decline Donut      │ - CLV Spend vs Contribution   │
├──────────────────────┼──────────────────────┼───────────────────────────────┤
│ Page 4: Merchant     │ Page 5: Risk &       │ Page 6: Management           │
│ Intelligence         │ Anomaly Monitoring   │ Action Center                 │
│ - 4-Quadrant Matrix  │ - Risk Score (0-1000)│ - Prioritized Action Cards    │
│ - Margin Drag Table  │ - Dispute Rate BPS   │ - Dollar-Denominated Impact   │
│ - Scheme Compliance  │ - Anomaly Review List│ - Operational Action Backlog  │
└──────────────────────┴──────────────────────┴───────────────────────────────┘
```

### Page 1: Executive Overview
- **Purpose:** Macro-level performance cockpit for senior leadership (CEO, CFO, Head of Payments).
- **Key Question:** Are top-line volume, conversion efficiency, and retained margins meeting strategic targets?
- **Key KPIs:** Gross Transaction Value ($134.5M), Settled STV ($121.1M), Authorization Rate (91.18%), Net Revenue ($803.5K), Contribution Margin (80.53%).
- **Key Visuals:** 5 Top KPI Cards, 12-Month Volume/Revenue Combo Trajectory, Regional Conversion Table.
- **Executive Takeaway:** Overall financial yield is outperforming plan (+118 bps auth rate, +253 bps margin), but geographic variance highlights European corridor volatility.

### Page 2: Payment Performance
- **Purpose:** Diagnostic routing and conversion analysis for Payment Operations and Engineering.
- **Key Question:** Where in the payment lifecycle are transactions dropping, and which rails perform best?
- **Key KPIs:** Total Attempts (1M), Gateway Success (99.87%), Approval Rate (91.18%), Average Latency (201 ms).
- **Key Visuals:** 4-Stage Horizontal Funnel, Grouped Rail Conversion Chart, Decline Code Donut Visual, Hierarchical Matrix Drilldown (`Country` $\rightarrow$ `Category` $\rightarrow$ `Method` $\rightarrow$ `Device`).
- **Executive Takeaway:** Modern tokenized rails (Apple Pay, Google Pay, A2A) deliver up to 96% authorization, while legacy Card-Not-Present credit card checkouts suffer 11.2% decline rates.

### Page 3: Customer Intelligence
- **Purpose:** Customer lifecycle economics and cohort recurrence tracking for CRM and Growth Marketing.
- **Key Question:** Who are our most valuable cardholders, and how quickly do newly acquired cohorts churn?
- **Key KPIs:** Active Cardholders (40,000), Top-2 Tier Contribution Share (61.2%), Month-1 Retention (42.1%), Steady-State Retention (19.8%).
- **Key Visuals:** RFM Segment Volume Contribution Bar Chart, 12-Month Cohort Retention Triangle Heatmap, Customer Spend vs. Contribution Scatter Plot, At-Risk Customer Grid.
- **Executive Takeaway:** 28.1% of cardholders generate 61.2% of platform net contribution; priority re-engagement should target the 16.4% "At Risk" tier before Day 90 dormancy sets in.

### Page 4: Merchant Intelligence
- **Purpose:** Portfolio yield optimization and card scheme compliance monitoring for Merchant Business Development.
- **Key Question:** Which merchants drive healthy margins versus which accounts erode profitability or exceed dispute thresholds?
- **Key KPIs:** Portfolio HHI (44.3), Core Anchors (482), Margin Drag (118), Portfolio Dispute Ratio (12.17 bps).
- **Key Visuals:** 4-Quadrant Opportunity Matrix Scatter Plot, Quadrant GTV Share Donut, Merchant Compliance Scorecard Table.
- **Executive Takeaway:** Contract restructuring on 118 Margin Drag merchants captures +$45K in annual contribution; zero merchants currently breach the critical 100 bps card scheme chargeback limit.

### Page 5: Risk & Anomaly Monitoring
- **Purpose:** Real-time threat surveillance and fraud risk analysis for Fraud Operations and Risk Management.
- **Key Question:** Where are abnormal velocity spikes, bot attacks, and high-risk chargeback clusters emerging?
- **Key KPIs:** Flagged Anomalies (1.80% / 4,500 txs), Mean Risk Score (214), High-Risk Transactions (1,840 txs), Realized Chargeback Losses ($134.2K).
- **Key Visuals:** Composite Risk Score Histogram (0–1000), Category Chargeback BPS Ranking Bar Chart, Priority Anomaly Review Grid.
- **Executive Takeaway:** Digital Goods (`MCC 5999`) accounts for the highest dispute exposure (95 bps); Isolation Forest successfully flags bot card-testing attacks without disrupting genuine shoppers.

### Page 6: Management Action Center ("WHAT SHOULD MANAGEMENT INVESTIGATE?")
- **Purpose:** Decision support engine translating analytical findings directly into prioritized operational and commercial actions.
- **Key Question:** What concrete initiatives should leadership fund to capture the highest return on investment?
- **Key Visuals:** 3 Top Action Cards with Dollar Impact, Prioritized Operational Action Backlog Table.
- **Executive Takeaway:** Deploying smart retries (+$103K), mandating 3DS (+342 bps auth lift), and migrating Margin Drag contracts (+$45K) deliver an aggregate **+$170K+ in measurable commercial value**.
---

## 7. Connected Analytical Deep-Dives (Chart-by-Chart Analysis)

The analytical investigation unfolds as a continuous business investigation:
$$\text{Overall Performance} \longrightarrow \text{Conversion Funnel} \longrightarrow \text{Financial Exposure} \longrightarrow \text{Customer Concentration} \longrightarrow \text{Merchant Opportunity} \longrightarrow \text{Risk \& Anomalies} \longrightarrow \text{Operational RCA} \longrightarrow \text{Forward Projections}$$

---

### Chart 1: 2024 Monthly Settled Volume and Net Retained Revenue Trajectory
<p align="center">
  <img src="reports/figures/eda_monthly_volume_trend.png" width="700" alt="2024 Monthly Volume & Net Revenue Trend" />
  <br/><em>Figure 1: 2024 Monthly Settled Volume ($M) and Net Retained Revenue ($K) Trajectory</em>
</p>

- **What It Shows:** Dual-axis monthly time series tracking Settled Transaction Volume ($ Millions, bar chart) and Net Retained Revenue ($ Thousands, line chart) across all 12 calendar months of 2024.
- **Key Finding:** Top-line settled volume expanded from **$8.91M in January to a peak of $14.82M in November**, driven by the holiday shopping cycle, while net revenue closely tracked volume at a steady 66.3 bps net take rate. A temporary volume deceleration occurred in August ($9.21M).
- **Executive Takeaway (What? So What? Now What?):**
  - *What:* Monthly volume grew +66.3% from January to November, with an anomalous growth pause in August.
  - *So What:* The revenue model demonstrates stable take-rate elasticity, but the August disruption warrants operational investigation.
  - *Now What:* Deconstruct August gateway latency and routing logs to determine the root cause of the volume contraction.
- **Supporting Evidence:** Gross processing revenue totaled **$2,621,500.73**, while pass-through interchange and scheme fees consumed **$1,818,028.13**, leaving **$803,472.60** in net retained earnings.
- **Connection to Next Visual:** While monthly totals show strong macro growth, understanding top-line health requires examining the checkout conversion funnel to identify where initiated transactions drop off.

---

### Chart 2: End-to-End Payment Conversion & Retention Funnel
<p align="center">
  <img src="reports/figures/payment_performance_funnel.png" width="700" alt="Payment Performance Funnel" />
  <br/><em>Figure 2: PAYMENTIQ End-to-End Authorization & Retention Conversion Funnel</em>
</p>

- **What It Shows:** 4-stage operational transaction funnel illustrating attrition from initiated checkout demand to retained settled funds.
- **Key Finding:** Out of **1,000,000 initiated attempts**, **998,700 (99.87%) successfully reached issuer gateways**, **911,844 (91.18%) achieved authorization**, and **895,431 (89.54%) were retained** after customer return refunds.
- **Executive Takeaway (What? So What? Now What?):**
  - *What:* The largest single attrition point occurs at the authorization stage (86,856 declines, or 8.69% of attempts), whereas technical gateway drops are minimal (0.13%).
  - *So What:* Checkout failure is predominantly an issuer decision problem rather than a network connectivity failure.
  - *Now What:* Deconstruct decline reasons to determine how much of this $13.4M in declined volume is recoverable.
- **Supporting Evidence:** Technical gateway failure rate was held to **0.13% (1,300 attempts)**, proving high infrastructure availability, but cardholder authorization rejections accounted for **8.69% (86,856 attempts)**.
- **Connection to Next Visual:** Having isolated that 8.69% of transactions fail at the authorization step, the next step is quantifying the exact dollar-denominated value at risk and separating recoverable from terminal losses.

---

### Chart 3: Financial Volume Waterfall & Value at Risk (TVaR)
<p align="center">
  <img src="reports/figures/revenue_leakage_waterfall.png" width="700" alt="Revenue Leakage Waterfall" />
  <br/><em>Figure 3: Financial Volume Waterfall & Addressable Value at Risk (TVaR)</em>
</p>

- **What It Shows:** Financial volume waterfall decomposing total GTV demand into Settled Volume, Soft Declines (TVaR), Hard Declines (TVaR), and realized Chargeback Losses.
- **Key Finding:** Of the **$13,411,712.89 in total Transaction Value at Risk (TVaR)**, **$9,185,249.79 (68.5%) represents addressable soft declines** (insufficient funds, network timeouts), while terminal hard declines (stolen cards, invalid numbers) total $4.23M (31.5%).
- **Executive Takeaway (What? So What? Now What?):**
  - *What:* Over two-thirds of declined transaction volume is addressable and technically retryable.
  - *So What:* Treating all declines as permanent lost sales forfeits over $9.1M in customer checkout demand.
  - *Now What:* Deploy smart retry routing with a 24-hour liquidity delay to capture the estimated **+$103,334.06 net revenue prize**.
- **Supporting Evidence:** Soft declines are dominated by Code `51` (Insufficient Funds, $5.62M) and Code `91` (Issuer System Unavailable, $2.41M). Realized chargeback losses totaled **$134,216.96**.
- **Connection to Next Visual:** After evaluating transaction-level leakage, the analysis shifts to customer-level behavior: which cardholder cohorts generate our volume and how well do we retain them?

---

### Chart 4: 12-Month Customer Acquisition Cohort Retention Triangle
<p align="center">
  <img src="reports/figures/customer_cohort_retention.png" width="700" alt="Customer Cohort Retention Heatmap" />
  <br/><em>Figure 4: 12-Month Customer Acquisition Cohort Activity Retention Triangle</em>
</p>

- **What It Shows:** Triangular cohort heatmap tracking monthly activity retention rates for cardholder cohorts acquired between January and December 2024 across 12 subsequent operating months.
- **Key Finding:** Retention follows an empirical power-law decay: Month 1 repeat transaction rates drop to **42.1%** across cohorts, but subsequently flatten and stabilize into a highly predictable recurring baseline of **18.0% to 22.0%** from Month 4 through Month 12.
- **Executive Takeaway (What? So What? Now What?):**
  - *What:* Customer retention experiences acute early attrition in Month 1, but stabilized cohorts exhibit remarkable long-term persistence (~20%).
  - *So What:* Growth depends heavily on repeat spend from the core retained base; post-acquisition onboarding during Days 1–30 is the critical window to prevent churn.
  - *Now What:* Cross-reference retention persistence against customer RFM spend tiers to identify which segments represent the highest lifetime value.
- **Supporting Evidence:** The January 2024 cohort (3,333 cardholders) recorded 42.4% retention in February, 28.1% in March, and maintained 19.8% active recurrence in December (Month 11).
- **Connection to Next Visual:** Knowing that ~20% of customers remain permanently active, the next question is: how much spend concentration is driven by these top recurring segments?

---

### Chart 5: Customer RFM Behavioral Segment Value Contribution
<p align="center">
  <img src="reports/figures/customer_rfm_segments.png" width="700" alt="Customer RFM Segments" />
  <br/><em>Figure 5: RFM Behavioral Segment Contribution to Settled Transaction Volume</em>
</p>

- **What It Shows:** Horizontal bar chart displaying total settled Gross Transaction Value contribution across the 7 standardized RFM customer segments.
- **Key Finding:** Extreme Pareto concentration: **Champions ($42.3M GTV) and Loyal Customers ($28.4M GTV) represent 28.1% of the customer base but drive 58.4% of total settled volume and 61.2% of net contribution ($396K)**.
- **Executive Takeaway (What? So What? Now What?):**
  - *What:* Less than a third of cardholders generate nearly two-thirds of platform net contribution.
  - *So What:* Losing a Champion cardholder has an outsized negative impact compared to casual retail shoppers.
  - *Now What:* Establish priority routing, frictionless 3DS whitelisting, and proactive support intervention for the 16.4% of customers currently sliding into the "At Risk" segment.
- **Supporting Evidence:** Champions exhibit an average annual spend of **$6,280.40** with average recency of **14.2 days**, compared to Hibernating customers who average **$342.10** with recency exceeding **210 days**.
- **Connection to Next Visual:** Having established customer-side concentration, the analysis transitions to the merchant side: how is volume distributed across commercial sellers, and where are margins compressed?

---

### Chart 6: 4-Quadrant Merchant Opportunity Matrix (Volume vs. Margin %)
<p align="center">
  <img src="reports/figures/merchant_opportunity_matrix.png" width="700" alt="Merchant Opportunity Matrix" />
  <br/><em>Figure 6: 4-Quadrant Merchant Opportunity Matrix (Volume vs. Contribution Margin %)</em>
</p>

- **What It Shows:** Log-scaled scatter plot mapping 1,000 contracted merchants across Settled Transaction Volume (X-axis) and Net Contribution Margin % (Y-axis), partitioned into four strategic quadrants by portfolio medians.
- **Key Finding:** While 482 merchants represent **Core Anchors** (high volume, above-median margin), **118 merchants operate as Margin Drag** (high volume, but contribution margin $<80.5\%$). Furthermore, 20 merchants exhibit elevated dispute rates approaching the 90 bps card network monitoring threshold.
- **Executive Takeaway (What? So What? Now What?):**
  - *What:* High transaction volume does not automatically equal profitability; 118 large accounts are diluting corporate margins due to flat-rate pricing on high-cost payment rails.
  - *So What:* Restructuring these 118 contracts will directly expand profitability without requiring new merchant acquisition.
  - *Now What:* Migrate Margin Drag accounts from flat-rate blended fees to Interchange Plus (IC+) pricing with minimum margin floors (**+$45K annual contribution uplift**).
- **Supporting Evidence:** Overall portfolio Herfindahl-Hirschman Index (HHI) is **44.3** (highly competitive and unconcentrated). Core Anchors generate **$78.2M in GTV** at an average net contribution margin of **84.2%**.
- **Connection to Next Visual:** Beyond merchant pricing economics, payment networks face systemic risks: what operational anomalies, fraud patterns, and bot attacks threaten portfolio health?

---

### Chart 7: Isolation Forest Anomaly Detection Performance & Score Separation
<p align="center">
  <img src="reports/figures/anomaly_detection_eval.png" width="700" alt="Anomaly Detection Evaluation" />
  <br/><em>Figure 7: Isolation Forest Anomaly Detection Precision-Recall Curve & Score Separation</em>
</p>

- **What It Shows:** Dual-panel diagnostic visual displaying the Precision-Recall curve (left) and empirical anomaly score density distributions separated by true latent fraud events (right).
- **Key Finding:** The unsupervised Isolation Forest model (contamination = 0.018) achieved an **Area Under the Precision-Recall Curve (PR-AUC) of 0.502**, successfully isolating abnormal card-testing micro-charges and high-ticket off-peak cross-border spikes without using supervised ground-truth labels during training.
- **Executive Takeaway (What? So What? Now What?):**
  - *What:* The model successfully separates anomalous transaction patterns from normal commercial baseline traffic.
  - *So What:* Severe class imbalance (~0.5% true fraud prevalence) makes standard accuracy metrics misleading; PR-AUC confirms genuine discriminative capability.
  - *Now What:* Establish an automated operational rule: transactions with anomaly scores $\ge 0.75$ are stepped up to mandatory 3DS verification rather than subjected to blunt, conversion-killing hard blocks.
- **Supporting Evidence:** At the optimal decision threshold (score = 0.466), the model flags **4,500 transactions (1.80%)** as anomalous, intercepting high-risk events while maintaining minimal customer friction.
- **Connection to Next Visual:** If stepping up suspicious transactions to 3D-Secure authentication is the recommended intervention, does 3DS authentication hurt checkout conversion? We test this empirically using inferential statistics.

---

### Chart 8: Two-Sample Proportion Z-Test: 3DS Authentication Conversion Lift
<p align="center">
  <img src="reports/figures/statistical_hypothesis_test.png" width="700" alt="Statistical Hypothesis Test" />
  <br/><em>Figure 8: Two-Sample Proportion Z-Test Sampling Distribution & Rejection Region (α = 0.01)</em>
</p>

- **What It Shows:** Standard normal sampling distribution under the null hypothesis ($H_0$) with shaded critical rejection regions ($\alpha = 0.01$) and the observed test statistic ($Z = 45.67$).
- **Key Finding:** 3D-Secure verified Card-Not-Present transactions achieve an authorization rate of **93.19% (n=408,402)** compared to **89.77% (n=191,355)** for frictionless non-3DS transactions. The resulting $Z = 45.67$ ($p < 10^{-15}$) decisively rejects the null hypothesis.
- **Executive Takeaway (What? So What? Now What?):**
  - *What:* 3D-Secure provides a statistically verified **+342 bps authorization rate uplift** (99% CI: `[+3.21%, +3.62%]`).
  - *So What:* The long-held commercial assumption that 3DS authentication suppresses sales conversion is empirically false; issuer approval confidence significantly outweighs cardholder form friction.
  - *Now What:* Mandate 3DS rollout across all Card-Not-Present merchants with average ticket sizes exceeding $100, capturing **+$882.4K in settled GTV** and shifting fraud chargeback liability to card issuers.
- **Supporting Evidence:** Standardized effect size is Cohen's $h = 0.1228$. Total recoverable net revenue from non-3DS volume uplift is **+$22,060.19**.
- **Connection to Next Visual:** Statistical and machine learning models establish baseline rules, but what happens during unexpected real-world infrastructure failures? We analyze two historical operational incidents.

---

### Chart 9: Operational Root-Cause Analysis: August Outage & May Attack
<p align="center">
  <img src="reports/figures/root_cause_incident_analysis.png" width="700" alt="Root Cause Incident Analysis" />
  <br/><em>Figure 9: Operational Incident Diagnostics: August Gateway Outage & May Bot Attack</em>
</p>

- **What It Shows:** Dual-panel incident diagnostic visual analyzing the August European Gateway Degradation (left panel, DE/FR vs. US authorization rates) and the May Digital Goods Card-Testing Bot Attack (right panel, transaction velocity vs. auth rate).
- **Key Finding:**
  - *Incident 1 (August 12–16):* Packet loss in European acquirer links caused DE/FR processing latency to spike to 2,800+ ms, collapsing authorization rates from **91.5% to 58.2%** and leaking **$1.42M in TVaR**. US rates remained unaffected.
  - *Incident 2 (May 8–10):* Botnet scripts targeted Merchant `MERCH-0042` with micro-charges ($1.50–$3.50), surging transaction volume 4.5x while authorization plunged to **18.5%**, incurring **$18.2K in non-refundable processor network fees**.
- **Executive Takeaway (What? So What? Now What?):**
  - *What:* Platform performance drops were localized operational events rather than systemic commercial decay.
  - *So What:* Single-acquirer routing dependencies and lack of checkout rate-limiting create substantial, unhedged financial vulnerabilities.
  - *Now What:* Deploy multi-acquirer dynamic failover at 600 ms latency and enforce checkout velocity rate-limiting on digital merchant checkouts.
- **Supporting Evidence:** Code `91` (Issuer Unavailable) accounted for 70% of August outage failures. Customer support decline inquiries surged to **55% of all support tickets** with an average resolution time of **132.4 minutes**.
- **Connection to Next Visual:** Having resolved operational vulnerabilities and established retry playbooks, how will platform volume trajectory look over the next quarter? We turn to time-series forecasting.

---

### Chart 10: Holt-Winters 90-Day Forward Transaction Volume Forecast (Q1 2025)
<p align="center">
  <img src="reports/figures/forecasting_trajectory.png" width="700" alt="Forecasting Trajectory" />
  <br/><em>Figure 10: Holt-Winters Daily Transaction Volume 90-Day Forward Forecast & Prediction Bounds</em>
</p>

- **What It Shows:** Time-series projection of daily transaction volume from January 1 to March 31, 2025, generated by Holt-Winters Triple Exponential Smoothing, showing the point forecast (dashed line) and 80% empirical prediction intervals.
- **Key Finding:** The model forecasts **243,850 total transactions** and **$29.58M in settled Gross Transaction Value** for Q1 2025. Out-of-sample backtest validation (80% train / 20% test) achieved an exceptional **Volume MAPE of 1.53%** and **GTV MAPE of 3.25%**.
- **Executive Takeaway (What? So What? Now What?):**
  - *What:* Transaction demand is projected to grow steadily with pronounced 7-day weekly seasonality (Monday–Wednesday building to Friday peaks, Sunday troughs).
  - *So What:* Cloud gateway capacity and customer support staffing can be budgeted with high precision (<2% error).
  - *Now What:* Allocate infrastructure headroom for Friday peak throughput (~3,400 daily txs) and schedule database maintenance windows during Sunday troughs (~1,950 daily txs).
- **Supporting Evidence:** Authorization rate is forecasted to remain stable at **91.2% $\pm$ 0.4%**. Forward 80% prediction interval ranges between **2,420 and 3,180 daily transactions**.

---

## 8. Conversational Analytics: "Ask PAYMENTIQ" (Natural Language to SQL)

An interactive natural-language query interface ([`ai/assistant_cli.py`](ai/assistant_cli.py)) that compiles stakeholder business questions directly into validated data warehouse queries:
- **Architecture:** Question Parsing $\rightarrow$ Intent Mapping $\rightarrow$ AST Safety Verification $\rightarrow$ SQL Execution $\rightarrow$ Data-Backed Synthesis.
- **Security:** Strict read-only query whitelist ([`ai/query_whitelist.py`](ai/query_whitelist.py)); blocks SQL injection, comments, and modifying commands.
- **Deterministic Metric Verification:** Automated test suite asserts that every monetary figure and percentage cited in the synthesized text matches returned database rows verbatim.

```bash
# Example Interactive CLI Session
python -m ai.assistant_cli "How much revenue are we losing to payment declines?"

======================================================================
QUESTION: How much revenue are we losing to payment declines?
INTENT:   REVENUE_LEAKAGE_SUMMARY
======================================================================
ANSWER:
Total Transaction Value at Risk (TVaR) from declined and failed transactions stands 
at $13,411,712.89. Of this, soft retryable declines account for $9,185,249.79, 
representing an estimated $103,334.06 in recoverable net revenue opportunity. 
Realized chargeback losses totaled $134,216.96.
======================================================================
```

---

## 9. Business Stakeholder Benefit Mapping

| Stakeholder Persona | Business Problem Addressed | PAYMENTIQ Core Capability | Decision / Action Enabled | Measurable or Estimated Benefit |
|---|---|---|---|---|
| **Chief Financial Officer (CFO)** | Pass-through interchange and scheme fees eroding gross processing margins. | P&L Waterfall & Reconciled Scorecard (`kpi_summary.json`). | Restructure 118 *Margin Drag* merchants from flat-rate blended to IC+ pricing. | **+$45,000.00 annual net contribution recapture** (Estimated). |
| **VP of Payments & Operations** | Unmonitored $13.4M checkout decline leakage forfeiting customer demand. | Payment Performance Funnel & Decline Code Taxonomy. | Deploy 24-hr retry routing for Code 51 and secondary gateway routing for Code 91. | **+$103,334.06 recoverable net revenue** ($4.13M GTV) (Modeled). |
| **Head of Risk & Fraud** | Coordinated bot attacks & chargeback scheme fines. | Unsupervised Isolation Forest (PR-AUC 0.502) & Risk Scoring. | Automatic CAPTCHA and 3DS step-up on transactions scoring $\ge 0.75$. | Intercepts card-testing bursts while maintaining **12.17 bps dispute ratio** (Simulated). |
| **Commercial Merchant Lead**| Lack of visibility into merchant-level yield. | 4-Quadrant Merchant Opportunity Matrix (`v_merchant_opportunity_matrix`). | Protect 482 *Core Anchors* with volume tier discounts; restructure 118 *Margin Drag* accounts. | HHI portfolio concentration maintained at **44.3** (healthy) (Calculated). |
| **CRM / Growth Director** | Cardholder churn after initial transaction. | 12-Month Triangular Cohort Retention Matrix & RFM Quintiles. | Priority re-engagement campaigns targeting 16.4% of cardholders in *At Risk* segment. | Protects top two segments driving **58.4% of volume ($70.7M)** (Calculated). |
| **Support Operations Manager**| High ticket volume driven by checkout failures. | Operational Support SLA Matrix (`v_operational_support_metrics`). | Automated decline messaging deflecting ~40% of tier-1 decline inquiry tickets. | Reduces **14.8% SLA breach rate** and deflects ~880 tickets annually (Potential). |

---

## 10. Data Reconciliation Matrix (0.00% Drift Verification)

A dedicated reconciliation engine ([`python/pipeline/reconciliation.py`](python/pipeline/reconciliation.py)) audits the entire pipeline to verify zero data loss or financial drift across all 5 architectural tiers:

| Metric | Raw Parquet (L1) | Clean Parquet (L2) | PostgreSQL DW (L3) | DuckDB Analytics (L4) | Power BI Export (L5) | Drift % | Audit Status |
|---|---|---|---|---|---|---|---|
| **Transaction Attempts** | 1,000,000 | 1,000,000 | 1,000,000 | 1,000,000 | 1,000,000 | **0.00%** | **RECONCILED** |
| **Gross Transaction Value**| $134,531,743.69 | $134,531,743.69 | $134,531,743.69 | $134,531,743.69 | $134,531,743.69 | **0.00%** | **RECONCILED** |
| **Settled STV** | $121,120,030.80 | $121,120,030.80 | $121,120,030.80 | $121,120,030.80 | $121,120,030.80 | **0.00%** | **RECONCILED** |
| **Net Retained Revenue** | $803,472.60 | $803,472.60 | $803,472.60 | $803,472.60 | $803,472.60 | **0.00%** | **RECONCILED** |
| **Approved Authorizations** | 911,844 | 911,844 | 911,844 | 911,844 | 911,844 | **0.00%** | **RECONCILED** |
| **Chargeback Disputes** | 1,110 | 1,110 | 1,110 | 1,110 | 1,110 | **0.00%** | **RECONCILED** |

---

## 11. Quickstart & How to Run

### Prerequisites
- Python 3.10+ (Tested on Python 3.14.6)
- Git 2.40+
- (Optional) PostgreSQL 16 server or DuckDB (bundled automatically)

### 1. Installation
```bash
# Clone the repository
git clone https://github.com/hriday-sobti/PAYMENTIQ.git
cd PAYMENTIQ

# Install required dependencies
pip install -r requirements.txt

# Copy environment template
cp .env.example .env
```

### 2. Execute Full End-to-End Pipeline
Run the single master orchestration script to execute all 19 pipeline stages (data generation, validation, warehouse loading, analytics, Power BI export, reconciliation, report generation, and tests):
```bash
python run_all.py
```

### 3. Run Automated Tests
```bash
python -m pytest tests/ -q
```

### 4. Launch Interactive Natural-Language Query Console
```bash
python -m ai.assistant_cli
```

### 5. Explore in Power BI Desktop
Open [`powerbi/PAYMENTIQ.pbip`](powerbi/PAYMENTIQ.pbip) directly in Power BI Desktop to interact with the 6-page dashboard.

---

## 12. License & Authorship
- **Author:** PAYMENTIQ Analytics Engineering
- **License:** MIT License — See `LICENSE` for details.
- **Disclosure:** Empirically calibrated dataset generated for benchmarking and system demonstration.
