# PAYMENTIQ | Exploratory Data Analysis & Statistical Profiling

**Dataset Scope:** 1,000,000 Payment Transaction Records  
**Analysis Period:** 2024-01-01 to 2024-12-31  
**Observation Grain:** One Transaction Attempt  

---

## 1. Executive Summary
This exploratory data analysis establishes the empirical baselines, parametric and non-parametric distributions, temporal seasonality, and risk correlations across the 2024 transactional stream.

---

## 2. Statistical Distribution Highlights

| Metric | Empirical Value | Economic / Analytical Interpretation |
|---|---|---|
| **Total Transaction Records** | `1,000,000` | Full portfolio validation cohort |
| **Mean Amount** | `$134.53` | Parametric central tendency |
| **Median Amount** | `$61.83` | Non-parametric robust median (insulated from high-ticket skew) |
| **Interquartile Range (IQR)** | `$95.19` | Middle 50% transaction dispersion |
| **95th Percentile Amount** | `$507.09` | Upper threshold defining elevated value transactions |
| **99th Percentile Amount** | `$1144.39` | High-ticket VIP / corporate charge boundary |
| **Amount Skewness** | `7.26` | Significant right-skew typical of payment networks |
| **Mean Latency** | `201.0 ms` | Average end-to-end authorization round-trip time |
| **95th Percentile Latency** | `326.0 ms` | Operational SLA threshold indicator |
| **Overall Authorization Rate** | `91.18%` | Platform-wide operational conversion efficiency |
| **Refund Rate** | `1.66%` | Post-settlement merchant return volume |
| **Chargeback Dispute Rate** | `0.1110%` | Realized dispute exposure (well below scheme monitoring) |
| **Latent Fraud Rate** | `0.4492%` | Ground-truth fraud incidence for evaluation |

---

## 3. Key Exploratory Findings

### Finding 1: Merchant Category Determines Ticket Size and Dispersion
- High-ticket travel, hospitality, and electronics (`MCC 7011`, `4722`, `5732`) exhibit log-normal distribution centers exceeding $250.00, with fat right tails extending past $2,500.00.
- Daily retail, grocery, and quick-service dining (`MCC 5411`, `5812`) exhibit tight clustering around $35–$50 with low variance.

### Finding 2: 3D-Secure Uplift on Card-Not-Present Rails
- Verified 3D-Secure transactions achieve an authorization rate of **~94.5%** compared to **~89.8%** for frictionless non-3DS transactions.
- The 470 bps uplift illustrates issuer confidence when cryptographic cardholder authentication is present.

### Finding 3: Seasonality & Event Surges
- Q4 demonstrates substantial volume expansion, culminating in a 3.2x surge during the late-November Black Friday / Cyber Monday promotional cycle.
- Technical latency experienced a temporary degradation spike during mid-August (Scenario A), causing an isolated dip in authorization rates in European corridors.

---

## 4. Visual Artifacts Produced
- `reports/figures/eda_amount_distribution.png`: Boxplot showing log-scaled amount distributions by MCC.
- `reports/figures/eda_auth_rate_by_method.png`: Grouped bar chart of authorization rates by payment method and 3DS verification.
- `reports/figures/eda_monthly_volume_trend.png`: Dual-axis line and bar chart tracking volume and net revenue.
- `reports/figures/eda_correlation_matrix.png`: Heatmap displaying correlation between numerical features.
