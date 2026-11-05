"""Clean the raw Superstore file and save an analysis-ready CSV."""

from __future__ import annotations

import re
from pathlib import Path

import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[1]
RAW_FILE = PROJECT_ROOT / "data" / "raw" / "Superstore.csv"
CLEAN_FILE = PROJECT_ROOT / "data" / "processed" / "superstore_cleaned.csv"


def standardize_column_name(name: str) -> str:
    """Convert a source column label into lowercase_with_underscores."""
    if name.strip() == "记录数":
        name = "record_count"

    name = name.strip().lower()
    name = re.sub(r"[\s\-/]+", "_", name)
    return re.sub(r"[^a-z0-9_]", "", name).strip("_")


def clean_data(
    input_path: Path = RAW_FILE, output_path: Path = CLEAN_FILE
) -> pd.DataFrame:
    """Clean one Superstore CSV and return the rows saved to ``output_path``."""
    try:
        df = pd.read_csv(input_path, encoding="utf-8")
    except UnicodeDecodeError:
        df = pd.read_csv(input_path, encoding="latin-1")

    rows_before = len(df)
    original_columns = list(df.columns)
    df.columns = [standardize_column_name(column) for column in df.columns]

    if len(set(df.columns)) != len(df.columns):
        raise ValueError("Column-name standardization produced duplicate columns.")

    duplicate_count = int(df.duplicated().sum())
    df = df.drop_duplicates().copy()

    for column in ("order_date", "ship_date"):
        if column in df.columns:
            df[column] = pd.to_datetime(df[column], errors="coerce")

    for column in ("sales", "profit", "discount", "quantity"):
        if column in df.columns:
            df[column] = pd.to_numeric(df[column], errors="coerce")

    required_columns = {"order_date", "sales", "profit"}
    missing_columns = required_columns.difference(df.columns)
    if missing_columns:
        readable = ", ".join(sorted(missing_columns))
        raise ValueError(
            f"Missing required columns after standardization: {readable}. "
            f"Source columns were: {original_columns}"
        )

    text_columns = df.select_dtypes(include=["object", "string"]).columns
    for column in text_columns:
        df[column] = df[column].replace(r"^\s*$", pd.NA, regex=True)

    missing_before_handling = int(df.isna().sum().sum())
    missing_required_values = int(df[list(required_columns)].isna().sum().sum())
    rows_with_missing_required = int(df[list(required_columns)].isna().any(axis=1).sum())
    df = df.dropna(subset=list(required_columns)).copy()

    text_columns = df.select_dtypes(include=["object", "string"]).columns
    missing_text_values = int(df[text_columns].isna().sum().sum())
    if len(text_columns):
        df[text_columns] = df[text_columns].fillna("Unknown")

    df["order_year"] = df["order_date"].dt.year.astype("int64")
    df["order_month"] = df["order_date"].dt.month.astype("int64")
    df["order_month_name"] = df["order_date"].dt.month_name()
    df["profit_margin"] = df["profit"].div(df["sales"].where(df["sales"] != 0))

    if "ship_date" in df.columns:
        df["shipping_days"] = (df["ship_date"] - df["order_date"]).dt.days
    else:
        df["shipping_days"] = pd.NA

    output_path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(output_path, index=False)

    missing_values_fixed = missing_text_values + missing_required_values
    print("Cleaning summary")
    print(f"  Rows before cleaning: {rows_before:,}")
    print(f"  Rows after cleaning:  {len(df):,}")
    print(f"  Duplicate rows removed: {duplicate_count:,}")
    print(f"  Missing values filled or removed: {missing_values_fixed:,}")
    print(f"  Missing values before handling: {missing_before_handling:,}")
    print(
        "  Undefined profit margins (zero sales): "
        f"{int((df['sales'] == 0).sum()):,}"
    )
    print(f"  Output: {output_path}")

    return df


if __name__ == "__main__":
    clean_data()
