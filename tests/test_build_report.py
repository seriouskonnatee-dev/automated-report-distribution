import sys
from pathlib import Path

import pandas as pd

SRC_DIR = Path(__file__).resolve().parent.parent / "src"
sys.path.insert(0, str(SRC_DIR))

from build_report import build_summary, weekly_trend_chart, store_performance_chart, category_mix_chart  # noqa: E402


def _sample_df() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "sale_date": pd.to_datetime(["2026-07-01", "2026-07-02", "2026-07-08"]),
            "store_name": ["Store A", "Store B", "Store A"],
            "category": ["Grocery", "Beverages", "Grocery"],
            "revenue": [100.0, 50.0, 200.0],
        }
    )


def test_build_summary_totals():
    df = _sample_df()
    summary = build_summary(df)
    assert summary["total_revenue"] == 350.0
    assert summary["n_transactions"] == 3
    assert summary["top_store"] == "Store A"
    assert summary["top_category"] == "Grocery"
    assert summary["period"] == "2026-07-01 to 2026-07-08"


def test_charts_return_figures():
    df = _sample_df()
    for fig in (weekly_trend_chart(df), store_performance_chart(df), category_mix_chart(df)):
        assert fig is not None
        assert len(fig.axes) >= 1
