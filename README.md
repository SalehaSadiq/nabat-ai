# NabatAI 🌱

Evidence-Based Plant Biotechnology & Crop Decision Support for Pakistan. NabatAI is a hackathon-ready Streamlit MVP built around a **two-round evidence workflow**: it first generates competing hypotheses and challenges them, then asks for the minimum useful evidence; after the user confirms extracted report values, it re-runs the assessment and can reverse its earlier conclusion.

## Features
- English, Urdu and Roman Urdu input
- Wheat, Tomato, Potato, Chilli and Citrus MVP
- Logical multi-agent architecture using one configurable multimodal LLM
- Offline/demo fallbacks when no API key is configured
- Skeptic Agent and Safety Agent
- Minimum useful test recommendations and “Don't Spend Yet” guidance
- PDF/image lab report extraction + mandatory human confirmation
- Before-vs-after evidence re-evaluation
- Minimum Cost / Best Value / Comprehensive pathways
- PKR budget optimization and “I can't afford this” flow
- CropCare timeline and financial schedule
- Static evidence library with non-fabrication fallback behavior
- Session-only Expert Mode
- JSON case export/import; no database required

## Run locally
1. Install Python 3.11+.
2. Open a terminal in this folder.
3. Create a virtual environment: `python -m venv .venv`
4. Activate it on Windows: `.venv\\Scripts\\activate`
5. Install dependencies: `pip install -r requirements.txt`
6. Optional AI mode: set `OPENAI_API_KEY` and optionally `OPENAI_MODEL`.
7. Optional Expert Mode: set `EXPERT_PASSWORD`.
8. Run: `streamlit run app.py`

Without an API key, the app remains runnable using deterministic hackathon demo logic. With an API key, logical agents use separate role prompts and structured JSON outputs.

## Streamlit Community Cloud
Push this folder to GitHub. In Streamlit Community Cloud, select `app.py` as the entrypoint and add secrets:

```toml
OPENAI_API_KEY = "your-key"
OPENAI_MODEL = "gpt-4o-mini"
EXPERT_PASSWORD = "choose-a-demo-password"
```

Never commit `.streamlit/secrets.toml`; it is ignored by `.gitignore`.

## Architecture
`pages/` contains the six-step UX. `agents/` contains separate logical agents and the orchestrator. `services/` wraps the LLM, report parsing, citations and static recommendations. `data/` is read-only JSON knowledge/demo content. `utils/` contains schemas, finance helpers, formatting and validation.

## Safety
NabatAI provides decision support, not guaranteed diagnosis. Critical agricultural and financial decisions should be confirmed with qualified local professionals. The app does not intentionally provide unsupported pesticide recipes, destructive crop actions, or exact fertilizer doses without adequate validated evidence. Static costs are explicitly demo estimates and must be verified locally.

## Demo scenarios
Use the dropdown on **New Case** to load: Chilli yellowing/poor growth (soil evidence + affordability), Tomato leaf curl/whitefly (viral hypothesis + safety gate), or Potato repeated disease (clean planting material + diagnostic/biotech relevance).

## Adding crops
Add a crop to `data/crops.json`, extend relevant static recommendations/references, and add crop-specific fallback rules only where useful. The LLM prompts are crop-agnostic.
