"""Scoring logic for university program recommendations."""

from typing import List, Tuple

import pandas as pd

from src.data.loader import parse_float


def tier_bonus(tier: str) -> int:
    t = (tier or "").strip().upper()
    if t == "A":
        return 15
    if t == "B":
        return 10
    if t == "C":
        return 5
    return 0


def score_row(
    row: pd.Series, budget: str, gpa_percent: int
) -> Tuple[int, List[str]]:
    why: List[str] = []
    score = 60
    why.append(f"✅ Field matches: {row.get('field','')}")

    if budget == "Any":
        score += 15
        why.append("✅ Budget: no limit (Any)")
    else:
        score += 20
        cat = row.get("tuition_category", "") or "unknown"
        if (
            cat.strip().lower() == "high"
            and budget in {"Free", "<=5000", "<=10000"}
        ):
            why.append(f"⚠️ Budget may be tight: {budget} (dataset category: {cat})")
        else:
            why.append(f"✅ Budget fits: {budget} (category: {cat})")

    tb = tier_bonus(row.get("ranking_tier", ""))
    score += tb
    if row.get("ranking_tier", "").strip():
        why.append(
            f"⭐ Ranking tier bonus: {row.get('ranking_tier','').strip().upper()}"
        )
    else:
        why.append("⭐ Ranking tier bonus: neutral")

    user_gpa_10 = gpa_percent / 10.0
    gpa_min = parse_float(row.get("gpa_min", ""))
    if gpa_min is not None:
        if user_gpa_10 >= gpa_min:
            score += 10
            why.append(
                f"✅ GPA looks sufficient (you: ~{user_gpa_10:.1f}/10, min: {gpa_min}/10)"
            )
        else:
            score -= 10
            why.append(
                f"⚠️ GPA may be below min (you: ~{user_gpa_10:.1f}/10, min: {gpa_min}/10)"
            )
    else:
        why.append("ℹ️ GPA min not provided in dataset")

    score = max(0, min(100, score))
    return score, why
