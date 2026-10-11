from src.metrics import category_performance, headline_metrics, monthly_performance


def _money(value: float) -> str:
    return f"£{value:,.0f}"


def build_summary(frame, source_label: str):
    headline = headline_metrics(frame)
    categories = category_performance(frame)
    monthly = monthly_performance(frame)

    leader = categories.iloc[0]
    runner_up = categories.iloc[1] if len(categories) > 1 else None
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
    if discount_signal_months:
        signal_sentence = (
            "Orders rose without revenue growth in "
            + ", ".join(discount_signal_months)
            + "."
        )
    else:
        signal_sentence = "No month had more orders without revenue growth."
    runner_up_text = (
        f" {runner_up['Category']} follows at {_money(runner_up['revenue'])}."
        if runner_up is not None
        else ""
    )
    if source_label.startswith("REAL"):
        source_note = (
            "The final month, December 2011, ends on the 9th. "
            "These patterns come from one UK-based giftware retailer."
        )
    else:
        source_note = "This sample only checks that the analysis runs."

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

    summary = f"""# Sales analysis

Source: **{source_label}**

I kept {headline['rows']:,} merchandise lines from {headline['orders']:,} orders, worth {_money(headline['total_revenue'])}. There are {headline['customers']:,} identified customers. The cleaning removes cancellations, returns, non-positive prices and quantities, and non-merchandise charges.

## Products

{leader['Category']} brought in the most revenue: **{_money(leader['revenue'])} ({leader['revenue_share']:.1%})**.{runner_up_text} I assigned categories from product descriptions, and {other_share:.1%} of revenue remains in `Other`. These groups are useful for exploring the mix, but they are not an official product taxonomy.

## Customers and countries

The UK accounts for **{headline['uk_revenue_share']:.1%}** of revenue. The largest identified customer accounts for {headline['top_customer_share']:.1%}; the top ten together account for {headline['top_10_customer_share']:.1%}. Orders without a customer ID remain in the revenue total but cannot appear in customer rankings.

## Timing

Revenue peaks in **{peak['month']}**, at {_money(peak['revenue'])} from {int(peak['orders']):,} orders. {signal_sentence} Lower prices or a change in product mix could explain this, but the data has no promotion field. {source_note}

## What the numbers mean

Revenue is `Quantity × UnitPrice` on the retained lines, in pounds sterling. It is not profit. I would not generalize these patterns to other retailers.
"""
    return summary, metrics
