"""SmartUni - University program recommender app."""

import streamlit as st

from config import BUDGETS, COUNTRIES, DATA_PATH, FIELDS, STUDY_LANGUAGES
from apply.steps import apply_steps
from data.loader import load_data
from filtering.filters import filter_and_rank
from gemini.parser import parse_user_desires_with_error


def format_tuition(row) -> str:
    """Format tuition info for display."""
    cat = row.get("tuition_category", "") or "unknown"
    amt = row.get("tuition_amount", "")
    cur = row.get("tuition_currency", "")
    if str(amt).strip() != "":
        return f"{cat} ({amt} {cur})".strip()
    return cat


def main():
    st.set_page_config(page_title="SmartUni", page_icon="🎓", layout="wide")

    st.markdown(
        """
        <style>
          .center-title {text-align: center; margin-top: 30px;}
          .center-sub {text-align: center; font-size: 18px; opacity: 0.85; margin-bottom: 50px;}
          .block {max-width: 900px; margin: 0 auto;}
          .small {opacity: 0.85; font-size: 14px;}
        </style>
        """,
        unsafe_allow_html=True,
    )

    st.markdown('<h1 class="center-title">SmartUni</h1>', unsafe_allow_html=True)
    st.markdown(
        '<div class="center-sub">SmartUni will help you choose easily the universities that match the best for you!</div>',
        unsafe_allow_html=True,
    )

    st.markdown('<div class="block">', unsafe_allow_html=True)

    try:
        df = load_data(DATA_PATH)
    except FileNotFoundError:
        st.error(f"CSV file not found: {DATA_PATH}. Put it in the same folder as app.py.")
        st.stop()
    except Exception as e:
        st.error(f"Failed to load dataset: {e}")
        st.stop()

    st.subheader("Find your best matches")

    # Input mode: form or AI
    input_mode = st.radio(
        "How would you like to search?",
        ["📝 Form (dropdowns)", "🤖 AI (describe in your own words)"],
        horizontal=True,
    )

    if input_mode == "🤖 AI (describe in your own words)":
        user_desires = st.text_area(
            "Describe what you're looking for",
            placeholder="e.g., I want to study computer science in Germany, my budget is 5000 euros, I speak German. My GPA is 85%.",
            height=100,
        )
        use_ai = st.button("🔍 Find similar programs", type="primary", use_container_width=True)

        if use_ai and user_desires.strip():
            with st.spinner("AI is analyzing your preferences..."):
                parsed, parse_error = parse_user_desires_with_error(
                    user_desires.strip()
                )

            if parsed is None:
                message = (
                    "AI parsing unavailable. Set GEMINI_API_KEY in your environment, "
                    "or use the Form mode instead."
                )
                if parse_error:
                    message = f"{message} Details: {parse_error}"
                st.warning(message)
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
    else:
        col1, col2 = st.columns(2)

        with col1:
            preferred_country = st.selectbox("Preferred country:", COUNTRIES, index=0)
            preferred_language = st.selectbox(
                "Preferred language of study:", STUDY_LANGUAGES, index=0
            )
            gpa_percent = st.slider(
                "GPA (percentage):", min_value=0, max_value=100, value=85
            )

        with col2:
            preferred_course = st.selectbox("Preferred course:", FIELDS, index=0)
            tuition_budget = st.selectbox("Tuition fee budget:", BUDGETS, index=0)

        submit = st.button("Submit ✅", use_container_width=True)

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

    st.markdown("</div>", unsafe_allow_html=True)


def _render_results(results):
    """Render filtered results as expandable cards."""
    if results.empty:
        st.warning(
            "No matches found with these filters. Try one of these:\n"
            "- Set country to **Any**\n"
            "- Set language to **Any**\n"
            "- Increase budget (e.g., <=10000 or Any)\n"
            "- Try a different course\n"
        )
    else:
        max_show = 15
        show_n = min(len(results), max_show)
        st.success(f"Found {len(results)} matches. Showing top {show_n}.")
        top = results.head(show_n)

        for _, row in top.iterrows():
            uni = row.get("university_name", "Unknown University")
            prog = row.get("program_name", "Unknown Program")
            score = row.get("score", 0)

            with st.expander(f"{uni} — {prog}  (Score: {score})"):
                country = row.get("country", "")
                city = row.get("city", "")
                lang = row.get("language", "")
                tuition = format_tuition(row)
                system = row.get("application_system", "")
                deadline = row.get("deadline_month", "")
                link = row.get("apply_link", "")

                st.write(f"**Location:** {country}{' / ' + city if city else ''}")
                st.write(f"**Language:** {lang if lang else 'unknown'}")
                st.write(f"**Tuition:** {tuition}")
                st.write(f"**Application system:** {system if system else 'unknown'}")
                st.write(f"**Deadline:** {deadline if deadline else 'varies/unknown'}")

                if link.strip():
                    st.markdown(f"🔗 Official page: {link}")
                else:
                    st.caption("No official link in dataset for this row.")

                st.markdown("### Why recommended")
                for bullet in row.get("why") or []:
                    st.write(f"- {bullet}")

                st.markdown("### How to apply")
                for s in apply_steps(system):
                    st.write(f"- {s}")

                if row.get("notes", "").strip():
                    st.markdown(
                        f"<div class='small'>Notes: {row.get('notes','')}</div>",
                        unsafe_allow_html=True,
                    )


if __name__ == "__main__":
    main()
