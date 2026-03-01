"""Parse user natural language desires into structured parameters using Gemini API."""

import json
import os
from dataclasses import dataclass
from typing import Optional, Tuple

from config import BUDGETS, COUNTRIES, FIELDS, STUDY_LANGUAGES

_DOTENV_LOADED = False


@dataclass
class ParsedPreferences:
    """Structured preferences extracted from user input."""

    field: str
    country: str
    language: str
    budget: str
    gpa_percent: Optional[int]
    raw_input: str


def _get_api_key() -> Optional[str]:
    """Get Gemini API key from environment."""
    global _DOTENV_LOADED
    if not _DOTENV_LOADED:
        try:
            from dotenv import load_dotenv

            load_dotenv()
        except Exception:
            pass
        _DOTENV_LOADED = True
    return os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY")


def _parse_gpa_percent(value: object) -> Optional[int]:
    """Coerce GPA percent to int 0-100 when possible."""
    if value is None:
        return None
    try:
        if isinstance(value, str):
            cleaned = value.strip()
            if not cleaned:
                return None
            if cleaned.endswith("%"):
                cleaned = cleaned[:-1].strip()
            value = cleaned
        num = float(value)
    except Exception:
        return None
    if num < 0 or num > 100:
        return None
    return int(round(num))


def parse_user_desires_with_error(
    user_input: str,
) -> Tuple[Optional[ParsedPreferences], Optional[str]]:
    """
    Use Gemini API to parse natural language into structured preferences.

    Args:
        user_input: Free-form text describing user's desires (e.g., "I want to
            study computer science in Germany, budget 5000 euros, I speak German").

    Returns:
        (ParsedPreferences, None) if successful, (None, error_message) otherwise.
    """
    api_key = _get_api_key()
    if not api_key:
        return None, "Missing GEMINI_API_KEY / GOOGLE_API_KEY."

    try:
        import google.generativeai as genai

        genai.configure(api_key=api_key)
        model = genai.GenerativeModel("gemini-2.5-flash")

        prompt = f"""You are a university recommender assistant. Parse the user's desires into structured preferences.

User input: "{user_input}"

Extract and return JSON only with these exact keys (no extra text):
- field: one of {json.dumps(FIELDS)}
- country: one of {json.dumps(COUNTRIES)}
- language: one of {json.dumps(STUDY_LANGUAGES)}
- budget: one of {json.dumps(BUDGETS)}
- gpa_percent: integer 0-100 if mentioned, else null

Rules:
- If user mentions a subject like "CS", "IT", "programming" -> field: "computer science"
- If user mentions "AI", "machine learning", "ML" -> field: "AI"
- If budget not mentioned -> "Any"
- If "free" or "no tuition" -> budget: "Free"
- If budget <= 5000 or "under 5k" -> budget: "<=5000"
- If budget <= 10000 or "under 10k" -> budget: "<=10000"
- If country not mentioned -> "Any"
- If language not mentioned -> "Any"
- If "UK", "England", "Britain" -> country: "UK"
- If "Deutschland" or "German" -> country: "Germany" (if country) or language: "German" (if language)
- gpa_percent: convert to 0-100 scale. If GPA 3.5/4 -> ~87, if 8.5/10 -> 85

Return ONLY valid JSON, no markdown code blocks."""

        response = model.generate_content(prompt)
        text = response.text.strip()
        # Remove markdown code blocks if present
        if text.startswith("```"):
            text = text.split("```")[1]
            if text.startswith("json"):
                text = text[4:]
        text = text.strip()

        data = json.loads(text)
        return (
            ParsedPreferences(
            field=data.get("field", "Any"),
            country=data.get("country", "Any"),
            language=data.get("language", "Any"),
            budget=data.get("budget", "Any"),
            gpa_percent=_parse_gpa_percent(data.get("gpa_percent")),
            raw_input=user_input,
            ),
            None,
        )
    except Exception as exc:
        return None, str(exc)


def parse_user_desires(user_input: str) -> Optional[ParsedPreferences]:
    """Compatibility wrapper returning only preferences."""
    prefs, _ = parse_user_desires_with_error(user_input)
    return prefs


