"""
Builds a weekly sales report (HTML + PDF) from the synthetic star schema in
data/. This is the core "automated dashboard, distributed to N recipients"
workflow: aggregate -> chart -> render -> (would-be) distribute.

Usage:
    python src/generate_data.py   # once, to (re)create data/*.csv
    python src/build_report.py    # builds reports/sales_report_<date>.{html,pdf}
"""
from __future__ import annotations

import base64
from datetime import date
from io import BytesIO
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
import pandas as pd

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
REPORTS_DIR = BASE_DIR / "reports"


def load_data() -> pd.DataFrame:
    fact = pd.read_csv(DATA_DIR / "fact_sales.csv", parse_dates=["sale_date"])
    dim_store = pd.read_csv(DATA_DIR / "dim_store.csv")
    dim_product = pd.read_csv(DATA_DIR / "dim_product.csv")
    df = fact.merge(dim_store, on="store_id").merge(dim_product, on="product_id")
    return df


def weekly_trend_chart(df: pd.DataFrame) -> plt.Figure:
    weekly = df.set_index("sale_date").resample("W-MON")["revenue"].sum().reset_index()
    fig, ax = plt.subplots(figsize=(8, 4))
    ax.plot(weekly["sale_date"], weekly["revenue"], marker="o", color="#2563eb")
    ax.set_title("Weekly Revenue Trend")
    ax.set_ylabel("Revenue (THB)")
    ax.set_xlabel("Week")
    fig.autofmt_xdate()
    fig.tight_layout()
    return fig


def store_performance_chart(df: pd.DataFrame) -> plt.Figure:
    by_store = df.groupby("store_name")["revenue"].sum().sort_values(ascending=False)
    fig, ax = plt.subplots(figsize=(8, 5))
    colors = ["#16a34a"] * 5 + ["#9ca3af"] * (len(by_store) - 10) + ["#dc2626"] * 5
    colors = colors[: len(by_store)]
    by_store.plot(kind="barh", ax=ax, color=colors)
    ax.invert_yaxis()
    ax.set_title("Total Revenue by Store (top 5 green, bottom 5 red)")
    ax.set_xlabel("Revenue (THB)")
    fig.tight_layout()
    return fig


def category_mix_chart(df: pd.DataFrame) -> plt.Figure:
    by_cat = df.groupby("category")["revenue"].sum().sort_values(ascending=False)
    fig, ax = plt.subplots(figsize=(6, 6))
    ax.pie(by_cat.values, labels=by_cat.index, autopct="%1.0f%%", startangle=90)
    ax.set_title("Revenue Mix by Category")
    fig.tight_layout()
    return fig


def fig_to_base64(fig: plt.Figure) -> str:
    buf = BytesIO()
    fig.savefig(buf, format="png", dpi=110)
    buf.seek(0)
    return base64.b64encode(buf.read()).decode("ascii")


def build_summary(df: pd.DataFrame) -> dict:
    total_revenue = df["revenue"].sum()
    n_transactions = len(df)
    top_store = df.groupby("store_name")["revenue"].sum().idxmax()
    top_category = df.groupby("category")["revenue"].sum().idxmax()
    date_min, date_max = df["sale_date"].min().date(), df["sale_date"].max().date()
    return {
        "total_revenue": total_revenue,
        "n_transactions": n_transactions,
        "top_store": top_store,
        "top_category": top_category,
        "period": f"{date_min.isoformat()} to {date_max.isoformat()}",
    }


HTML_TEMPLATE = """<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<title>Weekly Sales Report - {period}</title>
<style>
  body {{ font-family: -apple-system, Segoe UI, Arial, sans-serif; margin: 40px; color: #1f2937; }}
  h1 {{ color: #111827; }}
  .summary {{ display: flex; gap: 24px; margin: 24px 0; }}
  .card {{ background: #f3f4f6; border-radius: 8px; padding: 16px 20px; flex: 1; }}
  .card .label {{ font-size: 12px; color: #6b7280; text-transform: uppercase; }}
  .card .value {{ font-size: 22px; font-weight: 700; margin-top: 4px; }}
  img {{ max-width: 100%; margin: 16px 0; border: 1px solid #e5e7eb; border-radius: 6px; }}
  footer {{ margin-top: 40px; font-size: 12px; color: #9ca3af; }}
</style>
</head>
<body>
  <h1>Weekly Sales Report</h1>
  <p>Reporting period: <strong>{period}</strong></p>
  <div class="summary">
    <div class="card"><div class="label">Total Revenue</div><div class="value">THB {total_revenue:,.0f}</div></div>
    <div class="card"><div class="label">Transactions</div><div class="value">{n_transactions:,}</div></div>
    <div class="card"><div class="label">Top Store</div><div class="value">{top_store}</div></div>
    <div class="card"><div class="label">Top Category</div><div class="value">{top_category}</div></div>
  </div>
  <h2>Weekly Revenue Trend</h2>
  <img src="data:image/png;base64,{trend_b64}">
  <h2>Store Performance</h2>
  <img src="data:image/png;base64,{store_b64}">
  <h2>Category Mix</h2>
  <img src="data:image/png;base64,{cat_b64}">
  <footer>Generated automatically by build_report.py from synthetic data. Not a real business report.</footer>
</body>
</html>
"""


def build_html(summary: dict, trend_fig, store_fig, cat_fig, out_path: Path) -> None:
    html = HTML_TEMPLATE.format(
        period=summary["period"],
        total_revenue=summary["total_revenue"],
        n_transactions=summary["n_transactions"],
        top_store=summary["top_store"],
        top_category=summary["top_category"],
        trend_b64=fig_to_base64(trend_fig),
        store_b64=fig_to_base64(store_fig),
        cat_b64=fig_to_base64(cat_fig),
    )
    out_path.write_text(html, encoding="utf-8")


def build_pdf(summary: dict, trend_fig, store_fig, cat_fig, out_path: Path) -> None:
    with PdfPages(out_path) as pdf:
        # Title / summary page
        fig, ax = plt.subplots(figsize=(8.5, 5))
        ax.axis("off")
        ax.text(0.5, 0.85, "Weekly Sales Report", ha="center", fontsize=22, weight="bold")
        ax.text(0.5, 0.75, f"Period: {summary['period']}", ha="center", fontsize=12)
        lines = [
            f"Total Revenue: THB {summary['total_revenue']:,.0f}",
            f"Transactions: {summary['n_transactions']:,}",
            f"Top Store: {summary['top_store']}",
            f"Top Category: {summary['top_category']}",
        ]
        for i, line in enumerate(lines):
            ax.text(0.5, 0.55 - i * 0.08, line, ha="center", fontsize=13)
        pdf.savefig(fig)
        plt.close(fig)

        for f in (trend_fig, store_fig, cat_fig):
            pdf.savefig(f)


def main() -> None:
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    df = load_data()
    summary = build_summary(df)

    trend_fig = weekly_trend_chart(df)
    store_fig = store_performance_chart(df)
    cat_fig = category_mix_chart(df)

    report_date = date.today().isoformat()
    html_path = REPORTS_DIR / f"sample_report_{report_date}.html"
    pdf_path = REPORTS_DIR / f"sample_report_{report_date}.pdf"

    build_html(summary, trend_fig, store_fig, cat_fig, html_path)
    build_pdf(summary, trend_fig, store_fig, cat_fig, pdf_path)

    plt.close(trend_fig)
    plt.close(store_fig)
    plt.close(cat_fig)

    print(f"Wrote {html_path}")
    print(f"Wrote {pdf_path}")


if __name__ == "__main__":
    main()
