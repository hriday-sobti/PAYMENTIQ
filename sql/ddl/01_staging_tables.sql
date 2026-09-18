-- ====================================================================
-- PAYMENTIQ PostgreSQL Staging Layer DDL
-- Author: PAYMENTIQ Analytics Engineering
-- Description: Unconstrained staging tables for high-speed bulk ingestion
-- ====================================================================

CREATE SCHEMA IF NOT EXISTS staging;

DROP TABLE IF EXISTS staging.stg_transactions;
CREATE TABLE staging.stg_transactions (
    transaction_id VARCHAR(64),
    customer_key INTEGER,
    customer_id VARCHAR(32),
    merchant_key INTEGER,
    merchant_id VARCHAR(32),
    date_key INTEGER,
    timestamp TIMESTAMP,
    amount NUMERIC(12, 2),
    currency VARCHAR(8),
    payment_method_key SMALLINT,
    payment_method VARCHAR(64),
    merchant_category VARCHAR(64),
    merchant_country VARCHAR(8),
    customer_country VARCHAR(8),
    device_type VARCHAR(32),
    channel VARCHAR(64),
    is_3ds_authenticated BOOLEAN,
    auth_status VARCHAR(16),
    decline_code VARCHAR(8),
    decline_reason VARCHAR(128),
    processing_fee NUMERIC(10, 2),
    interchange_fee NUMERIC(10, 2),
    scheme_fee NUMERIC(10, 2),
    net_revenue NUMERIC(10, 2),
    net_contribution NUMERIC(10, 2),
    latency_ms INTEGER,
    retry_attempt SMALLINT,
    refund_flag BOOLEAN,
    chargeback_flag BOOLEAN,
    fraud_flag BOOLEAN,
    risk_score SMALLINT,
    is_high_value BOOLEAN,
    is_cross_border BOOLEAN,
    is_soft_decline BOOLEAN,
    addressable_leakage_amount NUMERIC(12, 2)
);

DROP TABLE IF EXISTS staging.stg_disputes;
CREATE TABLE staging.stg_disputes (
    dispute_id VARCHAR(64),
    transaction_id VARCHAR(64),
    merchant_key INTEGER,
    customer_key INTEGER,
    dispute_date_key INTEGER,
    dispute_timestamp TIMESTAMP,
    dispute_amount NUMERIC(12, 2),
    chargeback_fee NUMERIC(8, 2),
    dispute_reason VARCHAR(128),
    dispute_status VARCHAR(64)
);

DROP TABLE IF EXISTS staging.stg_support_cases;
CREATE TABLE staging.stg_support_cases (
    case_id VARCHAR(64),
    customer_key INTEGER,
    customer_id VARCHAR(32),
    transaction_id VARCHAR(64),
    created_date_key INTEGER,
    created_timestamp TIMESTAMP,
    category VARCHAR(64),
    severity VARCHAR(32),
    resolution_time_minutes INTEGER,
    sla_breached_flag BOOLEAN,
    csat_score SMALLINT,
    status VARCHAR(32)
);
