from pathlib import Path

import pandas as pd


CANONICAL_COLUMNS = [
    "InvoiceNo",
    "StockCode",
    "Description",
    "Quantity",
    "InvoiceDate",
    "UnitPrice",
    "CustomerID",
    "Country",
]

COLUMN_ALIASES = {
    "Invoice": "InvoiceNo",
    "Price": "UnitPrice",
    "Customer ID": "CustomerID",
}

NON_MERCHANDISE_CODES = {
    "ADJUST",
    "ADJUST2",
    "BANK CHARGES",
    "C2",
    "CRUK",
    "D",
    "DOT",
    "M",
    "POST",
    "S",
}

NON_MERCHANDISE_TERMS = (
    "AMAZON FEE",
    "BANK CHARGES",
    "CARRIAGE",
    "DOTCOM POSTAGE",
    "MANUAL",
    "POSTAGE",
    "SAMPLES",
)


def _canonicalize_columns(frame: pd.DataFrame) -> pd.DataFrame:
    renamed = frame.rename(columns=COLUMN_ALIASES)
    missing = sorted(set(CANONICAL_COLUMNS) - set(renamed.columns))
    unexpected = sorted(set(renamed.columns) - set(CANONICAL_COLUMNS))
    if missing:
        raise ValueError(
            f"Dataset schema mismatch. Missing columns: {missing}. "
            f"Unexpected columns: {unexpected}."
        )
    return renamed[CANONICAL_COLUMNS].copy()


def clean_transactions(frame: pd.DataFrame) -> pd.DataFrame:
    cleaned = _canonicalize_columns(frame)
    cleaned["InvoiceNo"] = cleaned["InvoiceNo"].astype("string").str.strip()
    cleaned["StockCode"] = cleaned["StockCode"].astype("string").str.strip()
    cleaned["Description"] = cleaned["Description"].astype("string").str.strip()
    cleaned["Country"] = cleaned["Country"].astype("string").str.strip()
    cleaned["InvoiceDate"] = pd.to_datetime(cleaned["InvoiceDate"], errors="coerce")
    cleaned["Quantity"] = pd.to_numeric(cleaned["Quantity"], errors="coerce")
    cleaned["UnitPrice"] = pd.to_numeric(cleaned["UnitPrice"], errors="coerce")
    cleaned["CustomerID"] = pd.to_numeric(cleaned["CustomerID"], errors="coerce").astype(
        "Int64"
    )

    description_upper = cleaned["Description"].str.upper()
    is_non_merchandise = cleaned["StockCode"].str.upper().isin(
        NON_MERCHANDISE_CODES
    ) | description_upper.str.contains("|".join(NON_MERCHANDISE_TERMS), na=False)

    valid = (
        cleaned["InvoiceNo"].notna()
        & ~cleaned["InvoiceNo"].str.upper().str.startswith("C", na=False)
        & cleaned["Description"].notna()
        & cleaned["InvoiceDate"].notna()
        & (cleaned["Quantity"] > 0)
        & (cleaned["UnitPrice"] > 0)
        & ~is_non_merchandise
    )
    cleaned = cleaned.loc[valid].copy()
    cleaned["Revenue"] = cleaned["Quantity"] * cleaned["UnitPrice"]
    return cleaned.reset_index(drop=True)


def load_transactions(path: str | Path) -> pd.DataFrame:
    path = Path(path)
    if not path.exists():
        raise FileNotFoundError(
            f"Real dataset not found at {path}. See data/raw/README.md for download steps."
        )

    workbook = pd.ExcelFile(path)
    if not workbook.sheet_names:
        raise ValueError(f"Dataset workbook has no sheets: {path}")
    parts = [pd.read_excel(path, sheet_name=sheet) for sheet in workbook.sheet_names]
    return clean_transactions(pd.concat(parts, ignore_index=True))


def synthetic_transactions() -> pd.DataFrame:
    """Small deterministic fixture for smoke-testing the pipeline, never for findings."""
    rows = [
        ("S1001", "85123A", "WHITE HANGING HEART T-LIGHT HOLDER", 12, "2011-01-03", 2.95, 10001, "United Kingdom"),
        ("S1002", "22720", "SET OF 3 CAKE TINS PANTRY DESIGN", 6, "2011-02-04", 4.95, 10002, "France"),
        ("S1003", "22423", "REGENCY CAKESTAND 3 TIER", 4, "2011-03-05", 12.75, 10003, "United Kingdom"),
        ("S1004", "47566", "PARTY BUNTING", 10, "2011-04-06", 4.65, 10004, "Germany"),
        ("S1005", "84879", "ASSORTED COLOUR BIRD ORNAMENT", 8, "2011-05-07", 1.69, 10001, "United Kingdom"),
    ]
    return clean_transactions(pd.DataFrame(rows, columns=CANONICAL_COLUMNS))
