# CSV to SQL ETL Pipeline

A simple **ETL (Extract, Transform, Load)** pipeline built in Python. Reads sales data from a CSV file, cleans and enriches it with Pandas, then loads it into a SQLite database using SQLAlchemy.

## Features

- **Extract** — reads sales data from CSV
- **Transform** — cleans, deduplicates, and enriches data:
  - Drops rows with missing critical fields (order_id, customer, quantity, price)
  - Fills missing values (product → "Unknown", date → today)
  - Type conversion (quantity → int, price → float, date → datetime)
  - Computes `total = quantity × price`
  - Removes duplicate order_ids
  - Trims whitespace
- **Load** — writes cleaned data to SQLite:
  - `sales` table — cleaned transactions
  - `summary_by_region` table — aggregated metrics
- **Logging** — every step is logged to `data/etl.log`
- **Verify** — `scripts/verify_db.py` for quick DB inspection

## Tech Stack

- **Python 3.14**
- **Pandas 3.0** — data manipulation
- **SQLAlchemy 2.1** — database abstraction
- **SQLite** — output database

## Project Structure

```
csv-to-sql-etl/
├── data/
│   ├── sales.csv           # Input CSV (test data)
│   ├── sales.db            # Output SQLite database (gitignored)
│   └── etl.log             # Pipeline log (gitignored)
├── scripts/
│   ├── etl_pipeline.py     # Main ETL script
│   └── verify_db.py        # Quick DB verification
├── .gitignore
├── README.md
└── requirements.txt
```
text

## Installation

### 1. Clone the repository

```bash
git clone https://github.com/mihail-serban-udescu/csv-to-sql-etl.git
cd csv-to-sql-etl
2. Create virtual environment
bash
python -m venv venv

# Windows
venv\Scripts\activate

# Linux/Mac
source venv/bin/activate
3. Install dependencies
bash
pip install -r requirements.txt
Usage
Run the ETL pipeline
bash
python scripts/etl_pipeline.py
Verify the database
bash
python scripts/verify_db.py
Input Format
data/sales.csv:

csv
order_id,customer,product,quantity,price,date,region
1001,Alice Johnson,Widget Pro,2,29.99,2026-01-15,North
1002,Bob Smith,Gadget X,1,59.99,2026-01-16,South
...
Output
sales table
Cleaned transactions with computed total column.

Column	Description
order_id	Unique order identifier
customer	Customer name
product	Product name
quantity	Quantity ordered
price	Unit price
date	Order date
region	Sales region
total	Computed total (quantity × price)
summary_by_region table
Column	Description
region	Sales region
total_orders	Number of orders
total_revenue	Sum of all orders
avg_order_value	Average order value
Example Output
text
============================================================
ETL Pipeline started
============================================================
EXTRACT: Loaded 15 rows, 7 columns
TRANSFORM: Dropped 2 rows with missing critical fields
TRANSFORM: Finished with 13 clean rows
LOAD: Wrote 13 rows to 'sales' table
LOAD: Wrote 4 rows to 'summary_by_region' table
LOAD: Summary by region:
  South: 4 orders, $449.90 revenue, avg $112.48
  West:  2 orders, $319.96 revenue, avg $159.98
  North: 4 orders, $249.94 revenue, avg $62.48
  East:  3 orders, $209.94 revenue, avg $69.98
============================================================
ETL Pipeline completed successfully
============================================================
Why this project
This project demonstrates ETL fundamentals in Python:

Similar in concept to enterprise ETL tools like IBM DataStage or Apache Airflow

Shows data cleaning, transformation, and loading best practices

Uses industry-standard libraries (Pandas, SQLAlchemy)

Includes logging and error handling for production-like pipelines

Requirements
Python 3.10+

See requirements.txt for package versions

License
Personal portfolio project — Mihail Serban, 2026.

