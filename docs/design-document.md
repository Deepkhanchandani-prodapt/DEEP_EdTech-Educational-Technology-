# Eduvantage AI — Design Document

**Version:** 1.1  
**Date:** 6 October 2026  
**Product:** Advisor-facing student success intelligence prototype

## 1. Problem statement and business need

Advisors work across assessment, registration, and learning-platform records to identify students who may benefit from timely support. Reviewing these separate data sources makes it difficult to prioritize a large cohort, understand the evidence behind a concern, or locate historically similar student-course profiles.

Eduvantage AI brings these signals into one review workflow. Its business objective is to help advisors prioritize follow-up, interpret academic and engagement evidence, and record support plans. Risk scores are screening indicators; the system does not make student decisions or replace advisor judgment.

## 2. Solution overview and users

The browser application provides cohort dashboards, six metadata filters, student profiles and trends, historical similarity search, grounded cohort/student chat, support recommendations, intervention-plan CRUD, feedback, and CSV export. Advisors review evidence and own all interventions. Administrators manage records and audit activity. Analysts inspect trends, model estimates, and evaluation evidence.

The supplied OULAD data is imported to a local SQL database. A clean database can display clearly labeled synthetic demonstration records. Core analysis is deterministic and runs locally; NVIDIA NIM prose generation and LLM-as-Judge are optional server-side capabilities.

## 3. Architecture design

The deployed request path is **React/Vite UI → FastAPI API → analysis and retrieval services → SQLAlchemy persistence**. OULAD CSVs flow through streaming preprocessing and aggregation into student-course-presentation profiles. The architecture diagram is provided as `../deliverables/architecture-diagram.pdf` and `.jpg`.

The requested RAG reference chain is **Dataset → Preprocessing → Profile chunking → Embedding representation → Vector database → Retriever → RAG/LLM → Agents → API → UI**. A student profile is the retrieval unit. Local HashingVectorizer vectors are persisted and searched in ChromaDB; SQL-loaded structured features and BM25 keyword scores remain part of hybrid ranking. SQL remains authoritative for structured records and application data. NVIDIA NIM is optional, is not the retrieval engine, and receives selected evidence for supplemental prose or judging.

### Components and responsibilities

| Component | Responsibility |
|---|---|
| OULAD CSV importer | Stream large VLE file, join source tables, derive profile metrics, upsert idempotently |
| React + Vite | Responsive browser experience and authenticated API calls |
| Streamlit | Optional local demo client in root `frontend.py`; calls the same FastAPI API for login, search, analysis, chat, and intervention management |
| FastAPI | REST routes, request validation, authentication, authorization, orchestration |
| Analysis services | Performance factors, risk band/priority, recommendations, prediction baselines |
| Retrieval service | Metadata constraints, BM25, local TF-IDF/LSA similarity, structured profile similarity |
| SQLAlchemy database | Users, profiles, plans, feedback, and audit events; SQLite default, PostgreSQL supported |
| NVIDIA NIM (optional) | Evidence-constrained natural-language summary and judge response |

## 4. Technology selection

| Choice | Reason and trade-off |
|---|---|
| Python 3.11+, FastAPI, Pydantic, Uvicorn | Python supports the data and ML libraries; FastAPI provides typed validation and OpenAPI. |
| React 18 and Vite | Primary responsive, interactive advisor website. |
| Streamlit | Optional local demonstration client; it does not replace the full React website. |
| SQLAlchemy with SQLite/PostgreSQL | Simple local setup with a path to a server database; not a vector index. |
| scikit-learn | Local TF-IDF/TruncatedSVD retrieval representation and random-forest demonstration baselines. |
| NVIDIA NIM, optional `meta/llama-3.2-11b-vision-instruct` | Provides optional natural-language analysis/judging behind the API. Requires a configured key; core workflows remain available without it. |
| Embedding model | No separately selected pretrained embedding model. TF-IDF with LSA is the actual local semantic representation. This avoids an embedding service dependency, at the cost of weaker semantic generalization. |
| Vector database | None selected or required by the current implementation. SQL profiles are ranked in process. This simplifies local deployment but is less scalable than an indexed vector store. |

## 5. Data and retrieval strategy

### Dataset preprocessing

The ingestion unit is one student × module × presentation. The importer joins OULAD student, registration, assessment, assessment-metadata, VLE-event, VLE-metadata, and course tables; streams `studentVle.csv`; aggregates clicks and active weeks; calculates assessment means/trends and completion; and upserts profiles. The resulting profile is the retrieval document (“chunk”). We do not split rows into overlapping token windows because the source contains structured records, not long prose documents.

### Embedding approach

Profile text is vectorized locally using TF-IDF and a truncated-SVD latent semantic representation. This is a feature representation fit on the profile corpus, not a pretrained neural embedding model. Structured categories and numeric student features contribute a separate similarity score. No vector database is used.

### Retrieval method and hybrid search

The search service applies optional course/presentation, region, education, age band, studied-credit, and previous-attempt metadata filters. It combines BM25 keyword relevance with local latent text and structured-profile similarity; a shortlist limits fitting/ranking cost on larger cohorts. Analysis responses may include retrieved profiles as evidence. Retrieval benchmark values and their weak relevance label are in `evaluation-report.md`.

## 6. Agent design and communication

`POST /api/agents/analyze` coordinates three sequential agents in one backend request:

1. **Performance analyst:** summarizes assessment level and trend, completion, activity, and relevant profile evidence.
2. **Risk assessor:** applies the transparent scoring rules and returns risk band plus contributing factors.
3. **Intervention recommender:** uses the prior outputs and retrieved historical profiles to propose advisor actions.

Agents communicate through typed in-process data/results, not autonomous agent-to-agent chat. The orchestrator returns a combined analysis and supporting evidence. If configured, NVIDIA NIM drafts supplemental grounded prose and a judge assessment; its output does not replace deterministic risk fields. Human advisors accept, edit, or reject recommendations.

## 7. Evaluation strategy and current evidence

| Evaluation | Method/status |
|---|---|
| Retrieval | 40-query offline Precision@5 and MRR benchmark; relevance is approximated by same-course membership, a weak proxy. Hybrid: P@5 0.450/MRR 0.681; semantic-only: 0.395/0.617; keyword-only: 0.475/0.729. The result currently favors keyword-only under this proxy. |
| Predictive baselines | Local held-out estimates from random-forest score and withdrawal models. These are demo estimates, not independently validated predictions. |
| DeepEval | Optional script covers faithfulness, answer relevancy, contextual relevancy, and custom support quality. Aggregate report is pending; do not present unrun scores. |
| LLM-as-Judge | Optional NIM judge call for individual analysis/support output; qualitative auxiliary signal, not ground truth. |
| API / workflow cases | `sample-test-cases.md` lists manual request and expected-behavior cases. Pydantic validation, auth/role responses, CRUD, retrieval, and errors are described in API docs/OpenAPI. |

Before operational use, replace weak retrieval labels with advisor judgments; evaluate calibrated predictive metrics, subgroup performance, drift, and prospective outcomes; and obtain institutional privacy/security review.

## 8. Guardrails, privacy, and oversight

- Pydantic validates request shapes and bounds; server-side checks verify referenced records and role permissions.
- Passwords are hashed; bearer tokens expire; administrative operations are role protected and audited.
- NVIDIA credentials stay in ignored `backend/.env` and are not returned to the browser.
- LLM prompts constrain answers to supplied evidence and recommendations remain subject to advisor review.
- OULAD identifiers are anonymized but row-level educational records remain sensitive.
- Risk indicators are not diagnoses, causal explanations, or calibrated probabilities. Do not automate consequential student decisions from these outputs.

### Persistent role and data scopes

Role selection is controlled by administrators. The first account in an empty database becomes the initial administrator; later registrations receive the advisor role and no student assignments by default. A persistent `user_access` table stores individual student grants for advisors and course grants for faculty. Server-side queries apply those grants to student lists, profile detail, recommendations, retrieval, agent analysis, predictions, support plans, feedback, and student CSV exports. Analysts receive aggregate dashboards and course-level exports; identifiable student routes are denied. Administrators can change roles, grant or revoke scopes, and review audited access changes. A user with no assignments sees an empty scope until an administrator grants access.

## 9. Local deployment

The primary interface is **React/Vite** at `http://127.0.0.1:5173`; an optional Streamlit demo client is in root `frontend.py` at `http://localhost:8501`. The API runs with FastAPI/Uvicorn at `http://127.0.0.1:8000`. Create `backend/.venv`, install `backend/requirements.txt`, copy `backend/.env.example` to `backend/.env`, and start `uvicorn app.main:app --reload` from `backend/`. Start React with `npm install` and `npm run dev` from `frontend/`, or start the demo client with `streamlit run frontend.py` from the repository root in the active Python environment. Full commands and secret handling are in the root README.

## 10. Challenges, trade-offs, and limitations

- Streaming the 10.6M-row VLE log reduces importer memory compared with loading the complete CSV.
- Feature-based retrieval is local and explainable, but does not have a pretrained embedding model or scalable vector index.
- The hybrid retrieval score trails keyword-only on the current weak-label benchmark, so its superiority is not established.
- The available profile-level model features and labels are historical and lack external validation, calibration, subgroup review, and prospective evaluation.
- Feedback is stored for review; the current system does not automatically retrain from it.
- No aggregate DeepEval report is supplied because a repeatable evaluation run has not been completed.

## 11. References

- [Dataset documentation and inventory](dataset-details.md)
- [API documentation](api-reference.md), [OpenAPI schema](openapi.json)
- [Evaluation report](evaluation-report.md), [model card](model-card.md), [rubric coverage](rubric-coverage.md)
