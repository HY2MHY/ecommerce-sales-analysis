-- Independent SQL checks for data/processed/ecommerce.db.
-- Run with: sqlite3 data/processed/ecommerce.db < sql/analysis.sql

.headers on
.mode column

SELECT
  COUNT(*) AS cleaned_rows,
  COUNT(DISTINCT InvoiceNo) AS orders,
  COUNT(DISTINCT CustomerID) AS identified_customers,
  ROUND(SUM(Revenue), 2) AS total_revenue
FROM transactions;

SELECT
  Category,
  ROUND(SUM(Revenue), 2) AS revenue,
  ROUND(100.0 * SUM(Revenue) / (SELECT SUM(Revenue) FROM transactions), 1) AS revenue_pct
FROM transactions
GROUP BY Category
ORDER BY revenue DESC;

SELECT
  ROUND(
    100.0 * SUM(CASE WHEN Country = 'United Kingdom' THEN Revenue ELSE 0 END)
    / SUM(Revenue),
    1
  ) AS uk_revenue_pct
FROM transactions;

WITH customer_revenue AS (
  SELECT CustomerID, SUM(Revenue) AS revenue
  FROM transactions
  WHERE CustomerID IS NOT NULL
  GROUP BY CustomerID
), ranked AS (
  SELECT revenue, ROW_NUMBER() OVER (ORDER BY revenue DESC) AS revenue_rank
  FROM customer_revenue
)
SELECT
  ROUND(100.0 * MAX(revenue) / (SELECT SUM(Revenue) FROM transactions), 1) AS top_customer_pct,
  ROUND(
    100.0 * SUM(CASE WHEN revenue_rank <= 10 THEN revenue ELSE 0 END)
    / (SELECT SUM(Revenue) FROM transactions),
    1
  ) AS top_10_customers_pct
FROM ranked;

SELECT
  substr(InvoiceDate, 1, 7) AS month,
  COUNT(DISTINCT InvoiceNo) AS orders,
  ROUND(SUM(Revenue), 2) AS revenue
FROM transactions
GROUP BY month
ORDER BY revenue DESC
LIMIT 1;

WITH monthly AS (
  SELECT
    substr(InvoiceDate, 1, 7) AS month,
    COUNT(DISTINCT InvoiceNo) AS orders,
    SUM(Revenue) AS revenue
  FROM transactions
  GROUP BY month
), compared AS (
  SELECT
    month,
    orders,
    revenue,
    LAG(orders) OVER (ORDER BY month) AS previous_orders,
    LAG(revenue) OVER (ORDER BY month) AS previous_revenue
  FROM monthly
)
SELECT month, orders, ROUND(revenue, 2) AS revenue
FROM compared
WHERE orders > previous_orders AND revenue <= previous_revenue
ORDER BY month;
