from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter, PercentFormatter
import pandas as pd

from src.metrics import category_performance, customer_performance, monthly_performance


BLUE = "#244b74"
ORANGE = "#d97732"


def _save(fig, path: Path):
    fig.tight_layout()
    fig.savefig(path, dpi=180, bbox_inches="tight", facecolor="white")
    plt.close(fig)


def create_charts(frame: pd.DataFrame, output_dir: str | Path):
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    currency = FuncFormatter(lambda value, _: f"£{value / 1_000_000:.1f}m")
    paths = []

    categories = category_performance(frame).sort_values("revenue")
    fig, axis = plt.subplots(figsize=(9, 5.4))
    colors = [ORANGE if name == "Other" else BLUE for name in categories["Category"]]
    axis.barh(categories["Category"], categories["revenue"], color=colors)
    axis.xaxis.set_major_formatter(currency)
    axis.set_title("Revenue by product category", loc="left", fontweight="bold")
    axis.set_xlabel("Cleaned merchandise revenue")
    axis.spines[["top", "right"]].set_visible(False)
    path = output_dir / "category_revenue.png"
    _save(fig, path)
    paths.append(path)

    customers = customer_performance(frame)
    cumulative = customers["revenue"].cumsum() / frame["Revenue"].sum()
    fig, axis = plt.subplots(figsize=(9, 5.4))
    axis.plot(range(1, len(cumulative) + 1), cumulative, color=BLUE, linewidth=2)
    axis.axhline(0.8, color=ORANGE, linestyle="--", linewidth=1.5, label="80% of revenue")
    axis.yaxis.set_major_formatter(PercentFormatter(1.0))
    axis.set_title("Customer revenue concentration", loc="left", fontweight="bold")
    axis.set_xlabel("Customers ranked by revenue")
    axis.set_ylabel("Cumulative share of all cleaned revenue")
    axis.legend(frameon=False)
    axis.spines[["top", "right"]].set_visible(False)
    path = output_dir / "customer_concentration.png"
    _save(fig, path)
    paths.append(path)

    monthly = monthly_performance(frame)
    x = range(len(monthly))
    fig, revenue_axis = plt.subplots(figsize=(10, 5.4))
    order_axis = revenue_axis.twinx()
    revenue_axis.bar(x, monthly["revenue"], color=BLUE, alpha=0.88, label="Revenue")
    order_axis.plot(x, monthly["orders"], color=ORANGE, marker="o", linewidth=1.8, label="Orders")
    revenue_axis.set_xticks(list(x)[::2], monthly["month"].iloc[::2], rotation=45, ha="right")
    revenue_axis.yaxis.set_major_formatter(currency)
    revenue_axis.set_ylabel("Revenue")
    order_axis.set_ylabel("Distinct orders")
    revenue_axis.set_title("Monthly revenue and order volume", loc="left", fontweight="bold")
    revenue_axis.spines["top"].set_visible(False)
    order_axis.spines["top"].set_visible(False)
    path = output_dir / "monthly_trends.png"
    _save(fig, path)
    paths.append(path)
    return paths
