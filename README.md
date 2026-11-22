# 🗺️ AI Learning Roadmap Generator

A Streamlit app that creates a personalised roadmap for learning AI, powered by Google's Gemini Flash model.

## Features
- Choose your level, goal, weekly hours, duration and learning style
- Get a phase-by-phase plan with topics, resources, projects and a capstone idea
- Download the roadmap as a Markdown file

## Run locally
```bash
git clone https://github.com/<your-username>/ai-roadmap-app.git
cd ai-roadmap-app
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

Get a free API key at <https://aistudio.google.com/apikey>, then either:

- **Option A:** set an environment variable
  - macOS/Linux: `export GEMINI_API_KEY="your_key"`
  - Windows (PowerShell): `$env:GEMINI_API_KEY="your_key"`
- **Option B:** create `.streamlit/secrets.toml`:
  ```toml
  GEMINI_API_KEY = "your_key"
  ```
- **Option C:** paste the key into the sidebar when the app runs.

Start the app:
```bash
streamlit run app.py
```

## Deploy on Streamlit Community Cloud
1. Push this repo to GitHub (never commit your API key).
2. Go to <https://share.streamlit.io> and sign in with GitHub.
3. Click **Create app**, pick your repo, branch `main`, main file `app.py`.
4. Open **Advanced settings → Secrets** and add:
   ```toml
   GEMINI_API_KEY = "your_key"
   ```
5. Click **Deploy**.

## Changing the model
The default model is `gemini-2.5-flash`. You can change it in the sidebar, or set the `GEMINI_MODEL` environment variable. Check <https://ai.google.dev/gemini-api/docs/models> for current model names.

## Project files
| File | Purpose |
|------|---------|
| `app.py` | Streamlit app |
| `requirements.txt` | Python dependencies |
| `README.md` | Documentation |
