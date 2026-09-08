"""
PDF Report Generator
---------------------
Cleaned data + AI insights + charts ko ek professional PDF report mein
convert karta hai using ReportLab + Matplotlib.
"""

import os
import pandas as pd
import matplotlib
matplotlib.use("Agg")  # GUI backend nahi chahiye, server-safe
import matplotlib.pyplot as plt
from datetime import datetime

from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.lib import colors
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Image, Table, TableStyle, PageBreak
)


def _make_chart(df: pd.DataFrame, chart_cfg: dict, output_dir: str) -> str:
    """Ek chart config ke hisaab se matplotlib image bana kar path return karta hai."""
    chart_type = chart_cfg.get("type", "bar")
    x_col = chart_cfg.get("x")
    y_col = chart_cfg.get("y")
    title = chart_cfg.get("title", f"{y_col} by {x_col}")

    if x_col not in df.columns or y_col not in df.columns:
        return None

    plt.figure(figsize=(7, 4))

    if chart_type == "bar":
        grouped = df.groupby(x_col)[y_col].sum().sort_values(ascending=False)
        grouped.plot(kind="bar", color="#2F5496")
    elif chart_type == "line":
        grouped = df.groupby(x_col)[y_col].sum().sort_index()
        grouped.plot(kind="line", marker="o", color="#2F5496")
    else:
        grouped = df.groupby(x_col)[y_col].sum()
        grouped.plot(kind="bar", color="#2F5496")

    plt.title(title)
    plt.ylabel(y_col)
    plt.xlabel(x_col)
    plt.xticks(rotation=30, ha="right")
    plt.tight_layout()

    chart_path = os.path.join(output_dir, f"_chart_{x_col}_{y_col}.png")
    plt.savefig(chart_path, dpi=150)
    plt.close()
    return chart_path


def generate_pdf_report(df: pd.DataFrame, insights: dict, report_config: dict) -> str:
    output_dir = report_config.get("output_dir", "outputs")
    os.makedirs(output_dir, exist_ok=True)
    filename = f"{output_dir}/report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"

    doc = SimpleDocTemplate(filename, pagesize=A4,
                             topMargin=2*cm, bottomMargin=2*cm,
                             leftMargin=2*cm, rightMargin=2*cm)

    styles = getSampleStyleSheet()
    title_style = ParagraphStyle("TitleStyle", parent=styles["Title"], textColor=colors.HexColor("#2F5496"))
    heading_style = ParagraphStyle("HeadingStyle", parent=styles["Heading2"], textColor=colors.HexColor("#2F5496"))
    body_style = styles["BodyText"]

    story = []

    # ---------- Title ----------
    story.append(Paragraph(report_config.get("title", "Automated Report"), title_style))
    story.append(Paragraph(f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M')}", styles["Normal"]))
    story.append(Spacer(1, 0.6*cm))

    # ---------- Summary ----------
    story.append(Paragraph("Overall Summary", heading_style))
    story.append(Paragraph(insights.get("summary", ""), body_style))
    story.append(Spacer(1, 0.4*cm))

    # ---------- Insights ----------
    if insights.get("insights"):
        story.append(Paragraph("Key Insights", heading_style))
        for point in insights["insights"]:
            story.append(Paragraph(f"• {point}", body_style))
        story.append(Spacer(1, 0.4*cm))

    # ---------- Recommendations ----------
    if insights.get("recommendations"):
        story.append(Paragraph("Recommendations", heading_style))
        for rec in insights["recommendations"]:
            story.append(Paragraph(f"• {rec}", body_style))
        story.append(Spacer(1, 0.4*cm))

    # ---------- Charts ----------
    chart_configs = report_config.get("charts", [])
    if chart_configs:
        story.append(PageBreak())
        story.append(Paragraph("Charts", heading_style))
        for chart_cfg in chart_configs:
            chart_path = _make_chart(df, chart_cfg, output_dir)
            if chart_path and os.path.exists(chart_path):
                story.append(Image(chart_path, width=15*cm, height=8*cm))
                story.append(Spacer(1, 0.5*cm))

    # ---------- Data Table (sirf pehli 20 rows preview ke liye) ----------
    story.append(PageBreak())
    story.append(Paragraph("Data Preview (first 20 rows)", heading_style))
    preview_df = df.head(20)
    table_data = [list(preview_df.columns)] + preview_df.astype(str).values.tolist()

    table = Table(table_data, repeatRows=1)
    table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#2F5496")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTSIZE", (0, 0), (-1, -1), 7),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#F2F2F2")]),
    ]))
    story.append(table)

    doc.build(story)

    # temp chart images clean karo
    for chart_cfg in chart_configs:
        chart_path = os.path.join(output_dir, f"_chart_{chart_cfg.get('x')}_{chart_cfg.get('y')}.png")
        if os.path.exists(chart_path):
            os.remove(chart_path)

    print(f"[PDFReport] Saved: {filename}")
    return filename
