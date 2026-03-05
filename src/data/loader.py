"""Data loading and preprocessing."""

from typing import Optional

import pandas as pd

from config import EXPECTED_COLUMNS


def safe_str(x) -> str:
    """Convert value to string, handling NaN."""
    if pd.isna(x):
        return ""
    return str(x).strip()


def normalize_lower(x: str) -> str:
    """Normalize string to lowercase."""
    return safe_str(x).lower()


def parse_float(x) -> Optional[float]:
    """Parse value to float, return None on failure."""
    try:
        if x is None or (isinstance(x, str) and x.strip() == ""):
            return None
        return float(x)
    except Exception:
        return None


def load_data(path: str) -> pd.DataFrame:
    """
    Load CSV dataset with normalization.

    Args:
        path: Path to CSV file.

    Returns:
        DataFrame with trimmed strings and normalized columns for matching.

    Raises:
        FileNotFoundError: If file does not exist.
    """
    df = pd.read_csv(path)

    for col in EXPECTED_COLUMNS:
        if col not in df.columns:
            df[col] = ""

    for col in EXPECTED_COLUMNS:
        df[col] = df[col].apply(safe_str)

    df["_country_l"] = df["country"].apply(normalize_lower)
    df["_field_l"] = df["field"].apply(normalize_lower)
    df["_lang_l"] = df["language"].apply(normalize_lower)
    df["_tuition_cat_l"] = df["tuition_category"].apply(normalize_lower)
    df["_tier_l"] = df["ranking_tier"].apply(normalize_lower)

    return df
