"""Download the public Global Superstore file and save it as a CSV."""

from pathlib import Path

import kagglehub
import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[1]
RAW_FILE = PROJECT_ROOT / "data" / "raw" / "Superstore.csv"
KAGGLE_DATASET = "anandaramg/global-superstore"
SOURCE_FILENAME = "Global Superstore.txt"


def download_data() -> Path:
    """Fetch the Kaggle dataset and convert its tab-separated source to CSV."""
    dataset_folder = Path(kagglehub.dataset_download(KAGGLE_DATASET))
    source_file = dataset_folder / SOURCE_FILENAME
    if not source_file.exists():
        raise FileNotFoundError(
            f"Expected {SOURCE_FILENAME!r} in the downloaded Kaggle dataset at "
            f"{dataset_folder}."
        )

    data = pd.read_csv(source_file, sep="\t", encoding="utf-8")
    RAW_FILE.parent.mkdir(parents=True, exist_ok=True)
    data.to_csv(RAW_FILE, index=False, encoding="utf-8")

    print(f"Downloaded dataset: {KAGGLE_DATASET}")
    print(f"Saved source CSV: {RAW_FILE}")
    print(f"Shape: {data.shape}")
    safe_columns = [
        column.encode("unicode_escape").decode("ascii") for column in data.columns
    ]
    print(f"Columns: {safe_columns}")
    return RAW_FILE


if __name__ == "__main__":
    download_data()
