# PAYMENTIQ | Platform Limitations & Boundary Conditions

**Document Version:** 1.0.0  
**Transparency Level:** Full Technical Disclosure  

---

## 1. Synthetic Data Disclosure & Boundaries

> **MANDATORY DISCLOSURE:** PAYMENTIQ utilizes synthetic payment transaction data designed to simulate realistic enterprise payment operations, fee dynamics, authorization funnels, and fraud attacks. It does not contain proprietary data from any specific bank, acquirer, or card network, nor does it represent the private financial records of any commercial merchant.

---

## 2. Analytical & Technical Limitations

### 2.1 Checkout Funnel Truncation (Cart Abandonment)
- **Boundary:** The dataset commences at the **authorization request** grain (`transaction_id`).
- **Limitation:** It does not observe pre-authorization cardholder actions (e.g. cardholder entering the checkout page and abandoning the cart prior to clicking "Pay", or dropping off during an SMS OTP challenge before submitting).
- **Implication:** The measured 3DS authorization lift (+342 bps) represents authorization success *conditional on form submission*. True end-to-end checkout conversion may be slightly lower if biometric/SMS friction causes pre-submission drop-off.

### 2.2 Independent Trials Assumption in Statistical Testing
- **Boundary:** The Two-Sample Proportion Z-Test assumes each transaction represents an independent Bernoulli trial.
- **Limitation:** In payment processing, a small fraction of attempts originate from the same cardholder in retry loops.
- **Implication:** While the massive sample size ($n > 400,000$) provides decisive statistical power ($Z = 45.67, p < 10^{-15}$), standard errors may be marginally understated due to serial correlation among repeated attempts.

### 2.3 Macroeconomic Shocks in Time-Series Forecasting
- **Boundary:** Holt-Winters exponential smoothing extrapolates historical level, additive trend, and 7-day weekly seasonality into Q1 2025.
- **Limitation:** The model cannot anticipate exogenous macroeconomic shocks (e.g. central bank interest rate shocks, major geopolitical disruptions, or unannounced scheme interchange regulation changes).

### 2.4 Unsupervised Anomaly Detection Precision
- **Boundary:** Isolation Forest is trained without labels to detect structural outliers in behavioral feature space.
- **Limitation:** High anomaly scores flag statistically rare behavior (e.g. sudden high-value purchases or late-night cross-border dining) that may occasionally represent legitimate affluent traveler activity rather than fraudulent bot attacks.
- **Operational Rule:** Anomaly scores must be utilized for **prioritized review and step-up 3DS challenges**, never as automated hard blocks that destroy legitimate customer conversion.
