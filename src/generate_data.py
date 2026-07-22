"""
Synthetic sales data generator for automated-report-distribution.

Produces three CSVs under data/ matching the star schema documented in
docs/design.md:
    - dim_store.csv
    - dim_product.csv
    - fact_sales.csv   (grain: one row per store/product/day transaction line)

Deterministic (seeded) so the committed sample report in reports/ is
reproducible from this script.
"""
from __future__ import annotations

import random
from datetime import date, timedelta
from pathlib import Path

import numpy as np
import pandas as pd

SEED = 42
random.seed(SEED)
np.random.seed(SEED)

DATA_DIR = Path(__file__).resolve().parent.parent / "data"

REGIONS = ["Central", "North", "Northeast", "South", "East"]
CATEGORIES = ["Grocery", "Fresh Food", "Beverages", "Household", "Electronics", "Apparel"]

N_STORES = 12
N_PRODUCTS = 60
N_DAYS = 90  # ~13 weeks of history so week-over-week trend charts have signal
END_DATE = date(2026, 7, 20)


def build_dim_store() -> pd.DataFrame:
    rows = []
    for i in range(1, N_STORES + 1):
        rows.append(
            {
                "store_id": f"ST-{i:03d}",
                "store_name": f"Makro {['Rangsit','Ladprao','Chaengwattana','Bangna','Ekamai','Ramindra','Saphankwai','Chiang Mai','Khon Kaen','Hat Yai','Pattaya','Nakhon Ratchasima'][i-1]}",
                "region": REGIONS[i % len(REGIONS)],
            }
        )
    return pd.DataFrame(rows)


def build_dim_product() -> pd.DataFrame:
    rows = []
    for i in range(1, N_PRODUCTS + 1):
        cat = CATEGORIES[i % len(CATEGORIES)]
        rows.append(
            {
                "product_id": f"PR-{i:04d}",
                "product_name": f"{cat} Item {i:04d}",
                "category": cat,
            }
        )
    return pd.DataFrame(rows)


def build_fact_sales(dim_store: pd.DataFrame, dim_product: pd.DataFrame) -> pd.DataFrame:
    # Give each category a different price band and each store a different
    # baseline demand multiplier, so the resulting report has real variation
    # in the top/bottom-store and category-mix charts.
    price_band = {
        "Grocery": (15, 90),
        "Fresh Food": (20, 150),
        "Beverages": (10, 60),
        "Household": (40, 300),
        "Electronics": (200, 3500),
        "Apparel": (150, 900),
    }
    store_multiplier = {row.store_id: np.random.uniform(0.6, 1.6) for row in dim_store.itertuples()}
    product_price = {
        row.product_id: round(np.random.uniform(*price_band[row.category]), 2)
        for row in dim_product.itertuples()
    }
    product_category = dict(zip(dim_product.product_id, dim_product.category))

    rows = []
    txn_counter = 1
    start_date = END_DATE - timedelta(days=N_DAYS - 1)
    for day_offset in range(N_DAYS):
        d = start_date + timedelta(days=day_offset)
        # weekday seasonality: weekends busier
        dow_factor = 1.3 if d.weekday() >= 5 else 1.0
        for store_row in dim_store.itertuples():
            n_lines_today = int(np.random.poisson(lam=25 * store_multiplier[store_row.store_id] * dow_factor))
            sampled_products = np.random.choice(dim_product.product_id, size=n_lines_today, replace=True)
            for product_id in sampled_products:
                qty = int(np.random.gamma(shape=2.0, scale=1.5)) + 1
                unit_price = product_price[product_id]
                rows.append(
                    {
                        "transaction_id": f"TXN-{txn_counter:06d}",
                        "sale_date": d.isoformat(),
                        "store_id": store_row.store_id,
                        "product_id": product_id,
                        "quantity": qty,
                        "unit_price": unit_price,
                        "revenue": round(qty * unit_price, 2),
                    }
                )
                txn_counter += 1
    return pd.DataFrame(rows)


def main() -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    dim_store = build_dim_store()
    dim_product = build_dim_product()
    fact_sales = build_fact_sales(dim_store, dim_product)

    dim_store.to_csv(DATA_DIR / "dim_store.csv", index=False)
    dim_product.to_csv(DATA_DIR / "dim_product.csv", index=False)
    fact_sales.to_csv(DATA_DIR / "fact_sales.csv", index=False)

    print(f"Wrote {len(dim_store)} stores, {len(dim_product)} products, {len(fact_sales)} transaction lines to {DATA_DIR}")


if __name__ == "__main__":
    main()
