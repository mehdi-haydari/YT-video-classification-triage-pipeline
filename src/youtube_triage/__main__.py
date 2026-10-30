"""Summarize a labelled clip CSV with pandas."""

import argparse
from pathlib import Path

import pandas as pd


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("csv_path", type=Path, help="Path to a labelled clip CSV")
    args = parser.parse_args()

    try:
        clips = pd.read_csv(args.csv_path)
    except (OSError, UnicodeError, pd.errors.ParserError, pd.errors.EmptyDataError) as exc:
        parser.error(str(exc))

    print(f"Clips: {len(clips)}")
    print(f"Columns: {', '.join(clips.columns)}")
    if "ground_truth_label" in clips.columns:
        print("\nGround-truth labels:")
        print(clips["ground_truth_label"].value_counts(dropna=False).to_string())


if __name__ == "__main__":
    main()
