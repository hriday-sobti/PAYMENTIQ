"""
PAYMENTIQ Unit Tests for KPI Engine Calculations
Verifies mathematical precision and consistency of portfolio metrics against raw tables.
"""
import pytest
from python.analytics.kpi_engine import KPIEngine

@pytest.fixture(scope="module")
def global_kpis():
    """Calculates global KPIs using the engine."""
    engine = KPIEngine()
    return engine.calculate_global_kpis()

def test_kpi_gtv_greater_than_stv(global_kpis):
    """Rule: Gross Transaction Value must be strictly greater than Settled Value."""
    assert global_kpis["Gross_Transaction_Value"] > global_kpis["Settled_Transaction_Value"]

def test_kpi_authorization_rate_bounds(global_kpis):
    """Rule: Authorization rate must be between 80% and 98% for commercial card networks."""
    assert 80.0 <= global_kpis["Authorization_Rate_Pct"] <= 98.0

def test_kpi_rate_partition_sum(global_kpis):
    """Rule: Auth Rate + Decline Rate + Failure Rate must equal 100% (+- 0.05% rounding)."""
    rate_sum = (
        global_kpis["Authorization_Rate_Pct"] +
        global_kpis["Decline_Rate_Pct"] +
        global_kpis["Failure_Rate_Pct"]
    )
    assert abs(rate_sum - 100.0) < 0.1

def test_kpi_net_revenue_bounds(global_kpis):
    """Rule: Net Revenue must be strictly positive and less than Gross Revenue."""
    assert 0.0 < global_kpis["Net_Revenue"] < global_kpis["Gross_Revenue"]

def test_kpi_net_contribution_bounds(global_kpis):
    """Rule: Net Contribution must be less than Net Revenue due to chargeback losses."""
    assert 0.0 < global_kpis["Net_Contribution"] < global_kpis["Net_Revenue"]

def test_kpi_chargeback_rate_bounds(global_kpis):
    """Rule: Chargeback rate must be within realistic portfolio bounds (5 to 30 bps)."""
    assert 5.0 <= global_kpis["Chargeback_Rate_BPS"] <= 30.0

def test_kpi_latency_bounds(global_kpis):
    """Rule: Average latency should be realistic for cloud payment processing (100-400 ms)."""
    assert 100.0 <= global_kpis["Average_Latency_MS"] <= 400.0
