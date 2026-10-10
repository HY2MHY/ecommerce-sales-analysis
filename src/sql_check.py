import argparse
import json
from pathlib import Path
import sqlite3


SQL_METRICS = {
    "rows": "SELECT COUNT(*) FROM transactions",
    "orders": "SELECT COUNT(DISTINCT InvoiceNo) FROM transactions",
    "customers": "SELECT COUNT(DISTINCT CustomerID) FROM transactions",
    "total_revenue": "SELECT SUM(Revenue) FROM transactions",
    "uk_revenue_share": """
        SELECT SUM(CASE WHEN Country = 'United Kingdom' THEN Revenue ELSE 0 END)
               / SUM(Revenue)
        FROM transactions
    """,
    "top_customer_share": """
        WITH customers AS (
          SELECT CustomerID, SUM(Revenue) AS revenue
          FROM transactions WHERE CustomerID IS NOT NULL GROUP BY CustomerID
        )
        SELECT MAX(revenue) / (SELECT SUM(Revenue) FROM transactions) FROM customers
    """,
    "top_10_customer_share": """
        WITH customers AS (
          SELECT CustomerID, SUM(Revenue) AS revenue
          FROM transactions WHERE CustomerID IS NOT NULL GROUP BY CustomerID
        )
        SELECT SUM(revenue) / (SELECT SUM(Revenue) FROM transactions)
        FROM (SELECT revenue FROM customers ORDER BY revenue DESC LIMIT 10)
    """,
    "leading_category": """
        SELECT Category FROM transactions GROUP BY Category ORDER BY SUM(Revenue) DESC LIMIT 1
    """,
    "leading_category_share": """
        SELECT SUM(Revenue) / (SELECT SUM(Revenue) FROM transactions)
        FROM transactions GROUP BY Category ORDER BY SUM(Revenue) DESC LIMIT 1
    """,
    "other_category_share": """
        SELECT COALESCE(SUM(CASE WHEN Category = 'Other' THEN Revenue ELSE 0 END), 0)
               / SUM(Revenue)
        FROM transactions
    """,
    "peak_month": """
        SELECT substr(InvoiceDate, 1, 7) FROM transactions
        GROUP BY substr(InvoiceDate, 1, 7) ORDER BY SUM(Revenue) DESC LIMIT 1
    """,
    "peak_month_revenue": """
        SELECT SUM(Revenue) FROM transactions
        GROUP BY substr(InvoiceDate, 1, 7) ORDER BY SUM(Revenue) DESC LIMIT 1
    """,
    "peak_month_orders": """
        SELECT COUNT(DISTINCT InvoiceNo) FROM transactions
        GROUP BY substr(InvoiceDate, 1, 7) ORDER BY SUM(Revenue) DESC LIMIT 1
    """,
}


def validate_sql_metrics(database_path: str | Path, metrics_path: str | Path):
    expected = json.loads(Path(metrics_path).read_text(encoding="utf-8"))
    checks = []
    with sqlite3.connect(database_path) as connection:
        for name, query in SQL_METRICS.items():
            actual = connection.execute(query).fetchone()[0]
            target = expected[name]
            if isinstance(target, float):
                tolerance = max(1e-7, abs(target) * 1e-7)
                passed = abs(float(actual) - target) <= tolerance
            else:
                passed = actual == target
            checks.append(
                {"metric": name, "python": target, "sql": actual, "passed": passed}
            )
    return checks


def main():
    parser = argparse.ArgumentParser(description="Cross-check Python findings in SQLite.")
    parser.add_argument("--database", default="data/processed/ecommerce.db")
    parser.add_argument("--metrics", default="reports/metrics.json")
    args = parser.parse_args()
    checks = validate_sql_metrics(args.database, args.metrics)
    for check in checks:
        status = "PASS" if check["passed"] else "FAIL"
        print(f"{status:4} {check['metric']}: Python={check['python']} SQL={check['sql']}")
    if not all(check["passed"] for check in checks):
        raise SystemExit("SQL cross-check failed.")


if __name__ == "__main__":
    main()
