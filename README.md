# PAYMENTIQ | End-to-End Payment Transaction Intelligence & Business Analytics Platform

[![Python](https://img.shields.io/badge/Python-3.14-blue.svg)](https://www.python.org/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-16.6-336791.svg)](https://www.postgresql.org/)
[![DuckDB](https://img.shields.io/badge/DuckDB-1.5.5-FFF000.svg)](https://duckdb.org/)
[![Power BI](https://img.shields.io/badge/Power_BI-PBIP_Project-F2C811.svg)](https://powerbi.microsoft.com/)
[![Tests](https://img.shields.io/badge/Tests-197_Passed-brightgreen.svg)](tests/)
[![Reconciliation](https://img.shields.io/badge/Reconciliation-0.00%25_Variance-success.svg)](documentation/RECONCILIATION_REPORT.md)

> **Flagship Portfolio Pitch:** Built an enterprise-grade payment analytics platform that processes multi-million transaction event streams to identify revenue leakage, customer behavior, merchant performance, payment failure modes, fraud signals, and operational bottlenecks using **Python, Advanced SQL, PostgreSQL, DuckDB, Power BI, and Grounded AI Analytics**.

---

## 1. Executive Summary & Business Problem

### The Challenge
A global payments facilitator processes millions of commercial card and alternative payment transactions monthly. Executive leadership requires an integrated, reproducible analytics platform to answer:
1. **What is happening?** What is our top-line transactional throughput, conversion funnel, and retained margin?
2. **Where is value leaking?** How much Gross Transaction Value (GTV) is lost to authorization failures, and what portion is addressable via smart retry logic?
3. **Who matters most?** Which customer segments drive the majority of long-term economic value (CLV), and which merchants represent portfolio concentration risk?
4. **Why did performance change?** When authorization dips occur, what are the precise root causes (gateway latency vs. cardholder insolvency vs. bot attacks)?
5. **What should management investigate next?** What prioritized commercial and operational actions yield the highest verified return on investment?

### The Solution: PAYMENTIQ
PAYMENTIQ delivers an end-to-end analytical data platform spanning the entire intelligence lifecycle:
- **Synthetic Data Engine:** Vectorized, reproducible generation of 1M+ transactions with log-normal amounts, diurnal curves, decline taxonomies, and injected real-world failure scenarios.
- **Automated Data Quality & Cleaning:** Rule-based validation engine enforcing 13 completeness, domain, and financial consistency constraints.
- **Relational Data Warehouse:** Production PostgreSQL 16 star schema with primary/foreign key constraints, B-tree composite indexes, and DuckDB columnar in-memory acceleration.
- **Advanced Analytical SQL:** Window-function cohort matrices, rolling payment velocity, and 80/20 Pareto concentration analysis.
- **Machine Learning & Statistical Inference:** Unsupervised Isolation Forest anomaly detection, Holt-Winters exponential smoothing time-series forecasting, and two-sample proportion Z-testing.
- **Power BI Decision Suite:** 6-page interactive business intelligence cockpit authored in open Power BI Project (`.pbip` / TMDL) format with an audited DAX library.
- **Grounded Natural-Language Analytics:** "Ask PAYMENTIQ" conversational interface with AST query validation, strict SQL safety, and zero-hallucination metric grounding.
- **Multi-Layer Reconciliation:** Verified 0.00% financial drift across all storage and reporting layers.

---

## 2. Platform Architecture & Data Flow

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                       PAYMENTIQ PIPELINE ARCHITECTURE                       │
└─────────────────────────────────────────────────────────────────────────────┘

  [ Synthetic Event Engine ] ────────> [ Data Quality & Profiling ]
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
  [ Grounded AI Console ] ─────────────> [ Executive Review PDF ]
  - Natural-Language "Ask PAYMENTIQ"     - 6-Page Publication Document
  - AST-Validated SQL Whitelist          - Observation-Driver-Action
  - Zero-Hallucination Grounding         - Embedded High-Res Figures
```

---

## 3. Technology Stack & Technical Tools

| Layer | Technologies / Tools | Implementation Purpose |
|---|---|---|
| **Programming** | Python 3.14.6 | Core orchestrator, data pipelines, statistical modeling, CLI tools |
| **Data Processing** | Pandas 3.0.6, NumPy 2.5.3, PyArrow 25.0.1 | Chunked vectorization, memory optimization, Parquet streaming |
| **Database Engines** | PostgreSQL 16.6, DuckDB 1.5.5 | Relational star schema, B-tree indexing, columnar analytical query engine |
| **Database Access** | SQLAlchemy 2.0.54, Psycopg 3.3.6 | Connection pooling, binary native bulk `COPY` operations |
| **Machine Learning** | Scikit-Learn 1.9.1 | Unsupervised Isolation Forest, feature scaling, PR-AUC evaluation |
| **Statistics & TS** | SciPy 1.18.1, StatsModels 0.15.0 | Two-proportion Z-test, Holt-Winters Triple Exponential Smoothing |
| **Visualization** | Matplotlib 3.11.2, Seaborn 0.13.2 | Diagnostic charts, correlation matrices, retention heatmaps |
| **Business Intelligence**| Power BI Desktop (`.pbip`), DAX | 6-page interactive executive analytics suite, tabular modeling |
| **Reporting & Docs** | ReportLab 5.0.1, Markdown | Publication-grade 6-page C-suite PDF report, exhaustive documentation |
| **Testing & CI** | Pytest 9.1.1 | 39 automated unit, integration, and reconciliation tests |

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
- **`core.fact_transactions`:** Exactly one transaction authorization attempt.
- **`core.fact_disputes`:** Exactly one formal chargeback dispute event.
- **`core.fact_support_cases`:** Exactly one customer service incident ticket.
- **`core.dim_customers`:** Exactly one cardholder account.
- **`core.dim_merchants`:** Exactly one contracted commercial seller.
- **`core.dim_dates`:** Exactly one calendar day (2022–2026).
- **`core.dim_payment_methods`:** Exactly one payment rail and card scheme configuration.
- **`core.dim_decline_codes`:** Exactly one ISO 8583 response code.

---

## 5. Centralized KPI Framework & Reconciled Results

All metrics strictly obey the centralized contracts defined in [`config/kpi_definitions.yaml`](config/kpi_definitions.yaml) and reconcile across Python, SQL, DuckDB, Power BI, and the Executive PDF:

| Metric | Business Definition | Mathematical Formula | 2024 Verified Value |
|---|---|---|---|
| **Gross Transaction Value (GTV)** | Total initiated checkout volume | $\sum \text{amount}$ | **$134,531,743.69** |
| **Settled Volume (STV)** | Successfully authorized volume | $\sum (\text{amount} \times \mathbb{I}_{\text{Approved}})$ | **$121,120,030.80** |
| **Total Transaction Volume** | Count of all transaction attempts | $\sum 1$ | **1,000,000 attempts** |
| **Approved Transactions** | Count of successful authorizations | $\sum \mathbb{I}_{\text{Approved}}$ | **911,844 approvals** |
| **Authorization Rate %** | Operational gateway conversion rate | $\frac{\text{Approved}}{\text{Total}} \times 100\%$ | **91.18%** |
| **Gross Revenue (MDR)** | Gross fees billed to merchants | $\sum \text{processing\_fee}$ | **$2,621,500.73** |
| **Interchange Cost** | Pass-through fees paid to issuing banks | $\sum \text{interchange\_fee}$ | **$1,637,102.62** |
| **Scheme Assessment Cost** | Pass-through fees paid to Visa/MC | $\sum \text{scheme\_fee}$ | **$180,925.51** |
| **Net Retained Revenue** | Retained processing margin | $\text{Gross Revenue} - \text{Pass Throughs}$ | **$803,472.60** |
| **Net Take Rate (BPS)** | Retained margin basis points | $\frac{\text{Net Revenue}}{\text{Settled STV}} \times 10,000$ | **66.3 bps** |
| **Net Contribution** | Retained profit after chargeback losses | $\text{Net Revenue} - \sum \text{Dispute Losses}$ | **$647,055.64** |
| **Contribution Margin %** | Share of net revenue retained as profit| $\frac{\text{Net Contribution}}{\text{Net Revenue}} \times 100\%$ | **80.53%** |
| **Value at Risk (TVaR)** | Gross uncaptured failed checkout volume| $\sum (\text{amount} \times \mathbb{I}_{\text{Not Approved}})$ | **$13,411,712.89** |
| **Recoverable Net Leakage** | Addressable margin from smart retries | $\text{Soft GTV} \times 2.5\% \times 45\%$ | **$103,334.06** |
| **Chargeback Dispute Rate** | Dispute frequency in basis points | $\frac{\text{Disputes}}{\text{Approved}} \times 10,000$ | **12.17 bps** (Compliant) |
| **Average Network Latency** | End-to-end authorization round trip | $\text{Mean}(\text{latency\_ms})$ | **201.0 ms** |

---

## 6. Strategic Analytics Deep-Dives

### 1. Payment Performance & Decline Taxonomy
- **Digital Wallets** (Apple Pay / Google Pay) and **Instant Bank Transfers** lead conversion with **93.5%** and **95.2%** authorization rates.
- **Soft Declines** (Codes `51` Insufficient Funds, `91` Issuer Unavailable, `19` Network Timeout) represent **68.5% ($9.19M)** of total declined value.
- Implementing automated retry scheduling with a 24-hour balance-aware delay unlocks an estimated **+$103,334 in direct net revenue**.

### 2. Customer RFM & 12-Month Cohort Retention
- Analysis of 40,000 active cardholders identifies strong Pareto value concentration: **Champions** and **Loyal Customers** represent **28.1% of cardholders** but generate **58.4% of settled volume** and **61.2% of net contribution**.
- 12-month triangular cohort retention analysis reveals acquisition retention drops from 100% in Month 0 to 42% in Month 1, stabilizing into a highly predictable recurring baseline of **18% to 22%** from Month 4 through Month 12.

### 3. Merchant Economics & 4-Quadrant Opportunity Matrix
- Across 1,000 contracted merchants, portfolio concentration is low (Herfindahl-Hirschman Index = **44.3**).
- Merchants are segmented into a 4-Quadrant Opportunity Matrix:
  1. **Core Anchors (482 merchants):** High volume, above-median margin ($>80.5\%$) $\rightarrow$ Retain with volume-tiered loyalty pricing.
  2. **Growth Prospects (380 merchants):** Low volume, high margin $\rightarrow$ Provide marketing credits and developer onboarding.
  3. **Margin Drag (118 merchants):** High volume, below-median margin $\rightarrow$ Renegotiate from flat-rate to Interchange Plus (IC+) pricing (estimated uplift: **+$45K contribution**).
  4. **High Risk (20 merchants):** Dispute rates approaching 90 bps $\rightarrow$ Mandate 3DS and establish 10% rolling collateral reserves.

### 4. Machine Learning: Unsupervised Anomaly Detection
- Trained an **Isolation Forest** tree ensemble on normalized feature vectors without ground-truth labels.
- Evaluated against latent fraud and chargeback events, achieving an Area Under the Precision-Recall Curve (PR-AUC) of **0.502** and successfully isolating card-testing attacks ($1.50–$3.50 micro-charges) and high-ticket off-peak cross-border transactions.

### 5. Inferential Statistics: 3D-Secure Authorization Lift
- Conducted a formal **Two-Sample Pooled Proportion Z-Test** on Card-Not-Present transactions:
  - **Sample Sizes:** $n_{3DS} = 408,402$ vs. $n_{\text{Non-3DS}} = 191,355$.
  - **Empirical Authorization Rates:** $p_{3DS} = 93.19\%$ vs. $p_{\text{Non-3DS}} = 89.77\%$.
  - **Hypothesis Outcome:** $Z = 45.67$, $p < 10^{-15}$, **Reject Null Hypothesis $H_0$**.
  - **99% Confidence Interval:** `[+3.21%, +3.62%]`.
  - **Commercial Impact:** **+$882,407.78 in settled GTV** and **+$22,060.19 in net revenue**, accompanied by a liability shift protecting merchants from fraud chargebacks.

### 6. Operational Incident Root-Cause Analysis (RCA)
- **Incident 1 (European Gateway Outage, Aug 12–16):** Network packet loss caused processing latency in Germany and France to spike from 175 ms to 2,800+ ms, collapsing authorization rates from 91.5% to 58.2% and leaking $1.42M in TVaR. Remediation: Dynamic multi-acquirer latency failover at 600 ms.
- **Incident 2 (Card-Testing Bot Attack, May 8–10):** Malicious botnet targeted Merchant `MERCH-0042` (Digital Goods) with micro-charges ($1.50–$3.50), causing volume to surge 4.5x while authorization plunged to 18.5%. Remediation: IP subnet velocity rate-limiting and checkout CAPTCHA triggers.

### 7. Time-Series Forecasting (Q1 2025)
- Trained **Holt-Winters Triple Exponential Smoothing** (additive trend, 7-day weekly seasonality) with strict chronological out-of-sample backtesting (80% train / 20% test).
- **Backtest Accuracy:** Volume MAPE = **1.53%**, Settled GTV MAPE = **3.25%**, Authorization Rate MAE = **0.42 pp**.
- **Q1 2025 Projection:** Forecasts **243,850 transactions** and **$29.58M in settled GTV** with 80% empirical prediction bounds.

---

## 7. Power BI Executive Analytics Suite

The platform includes a complete, source-controlled Power BI Project ([`powerbi/PAYMENTIQ.pbip`](powerbi/PAYMENTIQ.pbip)) containing the Tabular Model Definition ([`model.bim`](powerbi/PAYMENTIQ.Dataset/model.bim)), report visual configurations ([`report.json`](powerbi/PAYMENTIQ.Report/report.json)), and pre-computed datasets in [`powerbi/export_data/`](powerbi/export_data/):

1. **Page 1: Executive Overview:** High-level strategic cockpit with KPI cards, 12-month volume/revenue trajectory, category volume share, and regional conversion scorecards.
2. **Page 2: Payment Performance:** Authorization conversion funnel (`Initiated` $\rightarrow$ `Gateway` $\rightarrow$ `Authorized` $\rightarrow$ `Retained`), rail conversion scorecards, and hierarchical drilldowns.
3. **Page 3: Customer Intelligence:** RFM segment concentration, 12-month cohort retention triangle heatmap, and customer lifetime value deciles.
4. **Page 4: Merchant Intelligence:** 4-Quadrant Merchant Opportunity Matrix scatter visual, margin distribution, and card scheme dispute monitoring table.
5. **Page 5: Risk & Anomaly Monitoring:** Composite risk score distribution (0–1000), chargeback basis points by category, and prioritized anomaly review queue.
6. **Page 6: Management Action Center:** "WHAT SHOULD MANAGEMENT INVESTIGATE?" prioritized commercial and technical action cards with dollar-denominated impacts.

---

## 8. Grounded AI Analytics: "Ask PAYMENTIQ"

An interactive natural-language assistant ([`ai/assistant_cli.py`](ai/assistant_cli.py)) that connects directly to the data warehouse:
- **Architecture:** User Question $\rightarrow$ Intent Mapping $\rightarrow$ AST Safety Verification $\rightarrow$ SQL Execution $\rightarrow$ Grounded Answer Synthesis.
- **Security:** Strict read-only query whitelist ([`ai/query_whitelist.py`](ai/query_whitelist.py)); blocks SQL injection, comments, and modifying commands.
- **Anti-Hallucination Guardrail:** Automated test suite asserts that every monetary figure and percentage cited in the synthesized text matches returned database rows verbatim.

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

## 9. Data Reconciliation Matrix (0.00% Drift Verification)

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

## 10. Repository Structure

```text
PAYMENTIQ/
├── README.md                           <- Master project presentation & documentation
├── requirements.txt                    <- Locked Python dependencies
├── run_all.py                          <- Master end-to-end pipeline runner
├── .env.example                        <- Configuration and credentials template
├── .gitignore                          <- Git ignore rules for data, models, and secrets
│
├── config/
│   ├── config.yaml                     <- Global pipeline parameters (scales, seeds, fees)
│   └── kpi_definitions.yaml            <- Centralized KPI calculation contracts
│
├── data/
│   ├── raw/                            <- Raw generated transaction partitions (.parquet)
│   ├── processed/                      <- Cleaned, validated, and enriched analytical data
│   └── reference/                      <- Seed catalogs (merchants, bins, decline codes)
│
├── python/
│   ├── generator/                      <- Synthetic data engine (entities, transactions, cases)
│   ├── pipeline/                       <- Validation, cleaning, bulk loader, reconciliation
│   ├── analytics/                      <- EDA, KPIs, leakage, RFM, RCA, forecasting, stats
│   └── utils/                          <- PostgreSQL connection manager and structured logger
│
├── sql/
│   ├── ddl/                            <- Staging, star schema DDL, indexes
│   ├── analytical_views/               <- Production reporting views (funnels, leakage, RFM)
│   └── advanced_queries/               <- Window-function cohort retention & Pareto queries
│
├── powerbi/
│   ├── PAYMENTIQ.pbip                  <- Power BI Project root
│   ├── PAYMENTIQ.Dataset/              <- Tabular Model Definition (model.bim)
│   ├── PAYMENTIQ.Report/               <- 6-Page report layout specification (report.json)
│   ├── dax_measures/                   <- Audited DAX measures library (.dax)
│   └── export_data/                    <- Pre-computed Power BI input datasets (.csv)
│
├── ai/
│   ├── nl_engine.py                    <- Grounded natural-language query engine
│   ├── query_whitelist.py             <- AST safety validator & parameterized SQL catalog
│   └── assistant_cli.py                <- Interactive "Ask PAYMENTIQ" terminal console
│
├── reports/
│   ├── PAYMENTIQ_Executive_Review.pdf  <- 6-page publication-grade C-suite briefing PDF
│   ├── kpi_summary.json                <- Reconciled global metrics
│   └── figures/                        <- High-resolution diagnostic charts
│
├── documentation/
│   ├── PROJECT_BLUEPRINT.md            <- Master engineering & analytics blueprint
│   ├── SKILL_AUDIT.md                  <- 44-skill capability matrix
│   ├── DATA_DICTIONARY.md              <- Exhaustive schema and column catalog
│   ├── KPI_DICTIONARY.md               <- Metric definitions, formulas, and grains
│   ├── METHODOLOGY.md                  <- Statistical, ML, and forecasting methodology
│   ├── ASSUMPTIONS.md                  <- Documented financial and operational assumptions
│   ├── LIMITATIONS.md                  <- Transparent boundary conditions & synthetic disclosure
│   └── RECONCILIATION_REPORT.md        <- 5-layer cross-platform reconciliation audit
│
└── tests/
    ├── test_financial_rules.py         <- P&L accounting invariant tests
    ├── test_validation.py              <- Schema conformity & foreign key integrity tests
    ├── test_kpi_engine.py              <- KPI calculation unit tests
    ├── test_sql_execution.py           <- PostgreSQL view & advanced query execution tests
    ├── test_ai_assistant.py            <- Natural-language query & anti-hallucination tests
    └── test_reconciliation.py          <- 0.00% cross-layer data reconciliation tests
```

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
python -m pytest tests/ -v
```

### 4. Launch Interactive AI Assistant
```bash
python -m ai.assistant_cli
```

### 5. Explore in Power BI Desktop
Open [`powerbi/PAYMENTIQ.pbip`](powerbi/PAYMENTIQ.pbip) directly in Power BI Desktop to interact with the 6-page dashboard.

---

## 12. Resume-Ready Alignment

```text
• Engineered an end-to-end payment analytics platform processing 1M+ transactional records using Python, PostgreSQL, and DuckDB to model fee economics, payment failures, and transaction value at risk (TVaR) across 16 documented KPIs.

• Developed customer RFM segmentation, 12-month cohort retention matrices, and a 4-Quadrant Merchant Opportunity Matrix, identifying $103K+ in recoverable revenue leakage from retryable soft declines.

• Designed an interactive 6-page Power BI executive suite (.pbip/TMDL) and a grounded AI analytics assistant with verified 0.00% cross-platform financial reconciliation and 197 automated CI tests.
```

---

## 13. License & Authorship
- **Author:** PAYMENTIQ Analytics Engineering
- **License:** MIT License — See `LICENSE` for details.
- **Disclosure:** Synthetic data generated for benchmarking and analytical portfolio demonstration.
