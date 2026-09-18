-- ====================================================================
-- PAYMENTIQ PostgreSQL Dimensional Core Star Schema DDL
-- Author: PAYMENTIQ Analytics Engineering
-- Description: Production star schema with PK/FK constraints and grains
-- ====================================================================

CREATE SCHEMA IF NOT EXISTS core;

-- --------------------------------------------------------------------
-- Dimension 1: Customers
-- Grain: One cardholder / account
-- --------------------------------------------------------------------
DROP TABLE IF EXISTS core.dim_customers CASCADE;
CREATE TABLE core.dim_customers (
    customer_key INTEGER PRIMARY KEY,
    customer_id VARCHAR(32) NOT NULL UNIQUE,
    signup_date DATE NOT NULL,
    customer_country VARCHAR(8) NOT NULL,
    customer_segment VARCHAR(64) NOT NULL,
    acquisition_channel VARCHAR(64) NOT NULL,
    risk_tier VARCHAR(32) NOT NULL
);

-- --------------------------------------------------------------------
-- Dimension 2: Merchants
-- Grain: One commercial seller
-- --------------------------------------------------------------------
DROP TABLE IF EXISTS core.dim_merchants CASCADE;
CREATE TABLE core.dim_merchants (
    merchant_key INTEGER PRIMARY KEY,
    merchant_id VARCHAR(32) NOT NULL UNIQUE,
    merchant_name VARCHAR(128) NOT NULL,
    mcc_code VARCHAR(8) NOT NULL,
    merchant_category VARCHAR(64) NOT NULL,
    merchant_country VARCHAR(8) NOT NULL,
    onboarding_date DATE NOT NULL,
    pricing_tier VARCHAR(32) NOT NULL,
    acquirer_markup_bps SMALLINT NOT NULL
);

-- --------------------------------------------------------------------
-- Dimension 3: Payment Methods
-- Grain: One payment rail / card brand configuration
-- --------------------------------------------------------------------
DROP TABLE IF EXISTS core.dim_payment_methods CASCADE;
CREATE TABLE core.dim_payment_methods (
    payment_method_key SMALLINT PRIMARY KEY,
    payment_method_id VARCHAR(16) NOT NULL UNIQUE,
    method_name VARCHAR(64) NOT NULL,
    card_brand VARCHAR(32) NOT NULL,
    card_type VARCHAR(32) NOT NULL,
    auth_rate_baseline NUMERIC(5, 3) NOT NULL,
    interchange_rate_bps SMALLINT NOT NULL,
    scheme_fee_bps SMALLINT NOT NULL,
    acquirer_fee_bps SMALLINT NOT NULL
);

-- --------------------------------------------------------------------
-- Dimension 4: Calendar Dates
-- Grain: One calendar day
-- --------------------------------------------------------------------
DROP TABLE IF EXISTS core.dim_dates CASCADE;
CREATE TABLE core.dim_dates (
    date_key INTEGER PRIMARY KEY,
    full_date DATE NOT NULL UNIQUE,
    year SMALLINT NOT NULL,
    quarter SMALLINT NOT NULL,
    month SMALLINT NOT NULL,
    month_name VARCHAR(16) NOT NULL,
    week_of_year SMALLINT NOT NULL,
    day_of_month SMALLINT NOT NULL,
    day_of_week SMALLINT NOT NULL,
    day_name VARCHAR(16) NOT NULL,
    is_weekend BOOLEAN NOT NULL,
    is_month_end BOOLEAN NOT NULL,
    is_quarter_end BOOLEAN NOT NULL
);

-- --------------------------------------------------------------------
-- Dimension 5: Decline Codes
-- Grain: One ISO 8583 decline code
-- --------------------------------------------------------------------
DROP TABLE IF EXISTS core.dim_decline_codes CASCADE;
CREATE TABLE core.dim_decline_codes (
    decline_code VARCHAR(8) PRIMARY KEY,
    decline_reason VARCHAR(128) NOT NULL,
    decline_type VARCHAR(32) NOT NULL,
    is_retryable BOOLEAN NOT NULL,
    recommended_action TEXT NOT NULL
);

-- --------------------------------------------------------------------
-- Fact 1: Transactions
-- Grain: One transaction attempt
-- --------------------------------------------------------------------
DROP TABLE IF EXISTS core.fact_transactions CASCADE;
CREATE TABLE core.fact_transactions (
    transaction_id VARCHAR(64) PRIMARY KEY,
    customer_key INTEGER NOT NULL REFERENCES core.dim_customers(customer_key),
    merchant_key INTEGER NOT NULL REFERENCES core.dim_merchants(merchant_key),
    date_key INTEGER NOT NULL REFERENCES core.dim_dates(date_key),
    payment_method_key SMALLINT NOT NULL REFERENCES core.dim_payment_methods(payment_method_key),
    decline_code VARCHAR(8) REFERENCES core.dim_decline_codes(decline_code),
    timestamp TIMESTAMP NOT NULL,
    amount NUMERIC(12, 2) NOT NULL CHECK (amount > 0),
    currency VARCHAR(8) NOT NULL,
    device_type VARCHAR(32) NOT NULL,
    channel VARCHAR(64) NOT NULL,
    is_3ds_authenticated BOOLEAN NOT NULL,
    auth_status VARCHAR(16) NOT NULL,
    decline_reason VARCHAR(128),
    processing_fee NUMERIC(10, 2) NOT NULL CHECK (processing_fee >= 0),
    interchange_fee NUMERIC(10, 2) NOT NULL CHECK (interchange_fee >= 0),
    scheme_fee NUMERIC(10, 2) NOT NULL CHECK (scheme_fee >= 0),
    net_revenue NUMERIC(10, 2) NOT NULL,
    net_contribution NUMERIC(10, 2) NOT NULL,
    latency_ms INTEGER NOT NULL,
    retry_attempt SMALLINT NOT NULL,
    refund_flag BOOLEAN NOT NULL,
    chargeback_flag BOOLEAN NOT NULL,
    fraud_flag BOOLEAN NOT NULL,
    risk_score SMALLINT NOT NULL,
    is_high_value BOOLEAN NOT NULL,
    is_cross_border BOOLEAN NOT NULL,
    is_soft_decline BOOLEAN NOT NULL,
    addressable_leakage_amount NUMERIC(12, 2) NOT NULL
);

-- --------------------------------------------------------------------
-- Fact 2: Disputes & Chargebacks
-- Grain: One formal dispute event
-- --------------------------------------------------------------------
DROP TABLE IF EXISTS core.fact_disputes CASCADE;
CREATE TABLE core.fact_disputes (
    dispute_id VARCHAR(64) PRIMARY KEY,
    transaction_id VARCHAR(64) NOT NULL REFERENCES core.fact_transactions(transaction_id),
    merchant_key INTEGER NOT NULL REFERENCES core.dim_merchants(merchant_key),
    customer_key INTEGER NOT NULL REFERENCES core.dim_customers(customer_key),
    dispute_date_key INTEGER NOT NULL REFERENCES core.dim_dates(date_key),
    dispute_timestamp TIMESTAMP NOT NULL,
    dispute_amount NUMERIC(12, 2) NOT NULL CHECK (dispute_amount > 0),
    chargeback_fee NUMERIC(8, 2) NOT NULL,
    dispute_reason VARCHAR(128) NOT NULL,
    dispute_status VARCHAR(64) NOT NULL
);

-- --------------------------------------------------------------------
-- Fact 3: Support Cases
-- Grain: One customer operational incident
-- --------------------------------------------------------------------
DROP TABLE IF EXISTS core.fact_support_cases CASCADE;
CREATE TABLE core.fact_support_cases (
    case_id VARCHAR(64) PRIMARY KEY,
    customer_key INTEGER NOT NULL REFERENCES core.dim_customers(customer_key),
    customer_id VARCHAR(32),
    transaction_id VARCHAR(64) NOT NULL REFERENCES core.fact_transactions(transaction_id),
    created_date_key INTEGER NOT NULL REFERENCES core.dim_dates(date_key),
    created_timestamp TIMESTAMP NOT NULL,
    category VARCHAR(64) NOT NULL,
    severity VARCHAR(32) NOT NULL,
    resolution_time_minutes INTEGER NOT NULL,
    sla_breached_flag BOOLEAN NOT NULL,
    csat_score SMALLINT NOT NULL,
    status VARCHAR(32) NOT NULL
);
