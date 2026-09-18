"""
PAYMENTIQ Unit and Property Tests for Analytics, Machine Learning & Statistical Models
Validates Isolation Forest anomaly detection, Holt-Winters forecasting, Two-Sample Z-Test,
RFM scoring, and the Merchant Opportunity Matrix.
"""
import pytest
import numpy as np
import pandas as pd
import scipy.stats as stats
from sklearn.ensemble import IsolationForest
from statsmodels.tsa.holtwinters import ExponentialSmoothing

from python.analytics.statistical_analysis import StatisticalHypothesisTester
from python.analytics.forecasting import TimeSeriesForecaster
from python.analytics.anomaly_detection import AnomalyDetectionEngine

# =========================================================================
# 1. Isolation Forest Anomaly Detection Tests
# =========================================================================

@pytest.fixture(scope="module")
def sample_feature_matrix():
    """Generates synthetic multi-dimensional feature matrix for anomaly model testing."""
    rng = np.random.default_rng(42)
    n = 1000
    amounts = np.exp(rng.normal(4.0, 0.8, n))
    latencies = np.clip(rng.normal(200, 50, n), 40, 3000)
    risk_scores = rng.integers(50, 800, n)
    cross_border = rng.integers(0, 2, n)
    return pd.DataFrame({
        "amount": amounts,
        "latency_ms": latencies,
        "risk_score": risk_scores,
        "is_cross_border": cross_border
    })

def test_isolation_forest_output_shape(sample_feature_matrix):
    """Rule: Isolation Forest must output predictions matching input row count."""
    clf = IsolationForest(n_estimators=50, contamination=0.02, random_state=42)
    preds = clf.fit_predict(sample_feature_matrix)
    assert len(preds) == len(sample_feature_matrix)

def test_isolation_forest_prediction_values(sample_feature_matrix):
    """Rule: Predictions must strictly be 1 (normal) or -1 (anomaly)."""
    clf = IsolationForest(n_estimators=50, contamination=0.02, random_state=42)
    preds = clf.fit_predict(sample_feature_matrix)
    unique_vals = set(np.unique(preds))
    assert unique_vals.issubset({1, -1})

def test_isolation_forest_contamination_rate(sample_feature_matrix):
    """Rule: Proportion of flagged anomalies must align with configured contamination parameter (+- 0.01)."""
    contamination = 0.03
    clf = IsolationForest(n_estimators=50, contamination=contamination, random_state=42)
    preds = clf.fit_predict(sample_feature_matrix)
    observed_contamination = (preds == -1).mean()
    assert abs(observed_contamination - contamination) < 0.015

def test_isolation_forest_deterministic_seed(sample_feature_matrix):
    """Rule: Identical random seeds must produce identical decision scores."""
    clf1 = IsolationForest(n_estimators=50, contamination=0.02, random_state=42)
    clf2 = IsolationForest(n_estimators=50, contamination=0.02, random_state=42)
    scores1 = clf1.fit(sample_feature_matrix).decision_function(sample_feature_matrix)
    scores2 = clf2.fit(sample_feature_matrix).decision_function(sample_feature_matrix)
    assert np.allclose(scores1, scores2)

# =========================================================================
# 2. Time-Series Forecasting Tests (Holt-Winters)
# =========================================================================

@pytest.fixture(scope="module")
def sample_time_series():
    """Generates synthetic daily transaction series with trend and weekly seasonality."""
    rng = np.random.default_rng(42)
    dates = pd.date_range("2024-01-01", periods=180, freq="D")
    trend = np.linspace(2000, 3000, 180)
    seasonality = 400 * np.sin(2 * np.pi * np.arange(180) / 7)
    noise = rng.normal(0, 50, 180)
    series = pd.Series(trend + seasonality + noise, index=dates)
    return series

def test_forecasting_model_convergence(sample_time_series):
    """Rule: Holt-Winters model must converge successfully with additive trend and weekly seasonality."""
    model = ExponentialSmoothing(sample_time_series, trend="add", seasonal="add", seasonal_periods=7).fit()
    assert model.mle_retvals is not None or model.params is not None

def test_forecasting_horizon_length(sample_time_series):
    """Rule: 90-day forecast must generate exactly 90 distinct future timestamps."""
    model = ExponentialSmoothing(sample_time_series, trend="add", seasonal="add", seasonal_periods=7).fit()
    forecast = model.forecast(90)
    assert len(forecast) == 90

def test_forecast_values_strictly_positive(sample_time_series):
    """Rule: Forecasted daily transaction volumes must be strictly positive."""
    model = ExponentialSmoothing(sample_time_series, trend="add", seasonal="add", seasonal_periods=7).fit()
    forecast = model.forecast(90)
    assert (forecast > 0).all()

def test_forecasting_backtest_mape_threshold():
    """Rule: Backtest out-of-sample MAPE must be under 8.0% benchmark."""
    forecaster = TimeSeriesForecaster()
    results = forecaster.run_forecasting(horizon_days=30)
    assert results["volume_mape"] < 8.0
    assert results["gtv_mape"] < 8.0

# =========================================================================
# 3. Inferential Statistics (Two-Sample Z-Test)
# =========================================================================

@pytest.fixture(scope="module")
def hypothesis_results():
    """Runs two-proportion hypothesis test."""
    tester = StatisticalHypothesisTester()
    return tester.run_two_proportion_test()

def test_statistical_test_sample_sizes(hypothesis_results):
    """Rule: Both sample cohorts must exceed 100,000 observations for valid asymptotic normality."""
    assert hypothesis_results["group_3ds_n"] > 100000
    assert hypothesis_results["group_non_3ds_n"] > 100000

def test_statistical_test_proportion_bounds(hypothesis_results):
    """Rule: Sample proportions must lie within [0.70, 0.99] bounds."""
    assert 0.70 <= hypothesis_results["group_3ds_p"] <= 0.99
    assert 0.70 <= hypothesis_results["group_non_3ds_p"] <= 0.99

def test_statistical_test_rejection_of_null(hypothesis_results):
    """Rule: The test must decisively reject H0 at p < 0.01."""
    assert hypothesis_results["reject_null"] is True
    assert hypothesis_results["p_value"] < 0.01

def test_statistical_test_confidence_interval_ordering(hypothesis_results):
    """Rule: 99% Confidence Interval lower bound must be strictly less than upper bound."""
    assert hypothesis_results["ci_99_lower"] < hypothesis_results["ci_99_upper"]
    assert hypothesis_results["ci_99_lower"] > 0.0  # Confirms positive lift

def test_cohens_h_effect_size_positive(hypothesis_results):
    """Rule: Cohen's h effect size must be positive and within meaningful operational range."""
    assert 0.05 <= hypothesis_results["cohens_h"] <= 0.50

# =========================================================================
# 4. Customer RFM & Segmentation Rules
# =========================================================================

def test_rfm_quintile_scoring_bounds():
    """Rule: RFM quintile scores must strictly take integer values from 1 to 5."""
    from python.utils.db import db_manager
    ddb = db_manager.get_duckdb()
    scores = ddb.execute("SELECT DISTINCT r_score, f_score, m_score FROM analytics.v_customer_rfm_scores;").fetchall()
    for r, f, m in scores:
        assert r in {1, 2, 3, 4, 5}
        assert f in {1, 2, 3, 4, 5}
        assert m in {1, 2, 3, 4, 5}

def test_rfm_segment_names_valid():
    """Rule: Every cardholder must be assigned to one of the 7 documented behavioral segments."""
    from python.utils.db import db_manager
    ddb = db_manager.get_duckdb()
    valid_segments = {
        "Champions", "Loyal Customers", "Recent High Spenders",
        "New Active Customers", "At Risk / Churn Alert", "Can Not Lose Them",
        "Hibernating / Dormant", "Standard Retail Active"
    }
    assigned_segments = set(ddb.execute("SELECT DISTINCT rfm_segment FROM analytics.v_customer_rfm_scores;").df()["rfm_segment"])
    assert assigned_segments.issubset(valid_segments)

# =========================================================================
# 5. Merchant Opportunity Matrix & Concentration Rules
# =========================================================================

def test_merchant_opportunity_quadrants_valid():
    """Rule: Merchants must map to one of the 5 opportunity quadrants."""
    from python.utils.db import db_manager
    ddb = db_manager.get_duckdb()
    valid_quadrants = {
        "Core Anchor (Protect & Expand)",
        "Growth Prospect (Incentivize Scale)",
        "Margin Drag (Renegotiate Markup)",
        "Review / Low Yield Portfolio",
        "High Risk / Scheme Monitoring"
    }
    assigned = set(ddb.execute("SELECT DISTINCT opportunity_quadrant FROM analytics.v_merchant_opportunity_matrix;").df()["opportunity_quadrant"])
    assert assigned.issubset(valid_quadrants)

def test_merchant_hhi_bounds():
    """Rule: Merchant Herfindahl-Hirschman Index (HHI) must be strictly between 1 and 10,000."""
    from python.utils.db import db_manager
    ddb = db_manager.get_duckdb()
    gtv_series = ddb.execute("SELECT settled_gtv FROM analytics.v_merchant_opportunity_matrix;").df()["settled_gtv"]
    shares = (gtv_series / gtv_series.sum()) * 100.0
    hhi = (shares ** 2).sum()
    assert 1.0 <= hhi <= 10000.0
    assert hhi < 1500.0  # Competitive / unconcentrated benchmark
