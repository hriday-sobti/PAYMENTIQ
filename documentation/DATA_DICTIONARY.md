# PAYMENTIQ | Enterprise Data Dictionary & Schema Specification

**Document Version:** 1.0.0  
**Data Warehouse:** `paymentiq_dw` (PostgreSQL 16 & DuckDB)  
**Schema Architecture:** Pure Dimensional Star Schema (`core`, `staging`, `analytics`)  

---

## 1. Table Catalog & Grain Overview

| Schema | Table Name | Type | Primary Key | Grain | Description |
|---|---|---|---|---|---|
| `core` | `dim_customers` | Dimension | `customer_key` | One cardholder / account | Customer profile, geography, segment, and acquisition channel |
| `core` | `dim_merchants` | Dimension | `merchant_key` | One commercial merchant | Merchant business profile, MCC category, pricing tier, and markups |
| `core` | `dim_payment_methods` | Dimension | `payment_method_key` | One payment rail & card brand | Payment method configuration, interchange, and scheme fees |
| `core` | `dim_dates` | Dimension | `date_key` | One calendar day | Complete financial calendar covering 2022 through 2026 |
| `core` | `dim_decline_codes` | Dimension | `decline_code` | One ISO 8583 response code | Standardized payment decline reasons, soft/hard status, and actions |
| `core` | `fact_transactions` | Fact | `transaction_id` | One transaction attempt | Core event stream capturing all checkout attempts and economic metrics |
| `core` | `fact_disputes` | Fact | `dispute_id` | One formal dispute event | Chargeback claims, reversal statuses, and network dispute fees |
| `core` | `fact_support_cases` | Fact | `case_id` | One customer service ticket | Operational inquiry incidents linked to transaction decline events |

---

## 2. Detailed Column Specifications

### 2.1 `core.dim_customers`
- **`customer_key`** (`INTEGER`, PK): Surrogate primary key.
- **`customer_id`** (`VARCHAR(32)`, Unique): Natural customer business identifier (`CUST-000001`).
- **`signup_date`** (`DATE`): Date the customer opened their account.
- **`customer_country`** (`VARCHAR(8)`): ISO 2-letter country code (`US`, `GB`, `DE`, `FR`, `CA`, `AU`).
- **`customer_segment`** (`VARCHAR(64)`): Behavioral customer grouping (`Retail Consumer`, `Affluent / VIP`, `Small Business`, `Corporate / Commercial`).
- **`acquisition_channel`** (`VARCHAR(64)`): Acquisition marketing source (`Organic Search`, `Paid Digital`, `Partner Referral`, `Direct App`, `Affiliate`).
- **`risk_tier`** (`VARCHAR(32)`): Credit and underwriting risk categorization (`Low Risk`, `Standard`, `Elevated Risk`).

### 2.2 `core.dim_merchants`
- **`merchant_key`** (`INTEGER`, PK): Surrogate primary key.
- **`merchant_id`** (`VARCHAR(32)`, Unique): Natural commercial entity identifier (`MERCH-0001`).
- **`merchant_name`** (`VARCHAR(128)`): Legal registered name of commercial seller.
- **`mcc_code`** (`VARCHAR(8)`): Standard ISO 18245 4-digit Merchant Category Code.
- **`merchant_category`** (`VARCHAR(64)`): Plain text industry category (`Grocery & Supermarkets`, `Airlines & Transit`, etc.).
- **`merchant_country`** (`VARCHAR(8)`): Merchant domicile ISO 2-letter country code.
- **`onboarding_date`** (`DATE`): Date merchant processing agreement commenced.
- **`pricing_tier`** (`VARCHAR(32)`): Commercial fee structure (`Enterprise IC+`, `Mid-Market Blended`, `SMB Flat Rate`).
- **`acquirer_markup_bps`** (`SMALLINT`): Processor margin markup in basis points (1 bp = 0.01%).

### 2.3 `core.dim_payment_methods`
- **`payment_method_key`** (`SMALLINT`, PK): Surrogate primary key.
- **`payment_method_id`** (`VARCHAR(16)`, Unique): Rail code identifier (`PM-01` to `PM-09`).
- **`method_name`** (`VARCHAR(64)`): Payment rail family (`Credit Card`, `Debit Card`, `Digital Wallet`, `BNPL`, `Instant Bank Transfer`).
- **`card_brand`** (`VARCHAR(32)`): Card scheme brand (`Visa`, `Mastercard`, `American Express`, `Apple Pay`, `Google Pay`, `Klarna / Afterpay Rail`, `FedNow / SEPA Instant`).
- **`card_type`** (`VARCHAR(32)`): Consumer vs commercial credential classification.
- **`auth_rate_baseline`** (`NUMERIC(5,3)`): Historical baseline approval rate across card schemes.
- **`interchange_rate_bps`** (`SMALLINT`): Card network pass-through interchange fee in basis points.
- **`scheme_fee_bps`** (`SMALLINT`): Card brand scheme assessment fee in basis points.
- **`acquirer_fee_bps`** (`SMALLINT`): Acquirer gateway technical fee in basis points.

### 2.4 `core.dim_dates`
- **`date_key`** (`INTEGER`, PK): Integer formatted calendar key (`YYYYMMDD`).
- **`full_date`** (`DATE`, Unique): Standard date timestamp.
- **`year`** (`SMALLINT`): Calendar year (2022–2026).
- **`quarter`** (`SMALLINT`): Quarter of year (1–4).
- **`month`** (`SMALLINT`): Calendar month (1–12).
- **`month_name`** (`VARCHAR(16)`): Month name (`January` through `December`).
- **`week_of_year`** (`SMALLINT`): ISO calendar week number (1–53).
- **`day_of_month`** (`SMALLINT`): Day of the month (1–31).
- **`day_of_week`** (`SMALLINT`): ISO day index (0 = Monday, 6 = Sunday).
- **`day_name`** (`VARCHAR(16)`): Day name (`Monday` through `Sunday`).
- **`is_weekend`** (`BOOLEAN`): True if Saturday or Sunday.
- **`is_month_end`** (`BOOLEAN`): True if final day of the calendar month.
- **`is_quarter_end`** (`BOOLEAN`): True if final day of the calendar quarter.

### 2.5 `core.dim_decline_codes`
- **`decline_code`** (`VARCHAR(8)`, PK): Standard ISO 8583 response code (`00`, `51`, `91`, `19`, `05`, `54`, `14`, `41`).
- **`decline_reason`** (`VARCHAR(128)`): Text description of failure cause.
- **`decline_type`** (`VARCHAR(32)`): Classification (`None`, `Soft Decline`, `Soft Technical`, `Hard Decline`, `Hard Fraud`).
- **`is_retryable`** (`BOOLEAN`): True if transaction is addressable via automated retry logic.
- **`recommended_action`** (`TEXT`): Standard operating procedure for remediation.

### 2.6 `core.fact_transactions`
- **`transaction_id`** (`VARCHAR(64)`, PK): Universal unique identifier (UUID v4).
- **`customer_key`** (`INTEGER`, FK): Reference to `dim_customers.customer_key`.
- **`merchant_key`** (`INTEGER`, FK): Reference to `dim_merchants.merchant_key`.
- **`date_key`** (`INTEGER`, FK): Reference to `dim_dates.date_key`.
- **`payment_method_key`** (`SMALLINT`, FK): Reference to `dim_payment_methods.payment_method_key`.
- **`decline_code`** (`VARCHAR(8)`, FK, Nullable): Reference to `dim_decline_codes.decline_code` (NULL if Approved).
- **`timestamp`** (`TIMESTAMP`): Exact millisecond transaction creation timestamp.
- **`amount`** (`NUMERIC(12,2)`): Gross transaction amount in local currency ($ > 0.00).
- **`currency`** (`VARCHAR(8)`): Transaction currency (`USD`, `EUR`, `GBP`, `CAD`, `AUD`).
- **`device_type`** (`VARCHAR(32)`): Originating checkout hardware (`Mobile App`, `Web Browser`, `POS Terminal`, `Contactless Tap`, `API / Auto-bill`).
- **`channel`** (`VARCHAR(64)`): Commercial transaction rail (`E-Commerce / CNP`, `In-Store / POS`, `Recurring / Subscription`).
- **`is_3ds_authenticated`** (`BOOLEAN`): True if cardholder completed 3D-Secure biometric/OTP verification.
- **`auth_status`** (`VARCHAR(16)`): Gateway response outcome (`Approved`, `Declined`, `Failed`).
- **`decline_reason`** (`VARCHAR(128)`, Nullable): Plain text description of decline reason.
- **`processing_fee`** (`NUMERIC(10,2)`): Gross Merchant Discount Rate (MDR) billed to merchant.
- **`interchange_fee`** (`NUMERIC(10,2)`): Pass-through interchange cost paid to issuing bank.
- **`scheme_fee`** (`NUMERIC(10,2)`): Pass-through card network scheme assessment fee paid to Visa/Mastercard.
- **`net_revenue`** (`NUMERIC(10,2)`): Gross fee revenue minus direct pass-through interchange and scheme costs.
- **`net_contribution`** (`NUMERIC(10,2)`): Net revenue minus chargeback write-offs and assessment fees.
- **`latency_ms`** (`INTEGER`): Authorization round-trip network response latency in milliseconds.
- **`retry_attempt`** (`SMALLINT`): Attempt sequence number (1 = original, 2+ = automated retry).
- **`refund_flag`** (`BOOLEAN`): True if customer initiated post-settlement return.
- **`chargeback_flag`** (`BOOLEAN`): True if cardholder initiated formal bank dispute.
- **`fraud_flag`** (`BOOLEAN`): Latent ground-truth synthetic fraud label (for model validation only).
- **`risk_score`** (`SMALLINT`): Multi-factor heuristic risk score (0 to 1000).
- **`is_high_value`** (`BOOLEAN`): True if amount $\ge \$500.00$.
- **`is_cross_border`** (`BOOLEAN`): True if customer country $\ne$ merchant country.
- **`is_soft_decline`** (`BOOLEAN`): True if decline code belongs to retryable soft decline taxonomy.
- **`addressable_leakage_amount`** (`NUMERIC(12,2)`): Amount if soft decline, else 0.00.

### 2.7 `core.fact_disputes`
- **`dispute_id`** (`VARCHAR(64)`, PK): Dispute record identifier (`DSP-xxxxxxxx`).
- **`transaction_id`** (`VARCHAR(64)`, FK): Reference to `fact_transactions.transaction_id`.
- **`merchant_key`** (`INTEGER`, FK): Reference to `dim_merchants.merchant_key`.
- **`customer_key`** (`INTEGER`, FK): Reference to `dim_customers.customer_key`.
- **`dispute_date_key`** (`INTEGER`, FK): Reference to `dim_dates.date_key`.
- **`dispute_timestamp`** (`TIMESTAMP`): Timestamp formal chargeback claim was filed.
- **`dispute_amount`** (`NUMERIC(12,2)`): Disputed transactional value.
- **`chargeback_fee`** (`NUMERIC(8,2)`): Acquirer administrative dispute assessment fee ($15.00–$25.00).
- **`dispute_reason`** (`VARCHAR(128)`): Reason code description (Fraud, Service Not Provided, etc.).
- **`dispute_status`** (`VARCHAR(64)`): Outcome state (`Lost (Debited)`, `Won (Reversed)`, `Under Arbitration`).

### 2.8 `core.fact_support_cases`
- **`case_id`** (`VARCHAR(64)`, PK): Support ticket identifier (`CASE-xxxxxxxx`).
- **`customer_key`** (`INTEGER`, FK): Reference to `dim_customers.customer_key`.
- **`customer_id`** (`VARCHAR(32)`): Denormalized customer natural identifier.
- **`transaction_id`** (`VARCHAR(64)`, FK): Reference to associated `fact_transactions.transaction_id`.
- **`created_date_key`** (`INTEGER`, FK): Reference to `dim_dates.date_key`.
- **`created_timestamp`** (`TIMESTAMP`): Creation timestamp of support ticket.
- **`category`** (`VARCHAR(64)`): Issue classification (`Decline Inquiry`, `Duplicate Charge`, etc.).
- **`severity`** (`VARCHAR(32)`): Priority level (`Low`, `Medium`, `High`, `Critical`).
- **`resolution_time_minutes`** (`INTEGER`): Total minutes elapsed until ticket resolution.
- **`sla_breached_flag`** (`BOOLEAN`): True if resolution time exceeded 240 minutes (4 hours).
- **`csat_score`** (`SMALLINT`): Cardholder satisfaction rating (1 = Unsatisfied, 5 = Highly Satisfied).
- **`status`** (`VARCHAR(32)`): Ticket lifecycle state (`Resolved`, `Escalated`).
