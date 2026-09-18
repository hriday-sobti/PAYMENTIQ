# PAYMENTIQ | Power BI Business Intelligence Architecture & Specification

**Project Name:** PAYMENTIQ Power BI Executive Analytics Suite  
**File Format:** Power BI Project (`.pbip` / Tabular Model Definition)  
**Report Pages:** 6 Interactive Multi-Dimensional Pages  
**Target Audience:** C-Suite, VP of Payments, Head of Risk, Merchant Operations  
**Specification Version:** 1.0.0  

---

## 1. Executive Summary
The PAYMENTIQ Power BI suite transforms 1,000,000+ transactional records and dimensional data into a clean, commercial decision cockpit. The reporting architecture adheres strictly to pre-attentive cognitive visualization principles, pure star schema modeling, and verified DAX business measures.

---

## 2. Dimensional Data Model & Star Schema Relationships

```
              ┌─────────────────────┐
              │  dim_customers      │
              │  customer_key (PK)  │
              └──────────┬──────────┘
                         │ 1
                         │ *
┌─────────────────────┐  │   ┌─────────────────────┐
│  dim_merchants      │  │   │  dim_dates          │
│  merchant_key (PK)  ├──┼───┤  date_key (PK)      │
└──────────┬──────────┘  │   └──────────┬──────────┘
           │ 1           │              │ 1
           │ *           │              │ *
    ┌──────┴─────────────┴──────────────┴──────┐
    │          fact_transactions               │
    │  date_key, merchant_key, customer_key... │
    └──────┬────────────────────────────┬──────┘
           │ *                          │ *
           │ 1                          │ 1
┌──────────┴───────────────┐ ┌──────────┴───────────────┐
│  dim_payment_methods     │ │  dim_decline_codes       │
│  payment_method_key (PK) │ │  decline_code (PK)       │
└──────────────────────────┘ └──────────────────────────┘
```

### Table Relationships Contract
1. `fact_transactions[customer_key] (Many)` $\rightarrow$ `dim_customers[customer_key] (One)`: Unidirectional.
2. `fact_transactions[merchant_key] (Many)` $\rightarrow$ `dim_merchants[merchant_key] (One)`: Unidirectional.
3. `fact_transactions[payment_method_key] (Many)` $\rightarrow$ `dim_payment_methods[payment_method_key] (One)`: Unidirectional.
4. `fact_transactions[date_key] (Many)` $\rightarrow$ `dim_dates[date_key] (One)`: Unidirectional, marked as Date Table.
5. `fact_transactions[decline_code] (Many)` $\rightarrow$ `dim_decline_codes[decline_code] (One)`: Unidirectional.
6. `fact_disputes[merchant_key] (Many)` $\rightarrow$ `dim_merchants[merchant_key] (One)`: Unidirectional.
7. `fact_support_cases[customer_key] (Many)` $\rightarrow$ `dim_customers[customer_key] (One)`: Unidirectional.

---

## 3. 6-Page Interactive Dashboard Specification

### Page 1: Executive Overview
- **Objective:** High-level strategic health check of payment processing, top-line settled volume, margin retention, and regional performance.
- **Visuals:**
  1. *Top KPI Banner:* 5 Executive cards (`[GTV]`, `[Settled STV]`, `[Authorization Rate %]`, `[Net Revenue]`, `[Contribution Margin %]`).
  2. *Central Trend Combo Visual:* 12-Month Bar and Line chart tracking Monthly Settled GTV ($M) on primary axis and Net Revenue ($K) on secondary axis.
  3. *Category Composition:* Horizontal bar chart ranking settled volume across merchant categories.
  4. *Regional Conversion Scorecard:* Tabular breakdown by country (`total_gtv`, `auth_rate_pct`, `net_revenue`, `avg_latency_ms`).

### Page 2: Payment Performance
- **Objective:** Diagnostic deep dive into authorization funnels, decline codes, network routing, and card rails.
- **Visuals:**
  1. *Payment Conversion Funnel:* Horizontal stage funnel (`Initiated` $\rightarrow$ `Reached Gateway` $\rightarrow$ `Authorized` $\rightarrow$ `Retained`).
  2. *Rail Authorization Scorecard:* Column chart comparing authorization rates across Visa, Mastercard, Amex, Wallets, and Bank Transfers.
  3. *Decline Taxonomy Donut:* Slices showing proportion of soft (retryable) vs. hard (terminal) declines.
  4. *Multi-Level Matrix Drilldown:* `Country` $\rightarrow$ `Category` $\rightarrow$ `Method` $\rightarrow$ `Device`.

### Page 3: Customer Intelligence
- **Objective:** Cardholder behavioral segmentation, 12-month acquisition cohort decay, and Customer Lifetime Value (CLV).
- **Visuals:**
  1. *RFM Segment Bar Visual:* Value contribution breakdown across the 7 RFM segments (*Champions*, *Loyal*, *At Risk*, etc.).
  2. *Cohort Retention Matrix:* Triangular 12-month retention heatmap tracking active cardholder recurrence.
  3. *CLV Scatter Plot:* Historical Annual Spend vs. Projected 24-Month CLV.
  4. *At-Risk Intervention Queue:* Table of high-monetary customers whose recency exceeds 120 days.

### Page 4: Merchant Intelligence
- **Objective:** Commercial portfolio profitability, risk-adjusted margin analysis, and strategic positioning.
- **Visuals:**
  1. *4-Quadrant Opportunity Matrix:* Log-scaled scatter plot of Settled Volume vs. Net Contribution Margin %, partitioned by portfolio medians.
  2. *Quadrant GTV Composition:* Donut visual illustrating volume share of *Core Anchors*, *Growth Prospects*, and *Margin Drag*.
  3. *Scheme Monitoring Compliance Table:* Table flagging any merchants approaching or exceeding the 90 bps dispute threshold.

### Page 5: Risk & Anomaly Monitoring
- **Objective:** Surveillance of operational abnormalities, card-testing attacks, and fraud risk score distributions.
- **Visuals:**
  1. *Risk Score Histogram:* Column distribution of composite risk scores (0–1000).
  2. *Dispute Exposure by MCC:* Bar chart illustrating chargeback basis points across merchant categories.
  3. *Priority Anomaly Review Queue:* Grid of transactions flagged by the Isolation Forest model with anomaly scores $\ge 0.75$.

### Page 6: Management Action Center ("WHAT SHOULD MANAGEMENT INVESTIGATE?")
- **Objective:** Action-oriented operational cockpit translating analytics into concrete commercial remediation steps.
- **Visuals:**
  1. *Priority Action Card 1:* Smart Retry Routing (Addressable Impact: **+$103K Net Revenue**).
  2. *Priority Action Card 2:* Dynamic 3DS Authentication Optimization (Addressable Impact: **+350 bps Auth Uplift**).
  3. *Priority Action Card 3:* Margin Drag Contract Migration (Addressable Impact: **+$45K Contribution**).
  4. *Action Backlog Table:* Prioritized backlog detailing Observation, Driver, Financial Impact, and Prescribed Action.

---

## 4. How to Open and Refresh in Power BI Desktop

1. Open **Power BI Desktop**.
2. Select **File $\rightarrow$ Open report** and browse to `powerbi/PAYMENTIQ.pbip` (or import files from `powerbi/export_data/`).
3. Power BI Desktop will parse `PAYMENTIQ.Dataset/model.bim` and automatically establish all tables, relationships, and calculated measures.
4. If prompted for data source path, point to `powerbi/export_data/` directory.
5. Click **Home $\rightarrow$ Refresh** to refresh the visual dashboard.
