"""AI Learning Roadmap Generator
Streamlit UI + Google Gemini Flash model (via REST API).
"""

import os

import requests
import streamlit as st

DEFAULT_MODEL = "gemini-2.5-flash"
API_URL = "https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent"

LEVELS = ["Complete beginner", "Some programming experience", "Intermediate (know basic ML)", "Advanced"]
GOALS = [
    "Machine Learning Engineer",
    "Data Scientist",
    "Generative AI / LLM Developer",
    "Computer Vision Engineer",
    "NLP Engineer",
    "AI Researcher",
    "Use AI in my current job / business",
    "Just exploring AI",
]
STYLES = ["Video courses", "Books & articles", "Hands-on projects", "A mix of everything"]


def get_api_key():
    """Look for the API key in Streamlit secrets, then environment variables."""
    try:
        key = st.secrets.get("GEMINI_API_KEY", "")
    except Exception:  # no secrets.toml present
        key = ""
    return key or os.environ.get("GEMINI_API_KEY", "")


def build_prompt(level, goal, hours_per_week, months, background, style, extra):
    """Create the prompt sent to Gemini."""
    total_weeks = int(months) * 4
    return f"""You are an expert AI mentor. Create a clear, practical, personalised AI learning roadmap.

Learner profile:
- Current level: {level}
- Goal: {goal}
- Time available: {hours_per_week} hours per week for {months} month(s) (about {total_weeks} weeks)
- Background: {background.strip() or "Not provided"}
- Preferred learning style: {style}
- Extra notes: {extra.strip() or "None"}

Write the roadmap in Markdown with exactly these sections:
1. ## Overview - 3-4 sentences on the path and what the learner will be able to do at the end.
2. ## Prerequisites - skills to have or refresh first (skip if none needed).
3. ## Phase-by-Phase Roadmap - split the {total_weeks} weeks into phases. For each phase give: title, week range, topics, 2-3 recommended free or well-known resources (courses, books, docs), and one hands-on mini project.
4. ## Capstone Project - one portfolio-worthy project idea.
5. ## Tools & Libraries - the main tools to learn.
6. ## Weekly Routine - how to split the {hours_per_week} weekly hours.
7. ## Tips & Common Mistakes - 4-5 short bullet points.

Be realistic for the time available. Only recommend resources you are confident exist. Do not invent URLs."""


def generate_roadmap(api_key, model, prompt):
    """Call the Gemini REST API and return the generated text."""
    try:
        resp = requests.post(
            API_URL.format(model=model),
            headers={"x-goog-api-key": api_key, "Content-Type": "application/json"},
            json={
                "contents": [{"parts": [{"text": prompt}]}],
                "generationConfig": {"temperature": 0.7},
            },
            timeout=120,
        )
    except requests.exceptions.RequestException as exc:
        raise RuntimeError(f"Network error while contacting Gemini: {exc}") from exc

    try:
        data = resp.json()
    except ValueError:
        data = {}

    if resp.status_code != 200:
        message = data.get("error", {}).get("message") if isinstance(data, dict) else None
        raise RuntimeError(f"Gemini API error ({resp.status_code}): {message or resp.text[:200]}")

    parts = []
    for cand in data.get("candidates", []):
        parts = cand.get("content", {}).get("parts", [])
        if parts:
            break
    text = "".join(p.get("text", "") for p in parts).strip()
    if not text:
        reason = data.get("promptFeedback", {}).get("blockReason")
        extra = f" (blocked: {reason})" if reason else ""
        raise ValueError(f"The model returned an empty response{extra}. Try rephrasing your inputs.")
    return text


def main():
    st.set_page_config(page_title="AI Learning Roadmap", page_icon="🗺️", layout="centered")
    st.title("🗺️ AI Learning Roadmap Generator")
    st.caption("Tell us about yourself and get a personalised plan to learn AI, powered by Google Gemini.")

    api_key = get_api_key()
    with st.sidebar:
        st.header("⚙️ Settings")
        if not api_key:
            api_key = st.text_input("Gemini API key", type="password", help="Get a free key at https://aistudio.google.com/apikey")
        else:
            st.success("API key loaded")
        model = st.text_input("Gemini model", value=os.environ.get("GEMINI_MODEL", DEFAULT_MODEL))

    with st.form("roadmap_form"):
        level = st.selectbox("Your current level", LEVELS)
        goal = st.selectbox("Your goal", GOALS)
        col1, col2 = st.columns(2)
        hours = col1.slider("Hours per week", 1, 40, 8)
        months = col2.slider("Duration (months)", 1, 12, 6)
        style = st.selectbox("Preferred learning style", STYLES)
        background = st.text_area("Your background (optional)", placeholder="e.g. Final-year CS student, know Python and basic maths")
        extra = st.text_area("Anything else? (optional)", placeholder="e.g. I want to focus on building chatbots")
        submitted = st.form_submit_button("✨ Generate my roadmap")

    if submitted:
        if not api_key:
            st.error("Please enter your Gemini API key in the sidebar.")
            st.stop()
        if not model.strip():
            st.error("Please enter a Gemini model name in the sidebar.")
            st.stop()
        prompt = build_prompt(level, goal, hours, months, background, style, extra)
        try:
            with st.spinner("Building your roadmap..."):
                st.session_state["roadmap"] = generate_roadmap(api_key, model.strip(), prompt)
        except Exception as exc:
            st.session_state.pop("roadmap", None)
            st.error(f"Could not generate the roadmap: {exc}")

    if st.session_state.get("roadmap"):
        st.divider()
        st.markdown(st.session_state["roadmap"])
        st.download_button(
            "⬇️ Download as Markdown",
            data=st.session_state["roadmap"],
            file_name="ai_learning_roadmap.md",
            mime="text/markdown",
        )


if __name__ == "__main__":
    main()
