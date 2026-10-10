from src.metrics import category_performance, headline_metrics, monthly_performance


def _money(value: float) -> str:
    return f"£{value:,.0f}"


def build_summary(frame, source_label: str):
    headline = headline_metrics(frame)
    categories = category_performance(frame)
    monthly = monthly_performance(frame)

    leader = categories.iloc[0]
    other_rows = categories.loc[categories["Category"].eq("Other"), "revenue_share"]
    other_share = float(other_rows.iloc[0]) if len(other_rows) else 0.0
    peak = monthly.loc[monthly["revenue"].idxmax()]

    comparison = monthly.assign(
        order_change=monthly["orders"].diff(),
        revenue_change=monthly["revenue"].diff(),
    )
    discount_signal_months = comparison.loc[
        comparison["order_change"].gt(0) & comparison["revenue_change"].le(0), "month"
    ].tolist()
    signal_text = (
        ", ".join(discount_signal_months)
        if discount_signal_months
        else "No month in the cleaned series"
    )

    metrics = {
        **headline,
        "source_label": source_label,
        "leading_category": str(leader["Category"]),
        "leading_category_revenue": float(leader["revenue"]),
        "leading_category_share": float(leader["revenue_share"]),
        "other_category_share": other_share,
        "peak_month": str(peak["month"]),
        "peak_month_revenue": float(peak["revenue"]),
        "peak_month_orders": int(peak["orders"]),
        "discount_signal_months": discount_signal_months,
    }

    summary = f"""# Analysis summary

**Data source:** {source_label}

After excluding cancellations, returns, invalid prices or quantities, and non-merchandise charges, the analysis covers **{headline['rows']:,} line items**, **{headline['orders']:,} orders**, and **{headline['customers']:,} identified customers**. Cleaned merchandise revenue is **{_money(headline['total_revenue'])}**.

## 1. Product mix

**{leader['Category']} leads the category view at {_money(leader['revenue'])}, or {leader['revenue_share']:.1%} of cleaned revenue.** The keyword mapping leaves {other_share:.1%} of revenue in `Other`; this is a practical portfolio taxonomy, not a source-system product hierarchy.

## 2. Geography and customer concentration

**The United Kingdom contributes {headline['uk_revenue_share']:.1%} of cleaned revenue.** The largest identified customer represents {headline['top_customer_share']:.1%}, while the top 10 represent {headline['top_10_customer_share']:.1%}. This separates the market's geographic concentration from its customer-level concentration.

## 3. Seasonality

**{peak['month']} is the strongest month, with {_money(peak['revenue'])} from {int(peak['orders']):,} orders.** Months where order count rose while revenue did not: {signal_text}. That pattern is only a discount or mix signal; the dataset has no promotion field, so it cannot establish the cause.

## Scope and limitations

- Revenue is gross merchandise value (`Quantity × UnitPrice`) after removing cancellations and returns; it is not profit and excludes shipping or fee lines.
- Orders with missing customer IDs remain in revenue and order totals but not in customer concentration metrics.
- Category labels are reproducible keyword rules over free-text descriptions. They are directional and should not be treated as a company-maintained taxonomy.
- Online Retail II describes one UK-based non-store retailer from December 2009 to December 2011, so the findings do not generalize to e-commerce overall.
"""
    return summary, metrics
