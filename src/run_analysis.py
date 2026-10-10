import argparse
import json
from pathlib import Path

from src.data_loader import load_transactions, synthetic_transactions
from src.metrics import add_categories
from src.plots import create_charts
from src.reporting import build_summary
from src.storage import write_analysis_database


def run_pipeline(data_path: Path, allow_synthetic: bool = False):
    if data_path.exists():
        frame = load_transactions(data_path)
        source_label = "REAL - UCI Online Retail II"
    elif allow_synthetic:
        frame = synthetic_transactions()
        source_label = "SYNTHETIC - smoke test only, not findings"
    else:
        raise FileNotFoundError(
            f"Missing {data_path}. Follow data/raw/README.md, or use --allow-synthetic for a smoke test."
        )

    frame = add_categories(frame)
    summary, metrics = build_summary(frame, source_label)
    reports = Path("reports")
    reports.mkdir(exist_ok=True)
    (reports / "figures").mkdir(exist_ok=True)
    (reports / "SUMMARY.md").write_text(summary, encoding="utf-8")
    (reports / "metrics.json").write_text(
        json.dumps(metrics, indent=2), encoding="utf-8"
    )
    write_analysis_database(frame, "data/processed/ecommerce.db")
    chart_paths = create_charts(frame, reports / "figures")
    print(
        f"Analyzed {metrics['rows']:,} cleaned rows from {source_label}; "
        f"wrote {len(chart_paths)} charts and the SQLite analysis store."
    )


def main():
    parser = argparse.ArgumentParser(description="Run the e-commerce analysis pipeline.")
    parser.add_argument("--data", type=Path, default=Path("data/raw/online_retail_II.xlsx"))
    parser.add_argument("--allow-synthetic", action="store_true")
    args = parser.parse_args()
    run_pipeline(args.data, args.allow_synthetic)


if __name__ == "__main__":
    main()
