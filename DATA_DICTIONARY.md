# Data dictionary

## Source

Online Retail II contains transactions from a UK-based non-store giftware retailer from 1 December 2009 to 9 December 2011. The workbook has two sheets (`Year 2009-2010` and `Year 2010-2011`) and 1,067,371 source rows. The pipeline combines both sheets before cleaning.

## Canonical columns

| Column | Meaning | Treatment |
| --- | --- | --- |
| `InvoiceNo` | Transaction identifier | Source column `Invoice`; values beginning with `C` are cancellations and are excluded. |
| `StockCode` | Product identifier | Used to exclude administrative, postage, and adjustment codes. |
| `Description` | Free-text item description | Missing descriptions are excluded; remaining text feeds the category rules. |
| `Quantity` | Units on the line | Must be greater than zero. Negative quantities are returns. |
| `InvoiceDate` | Transaction timestamp | Parsed to a timestamp; invalid dates are excluded. |
| `UnitPrice` | Price per unit in pounds sterling | Source column `Price`; must be greater than zero. |
| `CustomerID` | Customer identifier | Source column `Customer ID`; nullable and stored as an integer when present. |
| `Country` | Customer country | Used for geography aggregation. |

## Derived fields

| Field | Definition |
| --- | --- |
| `Revenue` | `Quantity × UnitPrice`; gross merchandise value, not profit or recognized accounting revenue. |
| `Category` | First matching keyword rule in `src/metrics.py::CATEGORY_RULES`; otherwise `Other`. |
| `month` | Calendar month derived from `InvoiceDate` in `YYYY-MM` format. |
| `average_order_value` | Monthly revenue divided by distinct invoice count. |

## Cleaning rules

The analysis removes cancellations, non-positive quantities, non-positive prices, missing descriptions, invalid dates, and non-merchandise records. Non-merchandise detection combines known stock codes (`POST`, `DOT`, `M`, `D`, `BANK CHARGES`, and related adjustment codes) with description terms such as `POSTAGE`, `CARRIAGE`, `MANUAL`, and `AMAZON FEE`.

These choices produce 1,036,899 merchandise lines from 1,067,371 source rows. A different treatment of postage, manual adjustments, or returns will produce different totals.

## Category mapping

The rules group description keywords into eight working categories: Home Decor, Kitchen & Dining, Party & Gift Wrap, Bags & Accessories, Toys & Stationery, Garden & Outdoor, Bath & Personal Care, and Crafts & Sewing. After reviewing the highest-revenue unmatched descriptions, the rules explicitly cover common source variants including `CAKESTAND`, `TEACUP`, `LIGHTS`, `MEMOBOARD`, `SNAP CARDS`, `JAM MAKING`, and `STORAGE CUBES`.

The final `Other` share is 12.6% of cleaned revenue. That is acceptable for directional analysis, but the mapping remains a portfolio approximation. Similar products can be named inconsistently, and rule order matters when a description contains keywords from multiple categories.

## Known limitations

- There is no cost field, so the project measures revenue rather than margin or profit.
- There is no promotion or discount flag. A month with more orders and lower revenue is only a signal of price or mix change.
- Unidentified customers contribute to total revenue but not to customer-level rankings. Therefore the cumulative customer chart ends below 100% of all revenue.
- The final month is incomplete: the source ends on 9 December 2011.
- One retailer and a giftware-heavy product mix are not representative of e-commerce as a whole.
