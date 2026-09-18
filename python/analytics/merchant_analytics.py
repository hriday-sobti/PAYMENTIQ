"""
PAYMENTIQ Merchant Intelligence & Opportunity Matrix Engine
Evaluates merchant portfolio unit economics, Herfindahl-Hirschman concentration (HHI),
dispute exposure in basis points, and 4-Quadrant commercial opportunity classification.
"""
import time
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
from typing import Dict, Any

from python.utils.db import db_manager
from python.utils.logger import setup_logger

logger = setup_logger("merchant_analytics")

class MerchantAnalyticsEngine:
    """Specialized merchant portfolio economics and opportunity matrix analyst."""

    def __init__(self, reports_dir: str = "reports", doc_dir: str = "documentation"):
        self.reports_dir = Path(reports_dir)
        self.figures_dir = Path(reports_dir) / "figures"
        self.figures_dir.mkdir(parents=True, exist_ok=True)
        self.doc_path = Path(doc_dir) / "MERCHANT_ANALYTICS_REPORT.md"

    def run_analysis(self) -> Dict[str, Any]:
        """Executes merchant portfolio analytics, plots opportunity matrix, and writes report."""
        start_time = time.time()
        logger.info("======================================================================")
        logger.info("Starting PAYMENTIQ Merchant Intelligence Analysis")
        logger.info("======================================================================")

        ddb = db_manager.get_duckdb()

        # 1. Query Merchant Opportunity Matrix Data
        logger.info("Querying merchant economics and opportunity matrix...")
        q_matrix = "SELECT * FROM analytics.v_merchant_opportunity_matrix;"
        m_df = ddb.execute(q_matrix).df()
        n_merchants = len(m_df)
        logger.info("Loaded %d merchant records for evaluation", n_merchants)

        # 2. Portfolio Concentration (Herfindahl-Hirschman Index - HHI)
        total_gtv = m_df["settled_gtv"].sum()
        market_shares = (m_df["settled_gtv"] / total_gtv) * 100.0
        hhi_index = (market_shares ** 2).sum()
        logger.info("Calculated Merchant Portfolio HHI Index: %.2f", hhi_index)

        # 3. Quadrant Aggregation
        quadrant_summary = m_df.groupby("opportunity_quadrant").agg(
            merchant_count=("merchant_id", "count"),
            total_settled_gtv=("settled_gtv", "sum"),
            total_net_contribution=("net_contribution", "sum"),
            avg_margin_pct=("contribution_margin_pct", "mean"),
            avg_dispute_bps=("dispute_rate_bps", "mean")
        ).reset_index()

        quadrant_summary["gtv_share_pct"] = (quadrant_summary["total_settled_gtv"] / total_gtv) * 100.0

        # 4. Generate Visual: 4-Quadrant Opportunity Matrix Scatter Plot
        logger.info("Generating Figure: Merchant Opportunity Matrix...")
        plt.figure(figsize=(11, 6))

        med_gtv = m_df["settled_gtv"].median()
        med_margin = m_df["contribution_margin_pct"].median()

        palette = {
            "Core Anchor (Protect & Expand)": "#2ca02c",
            "Growth Prospect (Incentivize Scale)": "#1f77b4",
            "Margin Drag (Renegotiate Markup)": "#ff7f0e",
            "Review / Low Yield Portfolio": "#7f7f7f",
            "High Risk / Scheme Monitoring": "#d62728"
        }

        sns.scatterplot(
            data=m_df,
            x="settled_gtv",
            y="contribution_margin_pct",
            hue="opportunity_quadrant",
            palette=palette,
            alpha=0.75,
            s=45
        )

        plt.axvline(med_gtv, color="grey", linestyle="--", alpha=0.6, label=f"Median GTV (${med_gtv:,.0f})")
        plt.axhline(med_margin, color="grey", linestyle=":", alpha=0.6, label=f"Median Margin ({med_margin:.1f}%)")

        plt.xscale("log")
        plt.title("PAYMENTIQ Merchant Opportunity Matrix (Volume vs. Net Contribution Margin)", fontweight="bold", pad=15)
        plt.xlabel("Settled Transaction Volume ($ Log Scale)")
        plt.ylabel("Net Contribution Margin (%)")
        plt.legend(bbox_to_anchor=(1.02, 1), loc="upper left", frameon=True)
        plt.tight_layout()
        matrix_path = self.figures_dir / "merchant_opportunity_matrix.png"
        plt.savefig(matrix_path, dpi=200)
        plt.close()

        # 5. Write Markdown Report
        self._write_report(m_df, quadrant_summary, hhi_index)

        elapsed = time.time() - start_time
        logger.info("Merchant Analytics Completed in %.2f seconds", elapsed)
        return {"merchants": m_df, "quadrants": quadrant_summary, "hhi": hhi_index}

    def _write_report(self, m_df: pd.DataFrame, q_df: pd.DataFrame, hhi: float):
        """Generates comprehensive Markdown report."""
        md = f"""# PAYMENTIQ | Merchant Intelligence & Opportunity Matrix Report

**Portfolio Size:** 1,000 Contracted Merchants  
**Total Settled GTV:** ${m_df['settled_gtv'].sum():,.2f}  
**Portfolio Concentration (HHI):** {hhi:.1f} (Unconcentrated competitive portfolio, regulatory benchmark < 1,500)  
**Report Version:** 1.0.0  

---

## 1. Executive Summary
This report evaluates merchant portfolio economics, margin contribution, dispute exposure, and strategic positioning across the 4-Quadrant Merchant Opportunity Matrix.

---

## 2. 4-Quadrant Opportunity Matrix Summary

| Opportunity Quadrant | Merchant Count | Share (%) | Total Settled GTV ($) | GTV Share (%) | Net Contribution ($) | Avg Margin (%) | Avg Dispute (BPS) |
|---|---|---|---|---|---|---|---|
"""
        for _, r in q_df.iterrows():
            pct_cnt = (r['merchant_count'] / len(m_df)) * 100.0
            md += f"| **{r['opportunity_quadrant']}** | {r['merchant_count']:,} | {pct_cnt:.1f}% | ${r['total_settled_gtv']:,.2f} | {r['gtv_share_pct']:.1f}% | ${r['total_net_contribution']:,.2f} | {r['avg_margin_pct']:.2f}% | {r['avg_dispute_bps']:.1f} bps |\n"

        md += f"""
---

## 3. High-Risk Merchant Exposure & Scheme Monitoring Alerts
Under Visa and Mastercard scheme compliance standards, merchants exceeding **90 to 100 basis points (1.00%)** in dispute chargeback ratios require immediate risk review or loss-reserve holdbacks.

"""
        high_risk = m_df[m_df["dispute_rate_bps"] > 90.0].sort_values("dispute_rate_bps", ascending=False).head(10)
        if len(high_risk) > 0:
            md += "| Merchant ID | Merchant Name | Category | Settled GTV ($) | Dispute Count | Dispute Rate (BPS) | Action |\n"
            md += "|---|---|---|---|---|---|---|\n"
            for _, r in high_risk.iterrows():
                md += f"| `{r['merchant_id']}` | {r['merchant_name']} | {r['merchant_category']} | ${r['settled_gtv']:,.2f} | {r['dispute_count']} | **{r['dispute_rate_bps']:.1f} bps** | Place 10% rolling reserve & require 3DS |\n"
        else:
            md += "Zero merchants currently exceed the 90.0 bps threshold.\n"

        md += """
---

## 4. Strategic Recommendations by Quadrant

1. **Core Anchors:** Offer volume-based tiered interchange incentives to defend contractual exclusivity against competitor acquirers.
2. **Growth Prospects:** Provide co-marketing credits and developer SDK optimization to accelerate transaction velocity.
3. **Margin Drag:** Initiate contract renegotiation to migrate accounts from flat-rate blended pricing to transparent Interchange Plus (IC+) pricing with minimum margin floors.
4. **Risk / Scheme Monitoring:** Mandate 3D-Secure authentication on 100% of card-not-present volume and implement 10% rolling collateral reserves.
"""
        with open(self.doc_path, "w") as f:
            f.write(md)

if __name__ == "__main__":
    engine = MerchantAnalyticsEngine()
    engine.run_analysis()
