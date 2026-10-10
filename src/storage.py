from pathlib import Path
import sqlite3

import pandas as pd

from src.metrics import (
    category_performance,
    country_performance,
    customer_performance,
    monthly_performance,
)


def write_analysis_database(frame: pd.DataFrame, path: str | Path) -> Path:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    stored = frame.copy()
    stored["InvoiceDate"] = stored["InvoiceDate"].dt.strftime("%Y-%m-%d %H:%M:%S")
    with sqlite3.connect(path) as connection:
        stored.to_sql("transactions", connection, if_exists="replace", index=False)
        category_performance(frame).to_sql(
            "category_performance", connection, if_exists="replace", index=False
        )
        country_performance(frame).to_sql(
            "country_performance", connection, if_exists="replace", index=False
        )
        customer_performance(frame).to_sql(
            "customer_performance", connection, if_exists="replace", index=False
        )
        monthly_performance(frame).to_sql(
            "monthly_performance", connection, if_exists="replace", index=False
        )
        connection.execute(
            "CREATE INDEX IF NOT EXISTS idx_transactions_invoice ON transactions (InvoiceNo)"
        )
        connection.execute(
            "CREATE INDEX IF NOT EXISTS idx_transactions_date ON transactions (InvoiceDate)"
        )
    return path
