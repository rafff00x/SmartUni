"""Parse user natural language desires into structured parameters using Gemini API."""

import json
import os
from dataclasses import dataclass
from typing import Optional

from config import BUDGETS, COUNTRIES, FIELDS, STUDY_LANGUAGES

try:
    from dotenv import load_dotenv

    load_dotenv()
except ModuleNotFoundError:  # pragma: no cover
    pass


@dataclass
class ParsedPreferences:
    field: str
    country: str
    language: str
    budget: str
    gpa_percent: Optional[int]
    raw_input: str


def _get_api_key() -> Optional[str]:
    return os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY")


def parse_user_desires(user_input: str) -> Optional[ParsedPreferences]:
    api_key = _get_api_key()
    if not api_key:
        return None

    try:
        from google import genai

        client = genai.Client(api_key=api_key)

        prompt = f"""
You are a university recommender assistant.

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

Return ONLY valid JSON. No markdown. No explanations.
"""

        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt,
        )

        text = response.text.strip()

        if text.startswith("```"):
            parts = text.split("```")
            if len(parts) > 1:
                text = parts[1]
                if text.startswith("json"):
                    text = text[4:]
        text = text.strip()

        data = json.loads(text)

        return ParsedPreferences(
            field=data.get("field", "Any"),
            country=data.get("country", "Any"),
            language=data.get("language", "Any"),
            budget=data.get("budget", "Any"),
            gpa_percent=data.get("gpa_percent"),
            raw_input=user_input,
        )

    except Exception as e:
        print("Gemini parsing error:", e)
        return None