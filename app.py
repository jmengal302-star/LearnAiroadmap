import streamlit as st
from google import genai

st.set_page_config(
    page_title="AI Learning Roadmap Generator",
    page_icon="🗺️",
    layout="wide",
)

st.title("🗺️ AI Learning Roadmap Generator")
st.write(
    "Enter what you want to learn in AI, your current level, and your weekly study time "
    "to get a structured, step-by-step learning roadmap powered by Gemini Flash."
)

# Read API key from Streamlit secrets first, or allow sidebar entry locally
api_key = ""
try:
    api_key = st.secrets.get("GEMINI_API_KEY", "")
except Exception:
    api_key = ""

with st.sidebar:
    st.header("Configuration")
    if not api_key:
        api_key = st.text_input(
            "Gemini API Key",
            type="password",
            help="Get a key from Google AI Studio (aistudio.google.com).",
        )
    else:
        st.success("API key loaded from Streamlit Secrets.")

    model_name = st.selectbox(
        "Gemini Flash Model",
        options=["gemini-3.8-flash", "gemini-3.5-flash-lite"],
        index=0,
    )

col1, col2, col3 = st.columns(3)
with col1:
    goal_topic = st.text_input(
        "Target AI Topic / Track",
        placeholder="e.g., Machine Learning, LLMs & RAG, Computer Vision",
    )
with col2:
    current_level = st.selectbox(
        "Current Experience Level",
        options=["Beginner", "Intermediate (Know Python basics)", "Advanced"],
    )
with col3:
    timeframe = st.selectbox(
        "Study Duration",
        options=["4 Weeks", "8 Weeks", "12 Weeks (3 Months)", "6 Months"],
        index=2,
    )

weekly_hours = st.slider(
    "Hours Available Per Week",
    min_value=2,
    max_value=30,
    value=8,
    step=1,
)

prior_skills = st.text_area(
    "Current Background / Tools You Already Know (Optional)",
    height=90,
    placeholder="e.g., Basic Python, calculus, statistics, Git, no prior ML experience",
)

if st.button("Generate Roadmap", type="primary"):
    if not api_key or not api_key.strip():
        st.error("Please provide a Gemini API key in Streamlit Secrets or the sidebar.")
    elif not goal_topic or not goal_topic.strip():
        st.error("Please enter a target AI topic or track.")
    else:
        prompt = f"""
You are a practical AI curriculum mentor. Create a clear, realistic, and actionable learning roadmap.

Learner Profile:
- Target Topic / Track: {goal_topic.strip()}
- Current Level: {current_level}
- Duration: {timeframe}
- Weekly Time Commitment: {weekly_hours} hours/week
- Prior Background: {prior_skills.strip() if prior_skills and prior_skills.strip() else "Not specified"}

Structure the response using clean Markdown with:
1. **Overview & Prerequisites**: Brief summary of what the learner will achieve and key foundations needed.
2. **Phase-by-Phase Roadmap**: Broken down across {timeframe} (~{weekly_hours} hrs/week), with concrete topics, concepts, and estimated time per phase.
3. **Hands-On Projects**: 2 to 3 practical mini-projects or milestones to build along the way.
4. **Study & Practice Tips**: How to avoid tutorial trap, test understanding, and track progress.
"""
        try:
            with st.spinner("Building your personalized AI roadmap..."):
                client = genai.Client(api_key=api_key.strip())
                response = client.models.generate_content(
                    model=model_name,
                    contents=prompt,
                )

            roadmap_text = response.text or ""
            if not roadmap_text.strip():
                st.warning("No roadmap text was returned. Please try again.")
            else:
                st.markdown("## Your AI Learning Roadmap")
                st.markdown(roadmap_text)

                safe_filename = (
                    "".join(c if c.isalnum() or c in ("-", "_") else "_" for c in goal_topic.strip().lower())
                    or "ai_roadmap"
                )
                st.download_button(
                    label="Download Roadmap (.md)",
                    data=roadmap_text,
                    file_name=f"{safe_filename}_roadmap.md",
                    mime="text/markdown",
                )
        except Exception as exc:
            st.error(f"Could not generate roadmap: {exc}")
