import sqlite3
from pathlib import Path

import pandas as pd


def write_analysis_database(frame: pd.DataFrame, path: str | Path) -> Path:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    stored = frame.copy()
    stored["InvoiceDate"] = stored["InvoiceDate"].dt.strftime("%Y-%m-%d %H:%M:%S")
    with sqlite3.connect(path) as connection:
        stored.to_sql("transactions", connection, if_exists="replace", index=False)
        connection.execute(
            "CREATE INDEX IF NOT EXISTS idx_transactions_invoice ON transactions (InvoiceNo)"
        )
        connection.execute(
            "CREATE INDEX IF NOT EXISTS idx_transactions_date ON transactions (InvoiceDate)"
        )
    return path
