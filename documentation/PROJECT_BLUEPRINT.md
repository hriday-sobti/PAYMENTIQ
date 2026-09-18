# PAYMENTIQ | Master Architecture Blueprint & Engineering Specification

**Document Version:** 1.0.0  
**Status:** Approved & Grounded  
**Project Lead:** Autonomous Analytics & Engineering Agent  
**Date:** 2026-09-18  

---

## 1. Discovered Local Environment
- **Operating System:** Windows 11 Home (x64, build 10.0.26200).
- **Compute Architecture:** AMD Ryzen 7 7735HS with Radeon Graphics (16 logical cores, 3.2 GHz base).
- **Active User:** Non-elevated Windows user profile (`C:\Users\hrida`).
- **Workspace Directory:** `C:\Users\hrida\projects\data_analyst\PAYMENTIQ`.

---

## 2. Available Software & Tools
- **Version Control:** Git version 2.55.0.windows.3.
- **Package Managers:** Windows Package Manager (`winget.exe`), Python `pip 26.1.2`.
- **Shells & Scripting:** Windows PowerShell, Windows Command Prompt (`cmd.exe`), Python execution runtime.
- **Development Harness:** Oh My Pi (omp v18.2.5).

---

## 3. Available Python Runtime
- **Version:** Python 3.14.6 (64-bit).
- **Path:** `C:\Users\hrida\AppData\Local\Python\pythoncore-3.14-64\python.exe`.

---

## 4. Available Analytical Packages
- **Core Numerical & Analytical:** `numpy 2.5.3`, `pandas 3.0.6`, `scipy 1.18.1`.
- **Machine Learning & Modeling:** `scikit-learn 1.9.1`, `statsmodels 0.15.0`.
- **Data Visualization:** `matplotlib 3.11.2`, `seaborn 0.13.2`.
- **Database & Storage Engines:** `duckdb 1.5.5`, `sqlalchemy 2.0.54`, `psycopg 3.3.6` (binary driver), `pyarrow 25.0.1`.
- **Reporting & Excel:** `reportlab 5.0.1`, `openpyxl 3.1.5`.
- **Testing & Quality Assurance:** `pytest 9.1.1`.

---

## 5. PostgreSQL Availability & Strategy
- **Status:** Portable PostgreSQL 16.6-1 server provisioned directly into `C:\Users\hrida\.local\pgsql`.
- **Architecture:** Standalone, zero-privilege user-space PostgreSQL instance.
- **Port:** Configured to port `5433` (isolated from any potential default 5432 conflict).
- **Cluster Initialization:** Managed via automated Python lifecycle scripts (`initdb`, `pg_ctl start/stop/status`).
- **Complementary Engine:** In-process `DuckDB 1.5.5` deployed in parallel for vectorized Parquet processing, extreme high-speed out-of-core aggregations on 5M+ records, and cross-engine analytical reconciliation.

---

## 6. Git Availability & Strategy
- **Status:** Git 2.55.0 installed and verified.
- **Strategy:** Granular, atomic conventional commits per engineering phase.
- **Asset Control:** Strict `.gitignore` excluding raw multi-gigabyte CSVs, database cluster files, environment secrets, and bytecode while retaining reproducible generation seeds, schema definitions, and analytical assets.

---

## 7. Docker Availability & Mitigation
- **Status:** Docker daemon is not installed or available on this host.
- **Mitigation Strategy:** Native portable PostgreSQL 16 user-space service and embedded Python-native runtime. Zero Docker dependency required for 100% full-stack reproducibility on Windows host.

---

## 8. Power BI Constraints & Implementation
- **Host Constraint:** Headless automated script execution cannot drive the proprietary Power BI Desktop Windows GUI directly during CI/terminal runs.
- **Engineering Solution:** 
  1. Full Power BI Project (`.pbip`) format authored programmatically using Tabular Model Definition Language (TMDL) and M-PowerQuery expressions.
  2. Standalone `.pbit` template and data connector scripts that load directly into Power BI Desktop with one click.
  3. Formatted DAX measures catalog with explicit evaluation contexts (`CALCULATE`, `KEEPFILTERS`, `SUMX`, `ALL`).
  4. Publication-quality visual mockups and layout definitions matching the exact 6-page dashboard specification.

---

## 9. Comprehensive Skill Matrix
- Formally documented in `documentation/SKILL_AUDIT.md` covering all 44 mandatory technical domains with explicit baselines, targets, gap remediations, and validation methods.

---

## 10. Identified Knowledge Gaps
1. High-throughput data synthesis preserving non-linear payment failure interactions across 5,000,000+ records without memory exhaustion.
2. Defensible distinction between operational payment declines (soft vs. hard), chargebacks, and technical latency.
3. Separation of financial metrics: Gross Transaction Value (GTV) vs. Gross Merchant Discount Rate (MDR) vs. Interchange/Scheme Cost vs. Net Revenue vs. Net Contribution.
4. Programmatic generation of valid Power BI Project (`.pbip` / TMDL) models without relying on manual Desktop clicks.
5. Construction of a secure, hallucination-free grounded Natural-Language SQL analytics engine.

---

## 11. Gap Remediation Plan
1. **Streaming Generator Architecture:** Implement chunked batch generators (`chunksize=100,000`) utilizing NumPy's vectorized `default_rng()` streaming directly into compressed Parquet chunks and PostgreSQL `COPY`.
2. **Domain-Specific Payment Taxonomy:** Map industry-standard ISO 8583 response codes (e.g. `00` Approved, `05` Do Not Honor, `51` Insufficient Funds, `54` Expired Card, `91` Issuer Unavailable) to categorize retryable soft declines vs. terminal hard declines.
3. **Formal Financial Waterfall:** Encode a mathematically rigorous waterfall where every fee type (interchange, scheme, acquirer markup) has an explicit formula reconciling down to Net Contribution.
4. **TMDL & DAX Specification:** Author complete TMDL semantic schemas and verified DAX measure libraries that can be opened directly in Power BI Desktop or deployed via Tabular Editor.
5. **Grounded NL-to-SQL Engine:** Build an AST-validated query mapper with whitelisted analytical views, parameter binding, read-only transaction locks, and deterministic JSON synthesis.

---

## 12. Proposed Repository Structure

```text
PAYMENTIQ/
├── README.md                           <- Portfolio-grade project presentation & documentation
├── requirements.txt                    <- Locked Python dependencies
├── .env.example                        <- Configuration and credentials template
├── .gitignore                          <- Git ignore rules for data, models, and secrets
├── run_all.py                          <- Master orchestration script for end-to-end pipeline
│
├── config/
│   ├── config.yaml                     <- Global pipeline parameters (seeds, scale, db)
│   └── kpi_definitions.yaml            <- Centralized KPI calculation contracts
│
├── data/
│   ├── raw/                            <- Raw partitioned generated transaction batches (.parquet)
│   ├── processed/                      <- Cleaned, validated, and enriched analytical data
│   └── reference/                      <- Seed catalogs (merchants, bins, locations, decline codes)
│
├── python/
│   ├── __init__.py
│   ├── generator/                      <- Synthetic data engine
│   │   ├── entities.py                 <- Customer, merchant, terminal entities
│   │   ├── transactions.py             <- Transaction stream & temporal behavioral models
│   │   └── generator.py                <- Main multi-scale generator orchestrator
│   ├── pipeline/
│   │   ├── validation.py               <- Schema, domain, and financial consistency validation
│   │   ├── cleaning.py                 <- Data cleaning, type casting, imputation
│   │   └── loader.py                   <- High-speed PostgreSQL & DuckDB bulk loader
│   ├── analytics/
│   │   ├── kpi_engine.py               <- Standardized metrics calculator
│   │   ├── payment_performance.py      <- Auth rates, decline analysis, latency
│   │   ├── revenue_leakage.py          <- Leakage quantification & value at risk
│   │   ├── customer_intelligence.py    <- RFM segmentation, CLV, cohort retention
│   │   ├── merchant_analytics.py       <- Portfolio economics & opportunity matrix
│   │   ├── anomaly_detection.py        <- Unsupervised risk scoring & Isolation Forest
│   │   ├── root_cause.py               <- Multi-dimensional variance & RCA engine
│   │   ├── forecasting.py              <- Exponential smoothing & time-series models
│   │   └── statistics.py               <- Hypothesis tests, p-values, effect sizes
│   └── utils/
│       ├── db.py                       <- Database connection manager & pool
│       └── logger.py                   <- Structured logging configuration
│
├── sql/
│   ├── ddl/
│   │   ├── 01_staging_tables.sql       <- Staging layer schemas
│   │   ├── 02_core_star_schema.sql     <- Production fact and dimension tables
│   │   └── 03_indexes_partitions.sql   <- Performance indexes and partitioning
│   ├── analytical_views/
│   │   ├── 01_v_payment_performance.sql<- Authorization funnel & routing views
│   │   ├── 02_v_revenue_leakage.sql    <- Financial loss & addressable leakage views
│   │   ├── 03_v_customer_rfm.sql       <- RFM quintiles & retention views
│   │   ├── 04_v_merchant_matrix.sql    <- Merchant contribution & opportunity matrix
│   │   └── 05_v_operational_sla.sql    <- Latency, support cases, and SLA views
│   └── advanced_queries/
│       ├── cohort_retention_matrix.sql <- Window-function triangular cohort matrix
│       ├── rolling_payment_velocity.sql<- 7-day & 30-day customer velocity windows
│       └── dimensional_pareto.sql      <- Cumulative contribution & Pareto analysis
│
├── powerbi/
│   ├── PAYMENTIQ.pbip                  <- Power BI Project root
│   ├── PAYMENTIQ.Report/               <- Layout, theme, visuals, bookmark configs
│   ├── PAYMENTIQ.Dataset/              <- TMDL model definitions, M-queries, relationships
│   ├── dax_measures/                   <- Standalone audited DAX formula library
│   └── export_data/                    <- Pre-computed Power BI input datasets
│
├── ai/
│   ├── __init__.py
│   ├── nl_engine.py                    <- Grounded question interpretation engine
│   ├── query_whitelist.py             <- Parameterized SQL query catalog & AST validator
│   └── assistant_cli.py                <- Interactive "Ask PAYMENTIQ" terminal console
│
├── reports/
│   ├── generate_executive_report.py    <- Automated ReportLab PDF generator
│   ├── figures/                        <- High-resolution analytical charts
│   └── PAYMENTIQ_Executive_Review.pdf  <- 6-page C-suite analytical briefing document
│
├── documentation/
│   ├── PROJECT_BLUEPRINT.md            <- Master engineering and analytics blueprint
│   ├── SKILL_AUDIT.md                  <- 44-skill capability matrix
│   ├── DATA_DICTIONARY.md              <- Comprehensive schema and field catalog
│   ├── KPI_DICTIONARY.md               <- Metric definitions, formulas, and grains
│   ├── METHODOLOGY.md                  <- Statistical and machine learning methodologies
│   ├── ASSUMPTIONS.md                  <- Explicit domain and economic assumptions
│   ├── LIMITATIONS.md                  <- Known platform and data boundaries
│   └── RECONCILIATION_REPORT.md        <- Cross-layer data reconciliation audit
│
└── tests/
    ├── test_generator.py               <- Data generation tests
    ├── test_validation.py              <- Schema and data quality validation tests
    ├── test_financial_rules.py         <- P&L and fee consistency tests
    ├── test_kpi_calculations.py        <- Metric computation unit tests
    ├── test_sql_execution.py           <- Database views & query correctness tests
    └── test_reconciliation.py          <- Python vs. SQL vs. BI reconciliation tests
```

---

## 13. Data Model & Grain Definitions
The platform implements a pure star schema in PostgreSQL and Power BI:

### Fact Tables
1. **`fact_transactions`**
   - **Grain:** Exactly one transaction attempt.
   - **Degenerate Key:** `transaction_id` (UUID).
   - **Foreign Keys:** `customer_key`, `merchant_key`, `date_key`, `time_key`, `payment_method_key`, `terminal_key`.
   - **Measures:** `amount`, `processing_fee`, `interchange_fee`, `scheme_fee`, `latency_ms`.
   - **Attributes:** `auth_status` (Approved, Declined, Failed), `decline_reason`, `decline_code`, `is_3ds_authenticated`, `retry_attempt_number`.
2. **`fact_disputes`**
   - **Grain:** Exactly one formal dispute / chargeback event.
   - **Keys:** `dispute_id`, `transaction_id`, `merchant_key`, `dispute_date_key`.
   - **Measures:** `dispute_amount`, `chargeback_fee`.
   - **Attributes:** `dispute_reason` (Fraud, Service Not Provided, Canceled Recurring), `dispute_status` (Open, Won, Lost).
3. **`fact_support_cases`**
   - **Grain:** Exactly one customer service incident related to a transaction or payment issue.
   - **Keys:** `case_id`, `customer_key`, `transaction_id`, `created_date_key`.
   - **Measures:** `resolution_time_minutes`, `customer_satisfaction_score`.
   - **Attributes:** `category`, `severity`, `status`, `sla_breached_flag`.

### Dimension Tables
1. **`dim_customers`**
   - **Grain:** One unique consumer cardholder.
   - **Fields:** `customer_key`, `customer_id`, `signup_date`, `customer_country`, `customer_segment`, `acquisition_channel`, `risk_tier`.
2. **`dim_merchants`**
   - **Grain:** One unique commercial seller / entity.
   - **Fields:** `merchant_key`, `merchant_id`, `merchant_name`, `mcc_code`, `merchant_category`, `merchant_country`, `onboarding_date`, `pricing_tier`.
3. **`dim_payment_methods`**
   - **Grain:** One unique payment rail and configuration.
   - **Fields:** `payment_method_key`, `method_name` (Credit Card, Debit Card, Digital Wallet, BNPL, Instant Bank Transfer), `card_brand` (Visa, Mastercard, Amex), `card_type` (Consumer, Commercial).
4. **`dim_dates`**
   - **Grain:** One calendar day.
   - **Fields:** `date_key`, `full_date`, `year`, `quarter`, `month`, `month_name`, `week_of_year`, `day_of_week`, `is_weekend`, `is_holiday`.

---

## 14. Data Generation Strategy & Multi-Scale Execution
- **Multi-Scale Tiers:**
  - `DEV`: 100,000 transactions (for rapid feature iteration and fast test cycles).
  - `TEST`: 1,000,000 transactions (for performance profiling and regression testing).
  - `FULL`: 5,000,000+ transactions (for portfolio demonstration and final benchmarks).
- **Behavioral Realism:**
  - Log-normal transaction amounts calibrated by Merchant Category Code (e.g. Grocery: $\mu=\$45, \sigma=0.6$; Luxury Goods: $\mu=\$350, \sigma=1.2$).
  - Diurnal and weekly temporal cycles (peak volume 12:00–14:00 and 18:00–21:00; weekend surges for Hospitality/Dining).
  - Realistic authorization rates: Credit Card (~88%), Debit Card (~91%), Digital Wallet (~93%), BNPL (~82%).
  - Decline categorization: 65% soft retryable declines (Insufficient Funds, Timeout), 35% hard terminal declines (Stolen Card, Invalid Account).
  - Embedded realistic scenarios: Injected gateway degradation in specific geographic corridor, seasonal holiday shopping surges, and coordinated card-testing attack pattern on high-risk merchants.

---

## 15. Data Quality Strategy & Validation Rules
- Automated validation pipeline executed before ingestion into the data warehouse:
  1. **Completeness:** Zero missing values in mandatory primary/foreign keys, timestamps, amounts, and statuses.
  2. **Domain Validity:** ISO currency codes (`USD`, `EUR`, `GBP`), valid country codes, MCC codes conforming to standard ISO 18245.
  3. **Financial Consistency:**
     - Non-negative amounts ($> 0.00$).
     - Non-negative fees ($>= 0.00$).
     - Fees must never exceed transaction amount.
     - Approved transactions must have `decline_reason IS NULL`.
     - Declined transactions must have a valid `decline_reason` and `decline_code`.
  4. **Referential Integrity:** 100% of foreign keys in `fact_transactions` resolve to existing records in dimension tables.
  5. **Temporal Consistency:** Dispute creation date must be $\ge$ transaction timestamp.

---

## 16. PostgreSQL Architecture & Tuning
- **Database Name:** `paymentiq_dw`.
- **Schemas:**
  - `staging`: Raw imported staging tables with minimal transformation.
  - `core`: Dimensional star schema (`fact_*`, `dim_*`) with enforced constraints.
  - `analytics`: Production reporting views, materialized aggregates, and KPI tables.
- **Tuning Configuration:**
  - `shared_buffers = 512MB`
  - `work_mem = 64MB`
  - `maintenance_work_mem = 256MB`
  - `effective_io_concurrency = 200`
- **Indexing Strategy:**
  - B-tree indexes on all foreign keys (`customer_key`, `merchant_key`, `date_key`).
  - Composite index on `fact_transactions(merchant_key, date_key, auth_status)` for sub-second dashboard filtering.

---

## 17. Python Architecture & Modularity
- Follows strict separation of concerns across 10 functional modules:
  - `generator/`: Pure data generation engine with zero external database dependencies.
  - `pipeline/`: Data ingestion, Great Expectations-style validation, cleaning, and bulk loading.
  - `analytics/`: Business logic, KPI engine, statistical tests, machine learning models, and forecasting.
  - `utils/`: Reusable database connectors, logging decorators, and configuration loaders.
- Written with PEP 484 type hints, dataclasses for domain entities, and comprehensive exception handling.

---

## 18. SQL Architecture & Query Design
- All analytical queries written with Common Table Expressions (CTEs) for maximum readability and maintainability.
- Advanced window functions utilized for running totals, rank ordering, rolling 7-day authorization rates, and retention matrices:
  - `ROW_NUMBER() OVER (PARTITION BY customer_key ORDER BY timestamp)` for transaction sequence tracking.
  - `AVG(is_approved::int) OVER (PARTITION BY merchant_key ORDER BY date_key ROWS BETWEEN 6 PRECEDING AND CURRENT ROW)` for rolling performance baselines.
  - `NTILE(5) OVER (ORDER BY monetary_value DESC)` for robust quintile scoring.

---

## 19. Unified KPI Framework
- Single source of truth cataloged in `config/kpi_definitions.yaml` and `documentation/KPI_DICTIONARY.md`.
- Core Metrics:
  - **Gross Transaction Value (GTV):** $\sum \text{Amount}$ for all attempted transactions.
  - **Settled Transaction Value (STV):** $\sum \text{Amount}$ for transactions where auth_status = 'Approved'.
  - **Authorization Rate (Auth Rate):** $\frac{\text{Count of Approved Transactions}}{\text{Count of Total Attempted Transactions}} \times 100\%$.
  - **Gross Revenue (MDR):** $\sum \text{Processing Fee}$ earned from merchants.
  - **Net Revenue:** $\text{Gross Revenue} - \sum (\text{Interchange Fee} + \text{Scheme Fee})$.
  - **Net Contribution:** $\text{Net Revenue} - \sum (\text{Chargeback Losses} + \text{Dispute Costs})$.
  - **Transaction Value at Risk (TVaR):** $\sum \text{Amount}$ for declined or failed transactions categorized by recoverability.
  - **Chargeback Rate:** $\frac{\text{Count of Chargebacks}}{\text{Count of Approved Transactions}} \times 100\%$.

---

## 20. Customer Analytics Architecture
- **RFM Engine:** Computes Recency (days since last transaction), Frequency (count of approved transactions in 365 days), and Monetary Value (total settled amount). Ranks into 5 quintiles (scores 1–5) and maps to 8 standardized behavioral segments.
- **Customer Lifetime Value (CLV):** 
  - *Historical Realized Value:* Cumulative net contribution per customer.
  - *Retention-Adjusted Forward CLV:* $CLV = \sum_{t=1}^{T} \frac{\text{Monthly Contribution} \times r^t}{(1 + d)^t}$ where $r$ is empirical cohort retention rate and $d$ is discount rate.
- **Cohort Retention Matrix:** Monthly triangle retention analysis tracking active customer persistence from month 0 to month 12.

---

## 21. Merchant Analytics Architecture
- **Portfolio Health Metrics:** Merchant GTV, settled volume, net contribution, and dispute frequency.
- **Concentration Analysis:** Herfindahl-Hirschman Index (HHI) calculated across merchant categories to monitor portfolio dependency.
- **Merchant Opportunity Matrix (4 Quadrants):**
  1. *Core Anchors:* High Volume, High Contribution Margin $\rightarrow$ Retain & Expand.
  2. *Growth Prospects:* Low Volume, High Contribution Margin $\rightarrow$ Scale & Incentive Pricing.
  3. *Margin Drag:* High Volume, Low Contribution Margin $\rightarrow$ Renegotiate Interchange Plus Pricing.
  4. *Risk / Monitor:* Low Volume, Low Contribution / High Disputes $\rightarrow$ Risk Review & Offboarding.

---

## 22. Revenue Leakage Methodology
- **Classification Taxonomy:**
  - *Soft Technical Declines:* Network timeouts, gateway communication errors $\rightarrow$ 80% addressable via smart retry routing.
  - *Soft Issuer Declines:* Insufficient funds $\rightarrow$ 25% addressable via dynamic time-of-day retries and account updater services.
  - *Hard Declines:* Stolen cards, closed accounts $\rightarrow$ 0% addressable (unrecoverable).
  - *Fraud Chargebacks:* Fraudulent transactions resulting in forced debit $\rightarrow$ Addressable via 3DS authentication and risk scoring.
- **Dollar-Denominated Impact:** Explicitly outputs potential revenue uplift from recovering addressable leakage buckets.

---

## 23. Risk & Anomaly Detection Methodology
- **Unsupervised Modeling:** Isolation Forest algorithm trained on normalized transaction vectors (Amount, Latency, Velocity in past 1 hour, Velocity in past 24 hours, Distance from home country, Historical merchant deviation).
- **Rule-Based Risk Engine:** Multi-factor heuristic score ($0 - 1000$ points) combining velocity surge flags, repeated decline patterns, device switches, and out-of-country transactions.
- **Evaluation & Benchmarking:** Model performance evaluated against latent synthetic anomaly ground truth using Precision-Recall Area Under Curve (PR-AUC), Brier score, and False Positive Ratio.

---

## 24. Time-Series Forecasting Methodology
- **Target Metrics:** Daily Transaction Volume, Daily GTV, and Daily Authorization Rate.
- **Models Evaluated:**
  1. Baseline Naive / Seasonal Moving Average.
  2. Holt-Winters Triple Exponential Smoothing (additive trend, weekly seasonality).
  3. Ridge Regression with auto-regressive lag features and calendar indicators.
- **Validation Protocol:** Strict temporal chronological split (first 80% train, subsequent 20% holdout test; zero lookahead leakage).
- **Error Metrics:** MAE, RMSE, and MAPE.

---

## 25. Statistical Methodology
- **Formal Hypothesis Test:**
  - *Research Question:* Does implementing 3D-Secure (3DS) authentication cause a statistically and commercially significant change in authorization rates compared to frictionless non-3DS transactions?
  - *Null Hypothesis ($H_0$):* $p_{\text{3DS}} = p_{\text{non3DS}}$ (no difference in population authorization proportions).
  - *Alternative Hypothesis ($H_1$):* $p_{\text{3DS}} \ne p_{\text{non3DS}}$.
  - *Statistical Test:* Two-proportion Z-test with $\alpha = 0.01$.
  - *Effect Size:* Cohen's $h$ calculated to distinguish statistical significance from practical business materiality.

---

## 26. Power BI Architecture & 6-Page Suite
- Structured into 6 dedicated business intelligence views:
  1. **Page 1: Executive Overview:** High-level executive cockpit showing GTV, Auth Rate, Net Revenue, Active Customers, 12-month trendlines, and negative variance alerts.
  2. **Page 2: Payment Performance:** Authorization funnel analysis, decline code breakdowns, routing efficiency, and hierarchical drilldowns (Country $\rightarrow$ Payment Method $\rightarrow$ Merchant).
  3. **Page 3: Customer Intelligence:** RFM segment migration, cohort retention triangle heatmap, customer concentration, and CLV decile distribution.
  4. **Page 4: Merchant Intelligence:** Merchant performance scorecard, fee burden analysis, and the 4-quadrant Merchant Opportunity Matrix.
  5. **Page 5: Risk & Anomaly Monitoring:** Risk score distribution, anomalous velocity alerts, chargeback rate monitoring vs. card scheme thresholds (Visa/Mastercard 100 bps threshold).
  6. **Page 6: Management Action Center:** "What Should Management Investigate?" exception report with prioritized operational and commercial action cards.

---

## 27. Grounded AI / Natural-Language Analytics Architecture
- **Safety Architecture:**
  - Natural-language user prompt is parsed by `ai/nl_engine.py`.
  - Intent is mapped strictly to an audited library of parameterized analytical SQL queries (`ai/query_whitelist.py`).
  - No unvalidated arbitrary SQL is executed against the database.
  - Queries execute in a read-only transaction with a 3-second statement timeout.
  - The synthesis engine ingests the returned structured dataset and outputs an executive answer citing exact figures.
  - Hallucination guard: Any figure in the output that does not exist in the database result payload triggers an assertion failure.

---

## 28. Automated Testing Strategy
- **Suite Structure:**
  - `test_generator.py`: Verifies distributions, reproducibility with random seeds, and volume scaling.
  - `test_validation.py`: Tests data quality rules, schema assertions, and boundary checks.
  - `test_financial_rules.py`: Verifies P&L integrity ($\text{GTV} \ge \text{Net Revenue} \ge \text{Contribution}$).
  - `test_kpi_calculations.py`: Validates mathematical consistency of every KPI formula.
  - `test_sql_execution.py`: Executes all SQL analytical views and verifies non-empty, error-free results.
  - `test_reconciliation.py`: Compares cross-platform aggregates to guarantee zero drift.

---

## 29. Data Reconciliation Strategy
- Automated reconciliation matrix verifying that across all layers:
  - $\text{Row Count (Raw)} = \text{Row Count (Staging)} = \text{Row Count (PostgreSQL)} = \text{Row Count (Power BI)}$
  - $\text{GTV (Python)} = \text{GTV (PostgreSQL)} = \text{GTV (Power BI)} = \text{GTV (Executive Report)}$
- Allowed variance: **0.00%**. Any discrepancy halts the delivery pipeline.

---

## 30. Documentation Strategy
- Comprehensive technical and business documentation generated in `documentation/`:
  - `DATA_DICTIONARY.md`: Every table, column, data type, description, and sample values.
  - `KPI_DICTIONARY.md`: Complete metric catalog with business definitions, formulas, and SQL/DAX code.
  - `METHODOLOGY.md`: Detailed mathematical descriptions of RFM, CLV, Isolation Forest, and Holt-Winters models.
  - `ASSUMPTIONS.md`: Documented business assumptions regarding interchange rates, decline recoverability, and cost allocations.
  - `LIMITATIONS.md`: Transparent boundary conditions, synthetic data characteristics, and external generalizability.

---

## 31. Executive Report Strategy
- Publication-quality 6-page PDF generated via Python `reportlab`:
  - Page 1: Strategic Executive Summary & Performance Scorecard.
  - Page 2: Revenue Waterfall & Payment Performance Funnel.
  - Page 3: Customer & Merchant Economics (RFM & Opportunity Matrix).
  - Page 4: Root-Cause Investigation: Payment Declines & Operational Latency.
  - Page 5: Risk Monitoring, Anomaly Scoring & Chargeback Exposure.
  - Page 6: Management Action Plan & Projected Financial Impact.
- Strictly adheres to the **Observation $\rightarrow$ Driver $\rightarrow$ Magnitude $\rightarrow$ Financial Impact $\rightarrow$ Action** narrative framework.

---

## 32. GitHub Presentation Strategy
- Production-grade public portfolio structure:
  - Clean, informative README with executive architecture diagrams, KPI highlights, sample screenshots, and exact reproduction instructions.
  - Git history with semantic, descriptive commits for each phase.
  - Zero large binary files tracked (clean repo size $< 25 \text{ MB}$).

---

## 33. Phase-by-Phase Implementation Plan
- **Phase 0-1:** Environment Discovery, Skill Audit & Architecture Blueprint *(Current Phase)*.
- **Phase 2:** Directory Scaffolding, Environment Configuration, Git Tracking.
- **Phase 3:** Synthetic Data Engine & Multi-Tier Dataset Generation.
- **Phase 4:** Data Quality Engine, Cleaning, and Feature Engineering.
- **Phase 5:** PostgreSQL Schema DDL, Indexing, and Bulk Loading Pipeline.
- **Phase 6:** Core Analytical Layer, KPIs, and Advanced SQL Views.
- **Phase 7:** Payment Performance Intelligence & Funnel Modeling.
- **Phase 8:** Revenue Leakage & Value at Risk Quantification.
- **Phase 9:** Customer Intelligence, RFM Segmentation, CLV, and Cohorts.
- **Phase 10:** Merchant Portfolio Intelligence & Opportunity Matrix.
- **Phase 11:** Risk Scoring & Unsupervised Anomaly Detection.
- **Phase 12:** Operational Incident Analytics & Root-Cause Explorer.
- **Phase 13:** Time-Series Forecasting Models & Backtest Validation.
- **Phase 14:** Inferential Statistical Hypothesis Testing.
- **Phase 15:** Power BI Project Architecture, TMDL, DAX Library.
- **Phase 16:** Grounded Natural-Language Analytics Engine ("Ask PAYMENTIQ").
- **Phase 17:** Automated Unit, Integration, and Reconciliation Test Suite.
- **Phase 18:** 6-Page Executive Analytics Review Document Generation.
- **Phase 19:** Comprehensive Technical Documentation & Dictionaries.
- **Phase 20:** Final End-to-End Audit and Quality Verification.

---

## 34. Definition of Done
The project is declared **DONE** if and only if:
1. All multi-tier datasets (DEV 100K, TEST 1M, and scalable FULL 5M+) can be generated deterministically via clean CLI commands.
2. 100% of data quality and validation checks pass with zero unhandled nulls, negative amounts, or referential integrity errors.
3. PostgreSQL database schema is fully initialized, populated via bulk load, and passes performance query benchmarks.
4. All advanced analytical SQL views and queries execute with verified mathematical consistency.
5. All 6 core analytical domains (Performance, Leakage, Customer, Merchant, Risk, Operations) produce documented business insights.
6. Statistical hypothesis testing confirms or rejects the research hypothesis with rigorous p-value and effect size calculation.
7. Power BI semantic model (`.pbip`/TMDL) and DAX measure catalog are fully authored and reconciled.
8. Grounded Natural-Language analytics engine safely answers business queries citing verified database figures without hallucination.
9. Cross-layer reconciliation confirms 0.00% variance in GTV, revenue, and transaction counts across Python, SQL, Power BI, and PDF report.
10. Automated test suite passes with 100% success rate across all unit, integration, and data tests.
11. 6-page Executive Analytics Review PDF is compiled with professional typography, charts, and actionable management recommendations.
12. Comprehensive documentation suite (`README.md`, `DATA_DICTIONARY.md`, `KPI_DICTIONARY.md`, `METHODOLOGY.md`, `ASSUMPTIONS.md`, `LIMITATIONS.md`) is complete.
