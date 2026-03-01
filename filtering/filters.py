"""Filtering logic for university programs."""

from typing import Optional

import pandas as pd

from data.loader import parse_float
from scoring.scorer import score_row


def budget_allowed_categories(budget: str) -> Optional[set]:
    """
    Return allowed tuition categories for a given budget selection.

    Mapping:
      - Free: free, low
      - <=5000: free, low
      - <=10000: free, low, medium
      - Any: no filtering (returns None)
    """
    budget = (budget or "").strip()
    if budget == "Free":
        return {"free", "low"}
    if budget == "<=5000":
        return {"free", "low"}
    if budget == "<=10000":
        return {"free", "low", "medium"}
    return None


def language_matches(cell: str, preferred_lang: str) -> bool:
    """Check if preferred language is contained in cell (case-insensitive)."""
    if preferred_lang == "Any":
        return True
    return preferred_lang.lower() in (cell or "").lower()


def filter_and_rank(
    df: pd.DataFrame,
    field: str,
    country: str,
    study_language: str,
    budget: str,
    gpa_percent: int,
) -> pd.DataFrame:
    """
    Filter dataframe by criteria and rank by score.

    Args:
        df: Input dataframe.
        field: Preferred field (or "Any").
        country: Preferred country (or "Any").
        study_language: Preferred language (or "Any").
        budget: Budget category (or "Any").
        gpa_percent: User GPA as percentage (0-100).

    Returns:
        Filtered and ranked dataframe with score and why columns.
    """
    work = df.copy()

    # Bachelor only if present
    if "degree_level" in work.columns and work["degree_level"].str.strip().ne("").any():
        work = work[work["degree_level"].str.lower().eq("bachelor")]

    # Field filter (case-insensitive)
    if field != "Any":
        field_l = field.lower()
        if field == "AI":
            field_l = "ai"
        work = work[work["_field_l"].eq(field_l)]

    # Country filter
    if country != "Any":
        work = work[work["_country_l"].eq(country.lower())]

    # Language filter
    if study_language != "Any":
        work = work[work["language"].apply(lambda x: language_matches(x, study_language))]

    # Budget filter
    if budget != "Any":
        budget_num = None
        if budget == "Free":
            budget_num = 0.0
        elif budget == "<=5000":
            budget_num = 5000.0
        elif budget == "<=10000":
            budget_num = 10000.0

        amt_series = (
            work["tuition_amount"].apply(parse_float)
            if "tuition_amount" in work.columns
            else None
        )
        if budget_num is not None and amt_series is not None and amt_series.notna().any():
            mask = amt_series.isna() | (amt_series <= budget_num)
            work = work[mask]
        else:
            allowed = budget_allowed_categories(budget)
            if allowed is not None:
                work = work[work["_tuition_cat_l"].isin(allowed)]

    # Score + why
    scores = []
    whys = []
    for _, row in work.iterrows():
        sc, why = score_row(row, budget, gpa_percent)
        scores.append(sc)
        whys.append(why)

    work = work.assign(score=scores, why=whys)
    work = work.sort_values(["score"], ascending=[False])

    return work
