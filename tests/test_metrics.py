import pandas as pd
import pytest

from src.data_loader import clean_transactions
from src.metrics import (
    add_categories,
    headline_metrics,
    monthly_performance,
)


@pytest.fixture
def raw_transactions():
    return pd.DataFrame(
        {
            "InvoiceNo": ["10001", "10001", "C10002", "10003", "10004"],
            "StockCode": ["A", "B", "A", "C", "D"],
            "Description": [
                "RED RETROSPOT MUG",
                "WOODEN PICTURE FRAME",
                "RED RETROSPOT MUG",
                None,
                "POSTAGE",
            ],
            "Quantity": [2, 1, -2, 3, 1],
            "InvoiceDate": pd.to_datetime(
                [
                    "2011-01-01 09:00",
                    "2011-01-01 09:00",
                    "2011-01-02 10:00",
                    "2011-02-01 11:00",
                    "2011-02-03 12:00",
                ]
            ),
            "UnitPrice": [3.0, 10.0, 3.0, 5.0, 2.0],
            "CustomerID": [12345, 12345, 12345, 22222, 99999],
            "Country": ["United Kingdom"] * 5,
        }
    )


def test_clean_transactions_excludes_cancellations_invalid_rows_and_non_merchandise(
    raw_transactions,
):
    cleaned = clean_transactions(raw_transactions)

    assert cleaned["InvoiceNo"].tolist() == ["10001", "10001"]
    assert cleaned["Revenue"].tolist() == [6.0, 10.0]


def test_add_categories_uses_description_keywords():
    frame = pd.DataFrame(
        {
            "Description": [
                "RED RETROSPOT MUG",
                "WOODEN PICTURE FRAME",
                "FAIRY CAKE CASES",
                "UNMATCHED PRODUCT",
            ]
        }
    )

    result = add_categories(frame)

    assert result["Category"].tolist() == [
        "Kitchen & Dining",
        "Home Decor",
        "Party & Gift Wrap",
        "Other",
    ]


def test_add_categories_handles_common_retail_description_variants():
    frame = pd.DataFrame(
        {
            "Description": [
                "REGENCY CAKESTAND 3 TIER",
                "CHILLI LIGHTS",
                "VINTAGE SNAP CARDS",
                "JAM MAKING SET WITH JARS",
            ]
        }
    )

    assert add_categories(frame)["Category"].tolist() == [
        "Kitchen & Dining",
        "Home Decor",
        "Toys & Stationery",
        "Kitchen & Dining",
    ]


def test_headline_metrics_calculates_country_and_customer_concentration():
    frame = pd.DataFrame(
        {
            "InvoiceNo": ["1", "2", "3", "4"],
            "CustomerID": [10, 20, 30, 40],
            "Country": ["United Kingdom", "France", "United Kingdom", "Germany"],
            "Revenue": [70.0, 10.0, 10.0, 10.0],
        }
    )

    result = headline_metrics(frame)

    assert result["total_revenue"] == 100.0
    assert result["uk_revenue_share"] == pytest.approx(0.8)
    assert result["top_customer_share"] == pytest.approx(0.7)
    assert result["top_10_customer_share"] == pytest.approx(1.0)


def test_monthly_performance_counts_distinct_orders():
    frame = pd.DataFrame(
        {
            "InvoiceNo": ["1", "1", "2"],
            "InvoiceDate": pd.to_datetime(
                ["2011-01-01", "2011-01-01", "2011-02-01"]
            ),
            "Revenue": [5.0, 7.0, 20.0],
        }
    )

    result = monthly_performance(frame)

    assert result["orders"].tolist() == [1, 1]
    assert result["revenue"].tolist() == [12.0, 20.0]
