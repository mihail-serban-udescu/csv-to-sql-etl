"""
CSV to SQL ETL Pipeline
=======================
Extract:   Read sales data from CSV
Transform: Clean, deduplicate, compute totals, aggregate by region
Load:      Insert into SQLite database (sales + summary tables)

Usage:
    python scripts/etl_pipeline.py
"""

import os
import sys
from pathlib import Path
from datetime import datetime

import pandas as pd
from sqlalchemy import create_engine, text


# ============================================================
# Configuration
# ============================================================

# Project root (one level up from scripts/)
BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
INPUT_CSV = DATA_DIR / "sales.csv"
OUTPUT_DB = DATA_DIR / "sales.db"
LOG_FILE = DATA_DIR / "etl.log"


# ============================================================
# Logging helper
# ============================================================

def log(message: str) -> None:
    """Print + append to log file."""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    line = f"[{timestamp}] {message}"
    print(line)
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(line + "\n")


# ============================================================
# EXTRACT
# ============================================================

def extract() -> pd.DataFrame:
    """Read CSV into DataFrame."""
    log(f"EXTRACT: Reading {INPUT_CSV}")
    if not INPUT_CSV.exists():
        log(f"ERROR: {INPUT_CSV} not found")
        sys.exit(1)

    df = pd.read_csv(INPUT_CSV)
    log(f"EXTRACT: Loaded {len(df)} rows, {len(df.columns)} columns")
    return df

# ============================================================
# TRANSFORM
# ============================================================

def transform(df: pd.DataFrame) -> pd.DataFrame:
    """Clean and enrich data."""
    log(f"TRANSFORM: Starting with {len(df)} rows")

    # 1. Drop rows with missing critical fields
    critical_cols = ["order_id", "customer", "quantity", "price"]
    before = len(df)
    df = df.dropna(subset=critical_cols)
    log(f"TRANSFORM: Dropped {before - len(df)} rows with missing critical fields")

    # 2. Fill missing product with 'Unknown'
    df["product"] = df["product"].fillna("Unknown")

    # 3. Fill missing date with today's date
    df["date"] = df["date"].fillna(datetime.now().strftime("%Y-%m-%d"))

    # 4. Convert types
    df["quantity"] = df["quantity"].astype(int)
    df["price"] = df["price"].astype(float)
    df["date"] = pd.to_datetime(df["date"])

    # 5. Compute total per order
    df["total"] = (df["quantity"] * df["price"]).round(2)

    # 6. Remove duplicates (same order_id)
    before = len(df)
    df = df.drop_duplicates(subset=["order_id"], keep="first")
    log(f"TRANSFORM: Removed {before - len(df)} duplicate order_ids")

    # 7. Trim whitespace on string columns
    for col in ["customer", "product", "region"]:
        if col in df.columns:
            df[col] = df[col].astype(str).str.strip()

    log(f"TRANSFORM: Finished with {len(df)} clean rows")
    return df

# ============================================================
# LOAD
# ============================================================

def load(df: pd.DataFrame) -> None:
    """Insert into SQLite."""
    log(f"LOAD: Writing to {OUTPUT_DB}")

    engine = create_engine(f"sqlite:///{OUTPUT_DB}")

    # 1. Write cleaned data
    df.to_sql("sales", engine, if_exists="replace", index=False)
    log(f"LOAD: Wrote {len(df)} rows to 'sales' table")

    # 2. Aggregate by region
    summary = (
        df.groupby("region")
        .agg(
            total_orders=("order_id", "count"),
            total_revenue=("total", "sum"),
            avg_order_value=("total", "mean"),
        )
        .round(2)
        .reset_index()
        .sort_values("total_revenue", ascending=False)
    )
    summary.to_sql("summary_by_region", engine, if_exists="replace", index=False)
    log(f"LOAD: Wrote {len(summary)} rows to 'summary_by_region' table")

    # 3. Show summary
    log("LOAD: Summary by region:")
    for _, row in summary.iterrows():
        log(f"  {row['region']}: {row['total_orders']} orders, "
            f"${row['total_revenue']:.2f} revenue, "
            f"avg ${row['avg_order_value']:.2f}")


# ============================================================
# MAIN
# ============================================================

def main() -> None:
    log("=" * 60)
    log("ETL Pipeline started")
    log("=" * 60)

    df_raw = extract()
    df_clean = transform(df_raw)
    load(df_clean)

    log("=" * 60)
    log("ETL Pipeline completed successfully")
    log("=" * 60)


if __name__ == "__main__":
    main()