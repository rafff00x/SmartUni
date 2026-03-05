"""SmartUni - University program recommender app (UI-focused version, logic unchanged)."""

import os

import streamlit as st

from config import BUDGETS, COUNTRIES, DATA_PATH, FIELDS, STUDY_LANGUAGES
from src.apply.steps import apply_steps
from src.data.loader import load_data
from src.filtering.filters import filter_and_rank
from src.gemini.parser import parse_user_desires

LOGO_URL = "PASTE_LOGO_IMAGE_URL_HERE"  # kept for compatibility but not used directly


def inject_css() -> None:
    """Inject global CSS for background, inputs, buttons, and cards."""
    st.markdown(
        """
        <style>
        /* App background gradient */
        .stApp {
            background: linear-gradient(135deg, #6082B6 0%, #B6D0E2 50%, #9fbdd5 100%);
            color: #0b1120;
            min-height: 100vh;
        }

        /* Headings and text */
        h1, h2, h3, h4, h5, h6,
        p, span, div, label {
            color: #f2f9ff;
        }

        /* Selectbox styling (inputs + dropdown) */
        div[data-baseweb="select"] > div {
            background-color: #7393B3 !important;
            color: #4682B4 !important;
            border-radius: 6px !important;
        }
        div[data-baseweb="select"] > div svg {
            fill: #0b1120 !important;
        }

        /* Dropdown list container */
        div[data-baseweb="popover"] div[role="listbox"] {
            background-color: #7393B3 !important;
            border-radius: 6px !important;
        }

        /* Dropdown options */
        div[data-baseweb="popover"] div[role="option"] {
            background-color: #7393B3 !important;
            color: #0b1120 !important;
        }
        div[data-baseweb="popover"] div[role="option"]:hover {
            background-color: #6885a3 !important; /* slightly darker hover */
        }
        div[data-baseweb="popover"] div[role="option"][aria-selected="true"] {
            background-color: #87a7c6 !important; /* slightly lighter selected */
            font-weight: 600;
        }

        /* Submit / primary buttons */
        div.stButton > button,
        button[kind="primary"],
        [data-testid="stFormSubmitButton"] button {
            background-color: #7393B3 !important;
            color: #0b1120 !important;
            border-radius: 999px !important;
            border: none !important;
            font-weight: 600;
            padding: 0.45rem 1.4rem !important;
            transition: background-color 0.15s ease-in-out;
        }
        div.stButton > button:hover,
        button[kind="primary"]:hover,
        [data-testid="stFormSubmitButton"] button:hover {
            background-color: #5E7FA0 !important;
        }

        /* Result cards */
        .smartuni-card {
            background-color: #6F8FAF;
            border-radius: 14px;
            padding: 1.1rem 1.2rem;
            margin-bottom: 0.9rem;
            box-shadow: 0 10px 24px rgba(15, 23, 42, 0.08);
            border: 1px solid rgba(148, 163, 184, 0.4);
        }
        .smartuni-card-header {
            display: flex;
            justify-content: space-between;
            align-items: flex-start;
            gap: 0.75rem;
            margin-bottom: 0.5rem;
        }
        .smartuni-card-title {
            font-size: 1.1rem;
            font-weight: 700;
        }
        .smartuni-card-subtitle {
            font-size: 0.9rem;
            opacity: 0.9;
        }
        .smartuni-card-field {
            font-size: 0.85rem;
            font-weight: 600;
            margin-top: 0.1rem;
        }
        .smartuni-card-score {
            font-size: 0.9rem;
            font-weight: 700;
            padding: 0.2rem 0.7rem;
            border-radius: 999px;
            background-color: #0F52BA;
            border: 1px solid rgba(148, 163, 184, 0.6);
        }
        .smartuni-badges {
            display: flex;
            flex-wrap: wrap;
            gap: 0.35rem;
            margin: 0.4rem 0 0.5rem 0;
        }
        .smartuni-badge {
            font-size: 0.75rem;
            padding: 0.18rem 0.55rem;
            border-radius: 999px;
            background-color: #e0ebff;
            color: #0b1120;
            border: 1px solid rgba(37, 99, 235, 0.3);
        }
        .smartuni-link-row {
            display: flex;
            flex-wrap: wrap;
            gap: 0.5rem;
            margin-top: 0.4rem;
        }
        .smartuni-link-btn {
            display: inline-block;
            padding: 0.3rem 0.9rem;
            border-radius: 999px;
            font-size: 0.82rem;
            font-weight: 600;
            text-decoration: none;
            border: 1px solid rgba(37, 99, 235, 0.35);
            color: #0b1120;
            background-color: #e6f0ff;
        }
        .smartuni-link-btn:hover {
            background-color: #d0e0ff;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def render_header(_: str) -> None:
    """Render the app header with local logo, title, and slogan."""
    logo_path = os.path.join("assets", "logo.png")

    hcol1, hcol2 = st.columns([1, 8], vertical_alignment="center")
    with hcol1:
        if os.path.exists(logo_path):
            st.image(logo_path, width=80)
    with hcol2:
        st.title("SmartUni")
        st.write("AI-powered university recommender to help you find matching Bachelor programs.")


def format_tuition(row) -> str:
    """Format tuition info for display."""
    cat = row.get("tuition_category", "") or "unknown"
    amt = row.get("tuition_amount", "")
    cur = row.get("tuition_currency", "")
    if str(amt).strip() != "":
        return f"{cat} ({amt} {cur})".strip()
    return cat


def render_result_card(row) -> None:
    """Render a single result as a styled card."""
    uni = row.get("university_name", "Unknown University")
    prog = row.get("program_name", "Unknown Program")
    score = row.get("score", 0)
    country = row.get("country", "")
    city = row.get("city", "")
    field = row.get("field", "")
    lang = row.get("language", "")
    tuition = format_tuition(row)
    system = row.get("application_system", "")
    deadline = row.get("deadline_month", "")
    link = row.get("apply_link", "")
    tier = (row.get("ranking_tier", "") or "").strip().upper() or "N/A"

    location = country or ""
    if city:
        location = f"{location} / {city}" if location else city

    st.markdown(
        f"""
        <div class="smartuni-card">
            <div class="smartuni-card-header">
                <div>
                    <div class="smartuni-card-title">{uni}</div>
                    <div class="smartuni-card-subtitle">{location}</div>
                    <div class="smartuni-card-field">{field}</div>
                </div>
                <div class="smartuni-card-score">Score: {score}</div>
            </div>
            <div class="smartuni-badges">
                <span class="smartuni-badge">Language: {lang or "unknown"}</span>
                <span class="smartuni-badge">Tuition: {tuition}</span>
                <span class="smartuni-badge">Tier: {tier}</span>
            </div>
        """,
        unsafe_allow_html=True,
    )

    st.write(f"**Application system:** {system or 'unknown'}")
    st.write(f"**Deadline:** {deadline or 'varies/unknown'}")

    st.markdown("**Why recommended**")
    for bullet in row.get("why") or []:
        st.write(f"- {bullet}")

    st.markdown("**How to apply**")
    for s in apply_steps(system):
        st.write(f"- {s}")

    link_buttons = ""
    if link and str(link).strip():
        link_buttons += f'<a class="smartuni-link-btn" href="{link}" target="_blank" rel="noopener noreferrer">Official website</a>'
    link_buttons += '<a class="smartuni-link-btn" href="#top">How to apply</a>'

    st.markdown(
        f'<div class="smartuni-link-row">{link_buttons}</div>',
        unsafe_allow_html=True,
    )

    if row.get("notes", "").strip():
        st.info(f"Notes: {row.get('notes','')}")

    st.markdown("</div>", unsafe_allow_html=True)


def _render_results(results):
    """Render filtered results as a stack of cards."""
    if results.empty:
        st.warning(
            "No matches found with these filters. Try one of these:\n"
            "- Set country to **Any**\n"
            "- Set language to **Any**\n"
            "- Increase budget (e.g., <=10000 or Any)\n"
            "- Try a different course\n"
        )
        return

    max_show = 15
    show_n = min(len(results), max_show)
    st.success(f"Found {len(results)} matches. Showing top {show_n}.")
    top = results.head(show_n)

    for _, row in top.iterrows():
        render_result_card(row)


def main():
    st.set_page_config(page_title="SmartUni", page_icon="🎓", layout="wide")
    inject_css()
    render_header(LOGO_URL)

    # Load data once
    try:
        df = load_data(DATA_PATH)
    except FileNotFoundError:
        st.error(f"CSV file not found: {DATA_PATH}. Put it in the same folder as app.py.")
        st.stop()
    except Exception as e:
        st.error(f"Failed to load dataset: {e}")
        st.stop()

    st.subheader("Search")

    form_tab, ai_tab = st.tabs(["Form (dropdowns)", "AI Search"])

    with ai_tab:
        user_desires = st.text_area(
            "Describe what you're looking for",
            placeholder=(
                "e.g., I want to study computer science in Germany, my budget is 5000 euros, "
                "I speak German. My GPA is 85%."
            ),
            height=120,
        )
        use_ai = st.button("🔍 Find similar programs (AI Search)")

        if use_ai and user_desires.strip():
            with st.spinner("AI is analyzing your preferences..."):
                parsed = parse_user_desires(user_desires.strip())

            if parsed is None:
                st.warning(
                    "AI parsing unavailable. Set GEMINI_API_KEY in your environment, "
                    "or use the Form (dropdowns) tab instead."
                )
            else:
                st.success(
                    f"Parsed: field={parsed.field}, country={parsed.country}, "
                    f"language={parsed.language}, budget={parsed.budget}"
                )
                gpa = parsed.gpa_percent if parsed.gpa_percent is not None else 85
                results = filter_and_rank(
                    df=df,
                    field=parsed.field,
                    country=parsed.country,
                    study_language=parsed.language,
                    budget=parsed.budget,
                    gpa_percent=gpa,
                )
                _render_results(results)
        elif use_ai:
            st.info("Please describe what you're looking for in the text area above.")

    with form_tab:
        col1, col2 = st.columns(2)

        with col1:
            preferred_country = st.selectbox("Preferred country:", COUNTRIES, index=0)
            preferred_language = st.selectbox(
                "Preferred language of study:", STUDY_LANGUAGES, index=0
            )
            gpa_percent = st.slider("GPA (percentage):", min_value=1, max_value=100, value=85)

        with col2:
            preferred_course = st.selectbox("Preferred course:", FIELDS, index=0)
            tuition_budget = st.selectbox("Tuition fee budget:", BUDGETS, index=0)

        submit = st.button("Submit ✅")

        if submit:
            results = filter_and_rank(
                df=df,
                field=preferred_course,
                country=preferred_country,
                study_language=preferred_language,
                budget=tuition_budget,
                gpa_percent=gpa_percent,
            )
            _render_results(results)


if __name__ == "__main__":
    main()
