# Analysis summary

**Data source:** REAL - UCI Online Retail II

After excluding cancellations, returns, invalid prices or quantities, and non-merchandise charges, the analysis covers **1,036,899 line items**, **39,527 orders**, and **5,852 identified customers**. Cleaned merchandise revenue is **£20,120,171**.

## 1. Product mix

**Home Decor leads the category view at £6,092,219, or 30.3% of cleaned revenue.** The keyword mapping leaves 12.6% of revenue in `Other`; this is a practical portfolio taxonomy, not a source-system product hierarchy.

## 2. Geography and customer concentration

**The United Kingdom contributes 85.7% of cleaned revenue.** The largest identified customer represents 3.0%, while the top 10 represent 13.9%. This separates the market's geographic concentration from its customer-level concentration.

## 3. Seasonality

**2011-11 is the strongest month, with £1,457,212 from 2,751 orders.** Months where order count rose while revenue did not: 2010-02, 2010-05, 2011-02. That pattern is only a discount or mix signal; the dataset has no promotion field, so it cannot establish the cause.

## Scope and limitations

- Revenue is gross merchandise value (`Quantity × UnitPrice`) after removing cancellations and returns; it is not profit and excludes shipping or fee lines.
- Orders with missing customer IDs remain in revenue and order totals but not in customer concentration metrics.
- Category labels are reproducible keyword rules over free-text descriptions. They are directional and should not be treated as a company-maintained taxonomy.
- Online Retail II describes one UK-based non-store retailer from December 2009 to December 2011, so the findings do not generalize to e-commerce overall.
