"""Quick DB verification script."""
import sqlite3
from pathlib import Path

import pandas as pd

DB = Path(__file__).resolve().parent.parent / "data" / "sales.db"

conn = sqlite3.connect(DB)

# Tabele
tables = pd.read_sql(
    "SELECT name FROM sqlite_master WHERE type='table'", conn
)
print("=== TABLES ===")
print(tables)

print()
print("=== SALES (first 5 rows) ===")
print(pd.read_sql("SELECT * FROM sales LIMIT 5", conn))

print()
print("=== SUMMARY BY REGION ===")
print(pd.read_sql("SELECT * FROM summary_by_region", conn))

conn.close()