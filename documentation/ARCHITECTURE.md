# PAYMENTIQ | Technical Architecture Specification

**Architecture Version:** 1.0.0  
**Storage Tier:** PostgreSQL 16.6 (Primary Star Schema) + DuckDB 1.5.5 (In-Memory Columnar Acceleration)  
**Execution Runtime:** Python 3.14.6  
**Presentation Tier:** Power BI Desktop (`.pbip` / TMDL) + ReportLab PDF  

---

## 1. End-to-End System Architecture Diagram

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

## 2. Storage & Database Design

### 2.1 Dual-Engine Architecture
PAYMENTIQ operates a synchronized dual-database architecture:
1. **PostgreSQL 16.6 (Relational System of Record):** Provides ACID compliance, primary/foreign key constraint enforcement, relational staging/core schemas, B-tree indexes, and standard analytical views.
2. **DuckDB 1.5.5 (Columnar Analytical Engine):** Embedded in-process OLAP engine operating directly on zero-copy Parquet buffers for sub-second analytical aggregations, ML feature vector extraction, and interactive CLI queries.

### 2.2 Schema Separation Contract
- **`staging`:** Landing zone for raw unconstrained data loads.
- **`core`:** Pure dimensional star schema with foreign key referential integrity (`fact_transactions`, `dim_customers`, `dim_merchants`, `dim_dates`, `dim_payment_methods`, `dim_decline_codes`, `fact_disputes`, `fact_support_cases`).
- **`analytics`:** Production analytical views and reporting aggregations (`v_payment_performance_by_method`, `v_revenue_leakage_waterfall`, `v_customer_rfm_scores`, `v_merchant_opportunity_matrix`, `v_operational_support_metrics`).

---

## 3. Data Processing & Pipeline Stages

1. **Generation:** High-speed streaming generator (`python/generator/generator.py`) writes partitioned compressed Parquet files (`data/raw/`).
2. **Quality Audit:** Validation engine (`python/pipeline/validation.py`) enforces 13 data quality rules across completeness, uniqueness, and financial invariants.
3. **Transformation:** Cleaning engine (`python/pipeline/cleaning.py`) downcasts memory types, enriches net revenue and contribution margins, and flags addressable leakage.
4. **Warehouse Load:** In-memory stream loader (`python/pipeline/loader.py`) executes high-speed PostgreSQL binary `COPY` (12,000+ rows/sec) and populates DuckDB tables.
5. **Analytics Execution:** Analytical modules run in sequence to compute KPIs, RFM segments, opportunity matrices, Isolation Forest anomaly scores, Holt-Winters forecasts, and Z-tests.
6. **BI Export & Sync:** Pre-computed datasets are exported to `powerbi/export_data/` for instant Power BI Desktop import.
7. **Reconciliation:** Multi-layer reconciliation auditor (`python/pipeline/reconciliation.py`) verifies 0.00% variance across all 5 layers.
8. **Reporting & AI:** ReportLab compiles the 6-page Executive Review PDF and the grounded natural-language assistant (`ai/assistant_cli.py`) serves stakeholder queries.
