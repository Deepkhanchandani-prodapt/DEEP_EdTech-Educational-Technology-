# Presentation Deck

The editable slide deck is [presentation.pptx](../deliverables/presentation.pptx); the matching [PDF](../deliverables/presentation.pdf) is included for submission. The 10-slide sequence maps to the requested presentation criteria.

## Slide outline

1. **Title** — Eduvantage AI: Student Success Intelligence.
2. **Problem statement and business need** — Academic and engagement evidence is spread across records; advisors need a reviewable way to prioritize follow-up.
3. **Solution overview** — Cohort dashboards, filtered profiles, historical search, recommendations, intervention plans, feedback, and export.
4. **Architecture** — OULAD ingestion, React/Vite, FastAPI, SQL persistence, analysis services, and optional NVIDIA NIM; explain that there is no pretrained embedding service or vector database.
5. **Data flow** — CSV source → streaming joins and aggregation → one student-course-presentation profile → filtered retrieval/analysis → advisor interface.
6. **Technology stack** — Python/FastAPI, React/Vite, SQLAlchemy, SQLite/PostgreSQL, scikit-learn, optional NVIDIA NIM; local TF-IDF/LSA representation.
7. **Agent workflow** — Performance analyst → risk assessor → intervention recommender, with evidence passed through the orchestrator and human review at the end.
8. **Demo** — Sign in, filter/prioritize a cohort, inspect a profile and similar cases, ask the assistant, save/edit an intervention, view feedback/export. Use the React site for the full interface or the optional Streamlit client for a quick API-backed walkthrough.
9. **Evaluation results** — Retrieval metrics and limitations; DeepEval results are pending and should not be represented as completed.
10. **Challenges and learnings** — Local retrieval trade-off, weak retrieval labels, model validation limits, privacy oversight, and next evaluation steps.

## Speaker notes for the demo

Use anonymized/synthetic records unless the demonstration environment is institutionally approved. State that the risk score is a heuristic indicator, not a calibrated probability. Explain that the retrieval benchmark's same-course relevance label is weak and keyword-only currently scores higher than hybrid. Do not claim DeepEval results that have not been produced. The full website is React/Vite; root `frontend.py` also provides the requested Streamlit demo client.
