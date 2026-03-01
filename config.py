"""SmartUni configuration and constants."""

DATA_PATH = "smartuni_dataset_v4.csv"

FIELDS = [
    "Any",
    "computer science",
    "business",
    "cybersecurity",
    "data science",
    "AI",
    "engineering",
]

COUNTRIES = [
    "Any",
    "UK",
    "Germany",
    "Netherlands",
    "Sweden",
    "Finland",
    "Denmark",
    "France",
    "USA",
    "Canada"
]

STUDY_LANGUAGES = [
    "Any",
    "English",
    "German",
    "Swedish",
    "Finnish",
    "Danish",
    "French",
]

BUDGETS = ["Any", "Free", "<=5000", "<=10000"]

EXPECTED_COLUMNS = [
    "university_name",
    "country",
    "city",
    "program_name",
    "degree_level",
    "field",
    "language",
    "tuition_category",
    "tuition_amount",
    "tuition_currency",
    "gpa_min",
    "application_system",
    "deadline_month",
    "apply_link",
    "ranking_tier",
    "notes",
]
