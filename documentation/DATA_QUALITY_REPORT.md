# PAYMENTIQ | Data Quality & Integrity Validation Report

**Execution Timestamp:** 2026-09-19T14:13:35.273272  
**Overall Validation Status:** **PASS**  
**Checks Passed:** 13 / 13 (100.0%)  

---

## 1. Executive Summary
The automated data quality engine evaluated all dimensional, transactional, and dispute records against 13 enterprise data quality rules across completeness, uniqueness, domain validity, financial consistency, and referential integrity.

---

## 2. Rule Execution Results Table

| Check ID | Rule Name | Category | Severity | Status | Details |
|---|---|---|---|---|---|
| `DQ_01` | Mandatory Columns Nullness Check | Completeness | ERROR | **PASSED** | Zero nulls across mandatory columns: {'transaction_id': np.int64(0), 'customer_key': np.int64(0), 'merchant_key': np.int64(0), 'date_key': np.int64(0), 'timestamp': np.int64(0), 'amount': np.int64(0), 'currency': np.int64(0), 'payment_method_key': np.int64(0), 'auth_status': np.int64(0), 'processing_fee': np.int64(0), 'interchange_fee': np.int64(0), 'scheme_fee': np.int64(0)} |
| `DQ_02` | Transaction ID Primary Key Uniqueness | Uniqueness | ERROR | **PASSED** | Distinct transaction IDs: 1000000 / 1000000 (0 duplicates) |
| `DQ_03` | Transaction Amount Positivity ($ > 0.00) | Financial Consistency | ERROR | **PASSED** | Non-positive amounts detected: 0 |
| `DQ_04` | Non-negative Fee Checks | Financial Consistency | ERROR | **PASSED** | Negative fees detected: 0 |
| `DQ_05` | Processing Fee Less Than Transaction Amount | Financial Consistency | ERROR | **PASSED** | Processing fees exceeding transaction amount: 0 |
| `DQ_06` | Approved Transactions Decline Code Nullness | Domain Validity | ERROR | **PASSED** | Approved transactions with non-null decline codes: 0 |
| `DQ_07` | Declined Transactions Must Possess Valid Decline Codes | Domain Validity | ERROR | **PASSED** | Declined transactions missing decline codes: 0 |
| `DQ_08` | Customer Foreign Key Referential Integrity | Referential Integrity | ERROR | **PASSED** | Transactions with invalid customer_key: 0 |
| `DQ_09` | Merchant Foreign Key Referential Integrity | Referential Integrity | ERROR | **PASSED** | Transactions with invalid merchant_key: 0 |
| `DQ_10` | Payment Method Foreign Key Referential Integrity | Referential Integrity | ERROR | **PASSED** | Transactions with invalid payment_method_key: 0 |
| `DQ_11` | Calendar Date Foreign Key Referential Integrity | Referential Integrity | ERROR | **PASSED** | Transactions with invalid date_key: 0 |
| `DQ_12` | Dispute Transaction ID Referential Integrity | Referential Integrity | ERROR | **PASSED** | Disputes referencing non-existent transaction IDs: 0 |
| `DQ_13` | Support Cases Transaction ID Referential Integrity | Referential Integrity | ERROR | **PASSED** | Support cases referencing non-existent transaction IDs: 0 |

---

## 3. Dataset Statistical Profiling Summary

- **Total Transactions Validated:** 1,000,000
- **Total Gross Transaction Value (GTV):** $134,531,743.69
- **Mean Transaction Amount:** $134.53
- **Median Transaction Amount:** $61.83
- **75th Percentile Amount:** $129.27
- **95th Percentile Amount:** $507.09
- **99th Percentile Amount:** $1144.39
- **Maximum Transaction Amount:** $15,000.00
- **Amount Distribution Skewness:** 7.26 (positive right skew as expected for commercial transactions)
- **Mean Processing Latency:** 201.0 ms
- **95th Percentile Latency:** 326.0 ms
- **Authorization Rate:** 91.18%
- **Refund Rate:** 1.66%
- **Chargeback Rate:** 0.1110%
- **Latent Fraud Rate:** 0.4492%

---

## 4. Status Breakdown
- **Approved:** 911,844 (91.18%)
- **Declined:** 86,850 (8.69%)
- **Failed:** 1,306 (0.13%)
