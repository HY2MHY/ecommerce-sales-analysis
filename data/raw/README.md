# Raw data

Download `online_retail_II.xlsx` from the [UCI Online Retail II dataset page](https://archive.ics.uci.edu/dataset/502/online+retail+ii) and place it in this directory.

Expected path:

```text
data/raw/online_retail_II.xlsx
```

The workbook should contain the `Year 2009-2010` and `Year 2010-2011` sheets. The loader validates and renames the source headers (`Invoice`, `Price`, and `Customer ID`) to the canonical names documented in `DATA_DICTIONARY.md`. It raises a visible error if required columns are missing.

The workbook is licensed CC BY 4.0 and is intentionally excluded from Git.
