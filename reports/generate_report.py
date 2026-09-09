"""
Automated executive report generator.
Queries the marketing_analytics warehouse, builds charts, and composes
a PDF executive summary. Designed to run unattended (e.g. via Windows
Task Scheduler) with zero manual steps.
"""

import os
import matplotlib
matplotlib.use("Agg")  # non-interactive backend, required for unattended/scheduled runs
import matplotlib.pyplot as plt
import pandas as pd
from datetime import datetime
from urllib.parse import quote_plus
from sqlalchemy import create_engine
from dotenv import load_dotenv

from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Image, Table, TableStyle
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle


def get_engine():
    load_dotenv()
    password_encoded = quote_plus(os.getenv("DB_PASSWORD"))
    db_url = f"postgresql://{os.getenv('DB_USER')}:{password_encoded}@{os.getenv('DB_HOST')}:{os.getenv('DB_PORT')}/{os.getenv('DB_NAME')}"
    return create_engine(db_url)


def fetch_kpis(engine):
    query = """
    SELECT
        SUM(CASE WHEN is_return = FALSE THEN total_amount ELSE 0 END) AS total_revenue,
        COUNT(DISTINCT CASE WHEN is_return = FALSE THEN invoice_number END) AS total_orders,
        COUNT(DISTINCT customer_key) AS total_customers
    FROM fact_sales;
    """
    kpis = pd.read_sql(query, engine).iloc[0]

    churn_query = "SELECT AVG(churn_probability) AS churn_rate FROM customer_churn_scores;"
    churn = pd.read_sql(churn_query, engine).iloc[0]

    return {
        "total_revenue": kpis["total_revenue"],
        "total_orders": kpis["total_orders"],
        "total_customers": kpis["total_customers"],
        "churn_rate": churn["churn_rate"],
    }


def fetch_monthly_trend(engine):
    query = """
    SELECT d.year, d.month, d.month_name,
        SUM(CASE WHEN f.is_return = FALSE THEN f.total_amount ELSE 0 END) AS revenue
    FROM fact_sales f
    JOIN dim_date d ON f.date_key = d.date_key
    GROUP BY d.year, d.month, d.month_name
    ORDER BY d.year, d.month;
    """
    return pd.read_sql(query, engine)


def fetch_top_categories(engine, n=7):
    query = """
    SELECT p.category,
        SUM(CASE WHEN f.is_return = FALSE THEN f.total_amount ELSE 0 END) AS revenue
    FROM fact_sales f
    JOIN dim_product p ON f.product_key = p.product_key
    GROUP BY p.category
    ORDER BY revenue DESC;
    """
    return pd.read_sql(query, engine).head(n)


def build_trend_chart(trend_df, output_path):
    trend_df = trend_df.copy()
    trend_df["label"] = trend_df["month_name"].str[:3] + " " + trend_df["year"].astype(str)

    fig, ax = plt.subplots(figsize=(7, 3))
    ax.plot(trend_df["label"], trend_df["revenue"], marker="o", linewidth=2, color="#2E5090")
    ax.set_title("Monthly Revenue Trend")
    ax.set_ylabel("Revenue")
    plt.xticks(rotation=45, ha="right", fontsize=7)
    plt.tight_layout()
    plt.savefig(output_path, dpi=150)
    plt.close(fig)


def build_category_chart(category_df, output_path):
    fig, ax = plt.subplots(figsize=(7, 3.5))
    ax.barh(category_df["category"], category_df["revenue"], color="#4C78A8")
    ax.set_xlabel("Revenue")
    ax.set_title("Revenue by Category")
    ax.invert_yaxis()
    plt.tight_layout()
    plt.savefig(output_path, dpi=150)
    plt.close(fig)


def build_pdf(kpis, trend_chart_path, category_chart_path, category_df, output_path):
    doc = SimpleDocTemplate(output_path, pagesize=letter,
                             topMargin=0.6*inch, bottomMargin=0.6*inch)
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle("TitleStyle", parent=styles["Title"], fontSize=20)
    subtitle_style = ParagraphStyle("SubtitleStyle", parent=styles["Normal"],
                                     fontSize=10, textColor=colors.grey)

    elements = []
    elements.append(Paragraph("Marketing Analytics Platform", title_style))
    elements.append(Paragraph(f"Executive Summary — Generated {datetime.now().strftime('%B %d, %Y %H:%M')}", subtitle_style))
    elements.append(Spacer(1, 0.3*inch))

    kpi_data = [
        ["Total Revenue", f"${kpis['total_revenue']:,.0f}"],
        ["Total Orders", f"{kpis['total_orders']:,}"],
        ["Total Customers", f"{kpis['total_customers']:,}"],
        ["Overall Churn Rate", f"{kpis['churn_rate']:.1%}"],
    ]
    kpi_table = Table(kpi_data, colWidths=[2.5*inch, 2.5*inch])
    kpi_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (0, -1), colors.HexColor("#1F3864")),
        ("TEXTCOLOR", (0, 0), (0, -1), colors.white),
        ("FONTSIZE", (0, 0), (-1, -1), 12),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
        ("TOPPADDING", (0, 0), (-1, -1), 8),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
    ]))
    elements.append(kpi_table)
    elements.append(Spacer(1, 0.4*inch))

    elements.append(Image(trend_chart_path, width=6.5*inch, height=2.8*inch))
    elements.append(Spacer(1, 0.3*inch))
    elements.append(Image(category_chart_path, width=6.5*inch, height=3.2*inch))
    elements.append(Spacer(1, 0.3*inch))

    elements.append(Paragraph("Top Categories by Revenue", styles["Heading2"]))
    cat_table_data = [["Category", "Revenue"]] + [
        [row["category"], f"${row['revenue']:,.0f}"] for _, row in category_df.iterrows()
    ]
    cat_table = Table(cat_table_data, colWidths=[3.5*inch, 2*inch])
    cat_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#4C78A8")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTSIZE", (0, 0), (-1, -1), 10),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
    ]))
    elements.append(cat_table)

    doc.build(elements)


def main():
    print(f"[{datetime.now()}] Starting report generation...")
    engine = get_engine()
    kpis = fetch_kpis(engine)
    trend_df = fetch_monthly_trend(engine)
    category_df = fetch_top_categories(engine)

    trend_chart_path = "trend_chart_temp.png"
    category_chart_path = "category_chart_temp.png"
    build_trend_chart(trend_df, trend_chart_path)
    build_category_chart(category_df, category_chart_path)

    date_str = datetime.now().strftime("%Y-%m-%d")
    output_path = f"executive_report_{date_str}.pdf"
    build_pdf(kpis, trend_chart_path, category_chart_path, category_df, output_path)

    os.remove(trend_chart_path)
    os.remove(category_chart_path)

    print(f"[{datetime.now()}] Report saved: {output_path}")


if __name__ == "__main__":
    main()