"""
PAYMENTIQ Automated Reconciliation Test
Asserts 0.00% variance across all 5 architectural storage layers.
"""
import pytest
from python.pipeline.reconciliation import DataReconciliationAuditor

def test_multi_layer_reconciliation_zero_drift():
    """Rule: All core financial metrics must reconcile with 0.00% variance across all layers."""
    auditor = DataReconciliationAuditor()
    results = auditor.audit_all_layers()
    assert results["status"] == "PASS", f"Cross-layer reconciliation failed! Report: {results['variance_matrix']}"

    # Verify key invariant figures
    l1 = results["layers"]["Layer_1_Raw_Parquet"]
    l3 = results["layers"]["Layer_3_PostgreSQL_DW"]
    l5 = results["layers"]["Layer_5_PowerBI_Model"]

    assert l1["row_count"] == l3["row_count"] == l5["row_count"] == 1000000
    assert abs(l1["gtv"] - l3["gtv"]) < 0.05
    assert abs(l1["gtv"] - l5["gtv"]) < 0.05
    assert abs(l1["net_revenue"] - l3["net_revenue"]) < 0.05
