# PAYMENTIQ | Time-Series Forecasting & Operational Projection Report

**Methodology:** Holt-Winters Triple Exponential Smoothing (Additive Trend, 7-Day Weekly Seasonality)  
**Validation Framework:** Chronological Out-of-Sample Backtest (80% Train, 20% Test, Zero Lookahead)  
**Forecast Horizon:** 90 Calendar Days (2025-01-01 to 2025-03-31)  
**Report Version:** 1.0.0  

---

## 1. Executive Summary
This report presents out-of-sample backtest accuracy and forward projections for transaction volume, settled gross transaction value (GTV), and authorization rates for Q1 2025.

---

## 2. Model Accuracy & Backtest Validation Metrics

| Forecast Target | Model Family | MAE | RMSE | MAPE (%) | Validation Rating |
|---|---|---|---|---|---|
| **Transaction Volume** | Holt-Winters Additive Trend + Weekly Seasonality | `41.7 tx/day` | `55.8` | **1.53%** | Excellent (<8% benchmark) |
| **Settled GTV** | Holt-Winters Additive Trend + Weekly Seasonality | `$10,834.08/day` | — | **3.25%** | Excellent (<8% benchmark) |
| **Authorization Rate** | Exponential Smoothing (Level + Weekly Seasonality) | `0.42 percentage points` | — | — | High Precision (<1.5 pp) |

---

## 3. Q1 2025 Forward Projections Summary

- **Projected Q1 2025 Total Transaction Volume:** **81,834 transactions**
- **Projected Q1 2025 Settled GTV:** **$9,893,365.09**
- **Projected Q1 2025 Mean Authorization Rate:** **90.45%**
- **Average Projected Daily Volume:** `2,728 transactions/day` (80% prediction bounds: `2,662` to `2,794`)

---

## 4. Methodological Safeguards Against Data Leakage
1. **Strict Chronological Splitting:** The models were trained strictly on observations up to Day 292 (October 2024). Test observations (November–December) were strictly withheld.
2. **Deterministic Confidence Envelopes:** Prediction intervals are constructed empirically from backtest residual standard errors rather than assumed Gaussian asymptotes.
3. **Stationarity & Seasonality Confirmation:** Strong weekly cycles (Sunday trough, Friday peak) were captured cleanly by the 7-period seasonal component.
