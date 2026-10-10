import json

import pandas as pd

from src.metrics import add_categories
from src.plots import create_charts
from src.reporting import build_summary
from src.storage import write_analysis_database
from src.sql_check import validate_sql_metrics


def sample_transactions():
    frame = pd.DataFrame(
        {
            "InvoiceNo": ["1", "2", "3"],
            "StockCode": ["A", "B", "C"],
            "Description": ["CERAMIC MUG", "PARTY BUNTING", "WOODEN FRAME"],
            "Quantity": [2, 1, 1],
            "InvoiceDate": pd.to_datetime(
                ["2011-01-01", "2011-02-01", "2011-02-02"]
            ),
            "UnitPrice": [5.0, 20.0, 10.0],
            "CustomerID": pd.Series([10, 20, 10], dtype="Int64"),
            "Country": ["United Kingdom", "France", "United Kingdom"],
            "Revenue": [10.0, 20.0, 10.0],
        }
    )
    return add_categories(frame)


def test_build_summary_labels_source_and_leads_with_findings():
    summary, metrics = build_summary(sample_transactions(), "REAL - Online Retail II")

    assert "REAL - Online Retail II" in summary
    assert "Party & Gift Wrap" in summary
    assert "50.0%" in summary
    assert metrics["leading_category"] == "Party & Gift Wrap"


def test_sql_check_matches_generated_metrics(tmp_path):
    frame = sample_transactions()
    database_path = tmp_path / "analysis.db"
    metrics_path = tmp_path / "metrics.json"
    _, metrics = build_summary(frame, "REAL - test")
    write_analysis_database(frame, database_path)
    metrics_path.write_text(json.dumps(metrics), encoding="utf-8")

    checks = validate_sql_metrics(database_path, metrics_path)

    assert checks
    assert all(check["passed"] for check in checks)


def test_create_charts_writes_three_nonempty_pngs(tmp_path):
    paths = create_charts(sample_transactions(), tmp_path)

    assert len(paths) == 3
    assert all(path.exists() and path.stat().st_size > 0 for path in paths)
