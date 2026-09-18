"""
PAYMENTIQ Publication-Grade Executive Analytics Review Generator
Compiles the official 6-page C-suite PDF report using ReportLab with embedded charts,
executive KPIs, and structured commercial decision frameworks.
"""
import os
import json
import pandas as pd
from pathlib import Path

from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image, PageBreak, KeepTogether, HRFlowable
)
from reportlab.pdfgen import canvas

from python.utils.logger import setup_logger

logger = setup_logger("executive_report")

class NumberedCanvas(canvas.Canvas):
    """Canvas that computes total pages dynamically for running footers."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._saved_page_states = []

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        num_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self.draw_header_footer(num_pages)
            super().showPage()
        super().save()

    def draw_header_footer(self, page_count):
        self.saveState()
        self.setFont("Helvetica-Bold", 8)
        self.setFillColor(colors.HexColor("#2b5c8f"))
        # Header (pages 2+)
        if self._pageNumber > 1:
            self.drawString(54, 750, "PAYMENTIQ | EXECUTIVE ANALYTICS REVIEW (2024)")
            self.setStrokeColor(colors.HexColor("#d0d7de"))
            self.setLineWidth(0.5)
            self.line(54, 744, 558, 744)

        # Footer (all pages)
        self.setFont("Helvetica", 8)
        self.setFillColor(colors.HexColor("#57606a"))
        page_str = f"Page {self._pageNumber} of {page_count}"
        self.drawRightString(558, 36, page_str)
        self.drawString(54, 36, "CONFIDENTIAL & PROPRIETARY — FOR INTERNAL MANAGEMENT USE ONLY")
        self.setStrokeColor(colors.HexColor("#d0d7de"))
        self.setLineWidth(0.5)
        self.line(54, 48, 558, 48)
        self.restoreState()

def build_pdf_report(
    output_pdf: str = "reports/PAYMENTIQ_Executive_Review.pdf",
    kpi_path: str = "reports/kpi_summary.json",
    figures_dir: str = "reports/figures"
):
    """Compiles the formal 6-page Executive Analytics Review document."""
    logger.info("======================================================================")
    logger.info("Generating PAYMENTIQ Publication-Grade Executive Analytics Review PDF")
    logger.info("======================================================================")

    # Load KPI summary
    with open(kpi_path, "r") as f:
        kpi = json.load(f)

    fig_dir = Path(figures_dir)
    doc = SimpleDocTemplate(
        output_pdf,
        pagesize=letter,
        leftMargin=54,
        rightMargin=54,
        topMargin=54,
        bottomMargin=54
    )

    styles = getSampleStyleSheet()
    
    # Custom styles
    title_style = ParagraphStyle(
        "DocTitle",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=20,
        leading=24,
        textColor=colors.HexColor("#0f2a4a")
    )
    subtitle_style = ParagraphStyle(
        "DocSubtitle",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=10,
        leading=14,
        textColor=colors.HexColor("#57606a")
    )
    h1_style = ParagraphStyle(
        "Heading1_Custom",
        parent=styles["Heading1"],
        fontName="Helvetica-Bold",
        fontSize=13,
        leading=16,
        textColor=colors.HexColor("#0f2a4a"),
        spaceAfter=6
    )
    body_style = ParagraphStyle(
        "Body_Custom",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=8.5,
        leading=11.5,
        textColor=colors.HexColor("#24292f")
    )
    callout_style = ParagraphStyle(
        "Callout_Text",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=8,
        leading=11,
        textColor=colors.HexColor("#1f2328")
    )

    story = []

    # =========================================================================
    # PAGE 1: Executive Summary & Strategic Scorecard
    # =========================================================================
    story.append(Paragraph("PAYMENTIQ | EXECUTIVE ANALYTICS REVIEW", title_style))
    story.append(Paragraph("End-to-End Payment Transaction Intelligence, Margin Optimization & Risk Surveillance", subtitle_style))
    story.append(Spacer(1, 10))
    story.append(HRFlowable(width="100%", thickness=1.5, color=colors.HexColor("#0f2a4a"), spaceAfter=12))

    story.append(Paragraph("1. Strategic Executive Summary", h1_style))
    story.append(Paragraph(
        "During the 2024 operating year, the PAYMENTIQ platform processed <b>1,000,000 transaction attempts</b>, "
        "generating <b>$134.53M in Gross Transaction Value (GTV)</b> and <b>$121.12M in Settled Volume</b>. "
        "Overall conversion efficiency remained resilient at an <b>authorization rate of 91.18%</b>, yielding <b>$803.47K in Net Retained Revenue</b> "
        "and <b>$647.06K in Net Contribution</b> after direct chargeback provisions. However, multi-dimensional analysis isolates "
        "<b>$13.41M in Transaction Value at Risk (TVaR)</b>, of which <b>$9.19M</b> stems from recoverable soft declines. "
        "Deploying targeted smart retry routing and expanding 3D-Secure authentication offers an addressable <b>+$103.3K net revenue recapture</b>.",
        body_style
    ))
    story.append(Spacer(1, 10))

    # KPI Scorecard Table
    scorecard_data = [
        ["METRIC", "2024 VALUE", "BENCHMARK", "VARIANCE / STATUS"],
        ["Gross Transaction Value (GTV)", f"${kpi['Gross_Transaction_Value']:,.2f}", "$130.00M", "+3.48% (Above Plan)"],
        ["Settled Volume (STV)", f"${kpi['Settled_Transaction_Value']:,.2f}", "$118.00M", "+2.64% (Strong Conversion)"],
        ["Authorization Rate", f"{kpi['Authorization_Rate_Pct']:.2f}%", "90.00%", "+118 bps (Outperforming)"],
        ["Gross Revenue (MDR)", f"${kpi['Gross_Revenue']:,.2f}", "$2.50M", "195 bps take rate"],
        ["Net Retained Revenue", f"${kpi['Net_Revenue']:,.2f}", "$775.0K", "66.3 bps net take rate"],
        ["Net Contribution Margin", f"{kpi['Contribution_Margin_Pct']:.2f}%", "78.00%", "+253 bps (Healthy Yield)"],
        ["Transaction Value at Risk (TVaR)", f"${kpi['Transaction_Value_at_Risk']:,.2f}", "< $15.00M", "$9.19M Soft Recoverable"],
        ["Dispute Chargeback Ratio", f"{kpi['Chargeback_Rate_BPS']:.2f} bps", "< 50.00 bps", "Compliant (< 100 bps threshold)"]
    ]
    t_scorecard = Table(scorecard_data, colWidths=[180, 110, 95, 120])
    t_scorecard.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#0f2a4a")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 8),
        ("ALIGN", (1, 0), (-1, -1), "CENTER"),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
        ("TOPPADDING", (0, 0), (-1, -1), 4),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#d0d7de")),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#f6f8fa")])
    ]))
    story.append(t_scorecard)
    story.append(Spacer(1, 12))

    # Embed Figure 3: Monthly Volume & Revenue Trend
    fig_monthly = fig_dir / "eda_monthly_volume_trend.png"
    if fig_monthly.exists():
        story.append(Image(str(fig_monthly), width=6.5*inch, height=2.6*inch))

    story.append(PageBreak())

    # =========================================================================
    # PAGE 2: Performance & Revenue Waterfall
    # =========================================================================
    story.append(Spacer(1, 10))
    story.append(Paragraph("2. Payment Performance & Revenue Waterfall", h1_style))
    story.append(Paragraph(
        "<b>OBSERVATION:</b> Top-line transaction attrition reveals that 8.82% of checkout attempts fail to convert to settled funds.<br/>"
        "<b>DRIVER:</b> Cardholder authorization rejections constitute 98.5% of total attrition, while technical gateway drops represent only 1.5%.<br/>"
        "<b>MAGNITUDE:</b> Exactly $13,411,712.89 in gross transaction value was declined or failed during 2024.<br/>"
        "<b>FINANCIAL EFFECT:</b> Uncaptured merchant discount revenue totals $261,500 across all non-authorized transactions.<br/>"
        "<b>INTERPRETATION:</b> 68.5% of total declined volume ($9.19M) stems from retryable soft decline codes (Insufficient Funds, System Timeout).<br/>"
        "<b>LIMITATION:</b> Customer cardholder balances are inherently volatile; retry capture curves decay rapidly after 72 hours.<br/>"
        "<b>ACTION:</b> Implement automated smart retries with machine-learned schedule optimization to capture ~$103.3K net revenue.",
        body_style
    ))
    story.append(Spacer(1, 8))

    fig_waterfall = fig_dir / "revenue_leakage_waterfall.png"
    if fig_waterfall.exists():
        story.append(Image(str(fig_waterfall), width=6.5*inch, height=2.5*inch))

    story.append(Spacer(1, 8))
    fig_funnel = fig_dir / "payment_performance_funnel.png"
    if fig_funnel.exists():
        story.append(Image(str(fig_funnel), width=6.5*inch, height=2.2*inch))

    story.append(PageBreak())

    # =========================================================================
    # PAGE 3: Customer & Merchant Economics
    # =========================================================================
    story.append(Spacer(1, 10))
    story.append(Paragraph("3. Customer & Merchant Portfolio Economics", h1_style))
    story.append(Paragraph(
        "<b>CUSTOMER PORTFOLIO:</b> Analysis of 40,000 active cardholders reveals extreme value concentration. "
        "The top two RFM segments (<i>Champions</i> and <i>Loyal Customers</i>) represent 28.1% of cardholders but generate <b>58.4% of settled volume</b> "
        "and <b>61.2% of net contribution</b> ($396K). Conversely, 16.4% of customers reside in the <i>At Risk / Churn Alert</i> category.<br/>"
        "<b>MERCHANT PORTFOLIO:</b> The 1,000 contracted merchants exhibit an unconcentrated, competitive distribution with an HHI of <b>44.3</b>. "
        "Under the 4-Quadrant Opportunity Matrix, 482 merchants qualify as <b>Core Anchors</b> (high volume, above-median margin), "
        "while 118 merchants operate as <b>Margin Drag</b> (high volume, but below-median contribution margin).",
        body_style
    ))
    story.append(Spacer(1, 8))

    fig_rfm = fig_dir / "customer_rfm_segments.png"
    if fig_rfm.exists():
        story.append(Image(str(fig_rfm), width=6.5*inch, height=2.4*inch))

    story.append(Spacer(1, 8))
    fig_matrix = fig_dir / "merchant_opportunity_matrix.png"
    if fig_matrix.exists():
        story.append(Image(str(fig_matrix), width=6.5*inch, height=2.4*inch))

    story.append(PageBreak())

    # =========================================================================
    # PAGE 4: Payment Failures & Root Causes
    # =========================================================================
    story.append(Spacer(1, 10))
    story.append(Paragraph("4. Payment Failures, Operational Latency & Root Causes", h1_style))
    story.append(Paragraph(
        "<b>INCIDENT 1 (European Gateway Outage):</b> Between August 12 and August 16, technical packet loss on the primary European link "
        "caused processing latency to escalate from 175 ms to 2,800+ ms in Germany and France. Authorization rates collapsed by <b>3,300 bps</b> "
        "(from 91.5% to 58.2%), generating <b>$1.42M in TVaR</b> and ~$35.5K in direct net revenue leakage.<br/>"
        "<b>INCIDENT 2 (Digital Goods Card-Testing Bot Attack):</b> On May 8–10, automated botnet scripts targeted Merchant `MERCH-0042` "
        "with rapid micro-transactions ($1.50–$3.50). Transaction velocity surged 4.5x while authorization plunged to 18.5%, "
        "incurring $18.2K in non-refundable processor network fees.<br/>"
        "<b>CUSTOMER SERVICE SLA:</b> Operational dispute and decline inquiries represent <b>55% of all support cases</b>, "
        "with an average resolution time of 132 minutes and an SLA breach rate of 14.8%.",
        body_style
    ))
    story.append(Spacer(1, 8))

    fig_rca = fig_dir / "root_cause_incident_analysis.png"
    if fig_rca.exists():
        story.append(Image(str(fig_rca), width=6.5*inch, height=2.6*inch))

    story.append(Spacer(1, 8))
    fig_cohort = fig_dir / "customer_cohort_retention.png"
    if fig_cohort.exists():
        story.append(Image(str(fig_cohort), width=6.5*inch, height=2.4*inch))

    story.append(PageBreak())

    # =========================================================================
    # PAGE 5: Risk & Anomaly Monitoring
    # =========================================================================
    story.append(Spacer(1, 10))
    story.append(Paragraph("5. Risk Surveillance, Anomaly Detection & Statistical Evidence", h1_style))
    story.append(Paragraph(
        "<b>UNSUPERVISED ANOMALY MODELING:</b> An Isolation Forest model trained on multidimensional behavioral vectors "
        "(amount, latency, risk score, cross-border, and velocity) flagged <b>1.80% of transactions</b> as anomalous. "
        "The model achieved an Area Under the Precision-Recall Curve (PR-AUC) of <b>0.502</b>, successfully isolating card-testing attacks "
        "and high-value cross-border fraud spikes without ground-truth label leakage.<br/>"
        "<b>INFERENTIAL STATISTICAL PROOF:</b> A Two-Sample Pooled Proportion Z-Test comparing 3D-Secure verified transactions (n=408,402) "
        "against frictionless non-3DS transactions (n=191,355) yielded <b>Z = 45.67 (p < 1e-15)</b>, decisively rejecting the null hypothesis. "
        "3DS achieves a verified <b>+342 bps authorization uplift</b> (93.19% vs. 89.77%), unlocking <b>$882K in recovered GTV</b> and "
        "<b>$22.1K in net revenue</b> while transferring fraud liability to issuing banks.",
        body_style
    ))
    story.append(Spacer(1, 8))

    fig_anomaly = fig_dir / "anomaly_detection_eval.png"
    if fig_anomaly.exists():
        story.append(Image(str(fig_anomaly), width=6.5*inch, height=2.4*inch))

    story.append(Spacer(1, 8))
    fig_stats = fig_dir / "statistical_hypothesis_test.png"
    if fig_stats.exists():
        story.append(Image(str(fig_stats), width=6.5*inch, height=2.4*inch))

    story.append(PageBreak())

    # =========================================================================
    # PAGE 6: Recommended Actions & Management Action Center
    # =========================================================================
    story.append(Spacer(1, 10))
    story.append(Paragraph("6. Prioritized Management Action Plan & Commercial Impact", h1_style))
    story.append(Paragraph(
        "The following prioritized remediation roadmap translates analytical findings into concrete, high-ROI commercial and operational initiatives.",
        body_style
    ))
    story.append(Spacer(1, 8))

    action_table_data = [
        ["PRIORITY", "STRATEGIC ACTION", "OWNER", "ESTIMATED IMPACT", "TIMEFRAME"],
        ["P1 (Urgent)", "Smart Retry Logic Deployment\nAutomate 24-hr retry for Code 51 & secondary routing for Code 91.", "Payments Eng", "+$103.3K Net Revenue\n(+$4.1M Settled GTV)", "Q1 2025\n(Weeks 1–4)"],
        ["P1 (Urgent)", "Automated Botnet Mitigation\nImplement rate-limiting & CAPTCHA on MCC 5999 digital checkouts.", "Risk & SecOps", "Eliminate $18K processor fees\nProtect merchant account", "Immediate\n(Week 1)"],
        ["P2 (High)", "Mandatory 3DS for CNP Rails\nEnforce 3DS on Card-Not-Present transactions > $100 or high risk.", "Product / Fraud", "+342 bps Auth Lift\nEliminate chargeback liability", "Q1 2025\n(Weeks 3–6)"],
        ["P2 (High)", "Multi-Acquirer Dynamic Failover\nAuto-switch gateway when regional latency exceeds 600 ms.", "Infrastructure", "Prevent ~$35K outage leakage\nPreserve 91%+ SLA", "Q2 2025\n(Weeks 7–10)"],
        ["P3 (Medium)", "Margin Drag Contract Migration\nRenegotiate 118 Margin Drag merchants from flat rate to IC+.", "Commercial Sales", "+$45.0K Net Contribution\nRestore 82%+ target margin", "Q2 2025\n(Weeks 8–12)"],
        ["P3 (Medium)", "Automated Decline Messaging\nSend real-time SMS/App prompt explaining soft decline & retry.", "Customer Ops", "Deflect 40% support tickets\n+$28K support cost savings", "Q2 2025\n(Weeks 10–14)"]
    ]
    t_action = Table(action_table_data, colWidths=[65, 175, 75, 125, 64])
    t_action.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#0f2a4a")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 7.5),
        ("ALIGN", (0, 0), (-1, -1), "LEFT"),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
        ("TOPPADDING", (0, 0), (-1, -1), 5),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#d0d7de")),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#f6f8fa")])
    ]))
    story.append(t_action)
    story.append(Spacer(1, 10))

    # Forecast Trajectory Chart
    fig_fwd = fig_dir / "forecasting_trajectory.png"
    if fig_fwd.exists():
        story.append(Image(str(fig_fwd), width=6.5*inch, height=2.4*inch))

    doc.build(story, canvasmaker=NumberedCanvas)
    logger.info("Executive Analytics Review PDF Successfully Generated: %s", output_pdf)

if __name__ == "__main__":
    build_pdf_report()
