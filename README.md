# Eduvantage AI

## Project overview

Eduvantage AI is a student success intelligence application for advisors. It combines student/course records, assessment results, and learning activity to find similar historical profiles, highlight possible academic risk, and suggest support actions. Advisors review the evidence and make all final decisions.

## Problem statement

Advisors need to review many student records across multiple datasets. It can be difficult to identify students who may need timely support, understand which assessment or engagement signals contributed to a concern, and find comparable historical cases.

## Business objective

Help advisors prioritize their workload, understand student performance and engagement patterns, and create traceable, individualized intervention plans. Risk indicators are decision support and must not be used as an automatic or final decision about a student.

## Solution summary

The application imports the Open University Learning Analytics Dataset (OULAD), aggregates activity and assessment data into student-course profiles, and presents dashboards, filters, student details, similarity search, support recommendations, cohort chat, and editable intervention plans. Retrieval combines BM25 keyword ranking, ChromaDB vector search, and structured feature similarity. A multi-stage workflow produces performance analysis, risk assessment, and intervention suggestions. NVIDIA NIM analysis and LLM-as-judge are optional; deterministic analysis remains available without an API key. A clean database uses clearly labeled synthetic demo profiles until OULAD data is imported.

## Technology stack

| Area | Technology |
|---|---|
| Programming languages | Python 3.11+; JavaScript/JSX (with TypeScript tooling) |
| Frontend | React 18, Vite 8 |
| Optional demo UI | Streamlit client in root `frontend.py` |
| API | FastAPI, Uvicorn, Pydantic |
| Data and persistence | SQLAlchemy, SQLite by default; PostgreSQL supported |
| Machine learning and retrieval | scikit-learn, BM25 keyword retrieval, ChromaDB vector retrieval |
| LLM | NVIDIA NIM, configured with `NVIDIA_MODEL` (default: `meta/llama-3.2-11b-vision-instruct`); optional |
| Embedding model | Local scikit-learn HashingVectorizer creates fixed-width vectors; no external embedding API or model download is required. |
| Vector database | ChromaDB with persistent local storage for student-profile vectors. SQL remains the source of truth for relational records, accounts, permissions, and interventions. |
| Authentication | Password-based JWT authentication; optional Google OAuth ID-token verification |
| Evaluation | Offline retrieval ranking evaluation; optional DeepEval and LLM-as-judge |

## Installation and local deployment

The full website is the shipped **React/Vite** application. An additional Streamlit demonstration client is provided in root `frontend.py`; both interfaces call the same FastAPI backend. Python dependencies, including Streamlit and Requests for the demo client, are declared in `backend/requirements.txt`; React packages are declared in `frontend/package.json`.

### Prerequisites

- Python 3.11 or newer
- Node.js 20.19+ or 22.12+ (npm included)
- The supplied OULAD CSV directory for real dataset-backed profiles

### Dependency installation

In PowerShell, from the repository root, open two terminals. In terminal 1, set up and start the API:

```powershell
cd backend
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
if (-not (Test-Path .env)) { Copy-Item .env.example .env }
uvicorn app.main:app --reload
```

In terminal 2, install frontend packages and start Vite:

```powershell
cd frontend
npm install
npm run dev
```

To run the Streamlit demonstration UI instead of React, activate the same Python virtual environment, return to the repository root, and run:

```powershell
cd ..
streamlit run frontend.py
```

Streamlit opens at http://localhost:8501. Start the API first; the client defaults to `http://127.0.0.1:8000`. Set `EDUVANTAGE_API_URL` or edit the API URL in its sidebar to use another local API address. The Streamlit client includes authentication, filtered student search, profile/agent analysis, cohort chat, and intervention-plan create/edit/delete. React remains the full-featured primary website.

Open http://127.0.0.1:5173. The API is at http://127.0.0.1:8000 and interactive API documentation is at http://127.0.0.1:8000/docs. Register at `/signup`; the first registered account is the initial administrator. To make a production frontend bundle, run `npm run build` in `frontend/`.

### Roles and access scopes

The first account created in a fresh database becomes the administrator. Later email/password and Google registrations start as advisors; a user cannot choose or elevate their own role during signup. In **Admin & Data → Accounts, roles & access**, an administrator can assign one of four roles and grant the scope it needs. Advisor accounts see only explicitly assigned student profiles. Faculty accounts see profiles in explicitly assigned courses. Analysts see cohort and course aggregates, with student-identifiable pages and exports blocked. Administrators manage all records and user access. These grants are stored in the configured database and remain after restart. Newly registered advisor accounts have no student records until an administrator assigns them.

### Environment setup and API key configuration

Copy `backend/.env.example` to `backend/.env`. The backend loads configuration from that file. Keep `.env` private and do not commit API keys. The example includes:

```dotenv
DATABASE_URL=sqlite:///./eduvantage.db
SECRET_KEY=replace-with-a-long-random-secret
DEMO_MODE=true
NVIDIA_API_KEY=
NVIDIA_MODEL=meta/llama-3.2-11b-vision-instruct
GOOGLE_CLIENT_ID=
```

Replace `SECRET_KEY` with a private random value. To enable NVIDIA NIM features, set `NVIDIA_API_KEY` to your NVIDIA API key and choose a model available to that key in `NVIDIA_MODEL`. Without it, the core app uses deterministic analysis. For Google sign-in, set `GOOGLE_CLIENT_ID` to a Google OAuth Web application client ID and add the frontend origin to its authorized JavaScript origins. Google sign-in is optional; email/password sign-in works without these credentials. Restart the API after changing backend environment values.

SQLite is used by default for relational application data. To use PostgreSQL, set `DATABASE_URL` to the SQLAlchemy connection URL for your database. Student-profile vectors are stored in a persistent ChromaDB directory (`backend/chroma` by default); set `CHROMA_PATH` to choose another path. ChromaDB supports semantic retrieval and does not replace the relational store used for accounts, permissions, interventions, and structured student records.

### Importing the OULAD dataset

From `backend/`, run:

```powershell
python scripts/ingest_oulad.py ../open+university+learning+analytics+dataset
```

The importer streams the large `studentVle.csv` file and aggregates assessment and activity records into student-course-presentation profiles. It can be rerun to refresh imported records. Keep student data in an appropriately protected environment.

## Sample user queries

These examples describe the intended request and response. Actual counts, retrieved profiles, risk levels, and recommendations depend on the dataset, filters, and model configuration.

1. **Query:** “Show students at high risk in course AAA 2013J.”  
   **Expected output:** A filtered, priority-ranked student list with anonymized IDs, course, average assessment score, VLE activity, risk category, trend, and outcome where available.
2. **Query:** “Find students similar to this profile with low assessment scores and declining activity.”  
   **Expected output:** A ranked list of comparable historical profiles with similarity scores and the matching academic or engagement signals.
3. **Query:** “Why is this student marked high risk?”  
   **Expected output:** A student analysis that summarizes relevant assessment and activity evidence, explains the contributing factors, and states the risk category for advisor review.
4. **Query:** “Recommend a support plan for a student whose assessment performance is falling.”  
   **Expected output:** Practical support suggestions based on performance and engagement evidence, suitable for an advisor to review and edit into an intervention plan.
5. **Query:** “Compare assessment performance and learning activity across courses.”  
   **Expected output:** Course-level performance and engagement summaries, trend comparisons, and notable differences based on the selected cohort.

## Existing features and project details

## Start locally (React + FastAPI, no Docker)

Requires Python 3.11+ and Node.js 20.19+ (or 22.12+).

In terminal 1, start the API:

```powershell
cd backend
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
if (-not (Test-Path .env)) { Copy-Item .env.example .env }
uvicorn app.main:app --reload
```

In terminal 2, start the React frontend:

```powershell
cd frontend
npm install
npm run dev
```

On the supplied Windows workspace, run `start.cmd` from `frontend`; it starts the same flow and can use the Python `nodejs-wheel` fallback if system Node is unavailable.

Open http://127.0.0.1:5173. Vite proxies `/api` to the FastAPI server on port 8000. API docs: http://127.0.0.1:8000/docs. The first registered account is the initial administrator; later signups cannot self-assign admin access. Build the frontend with `npm run build`.

Create an account on `/signup`; first account is admin. To load the supplied OULAD data, run this from `backend/`: `python scripts/ingest_oulad.py ../open+university+learning+analytics+dataset`. The importer streams the large `studentVle.csv` and aggregates assessment and activity data into one record per student-course presentation. The process is safe to rerun and refreshes imported records. Avoid putting identifiable student data in demo environments.

## Configuration

Copy `backend/.env.example` to `backend/.env`. `SECRET_KEY` must be replaced for deployments. NVIDIA NIM uses `NVIDIA_API_KEY` from this ignored environment file; it is never stored in source control. The configured model must be available to the NVIDIA API key. Demo mode works without a provider key and falls back to deterministic analysis. SQLite is the local default; `DATABASE_URL` can point SQLAlchemy at PostgreSQL.

Google sign-in requires a Google OAuth **Web application** client ID. Set the same client ID as `GOOGLE_CLIENT_ID` in `backend/.env` and `VITE_GOOGLE_CLIENT_ID` in `frontend/.env.local`, then restart both servers. Add the development origin (for example `http://127.0.0.1:5173`) to the OAuth client's authorized JavaScript origins in Google Cloud Console. The API verifies Google ID tokens before creating or signing in a workspace account. Without these credentials, password login and signup continue to work and the Google sign-in option stays hidden.

Student-profile vectors are persisted in `backend/chroma` by default; set `CHROMA_PATH` to choose another directory. SQLite remains the local default for relational application data. To use PostgreSQL, set `DATABASE_URL` to the SQLAlchemy connection URL for your database. ChromaDB powers semantic retrieval and does not replace the relational store for accounts, permissions, interventions, or structured student records.

Workspace profile details can be edited under Profile & Settings. Intervention plans can be created, edited, and deleted by their owner; administrators can manage all plans. Administrators can also edit or delete student records from a student profile. These changes are saved to the configured database.

## Included

- Email/password auth, hashed passwords, signed bearer tokens, roles, protected APIs.
- Student list/detail, dashboard and course analytics, risk scoring and prioritization, six-field metadata filters, support recommendations, hybrid BM25 + ChromaDB vector similarity, OULAD grounded cohort chat, feedback, interventions, CSV import/export, and audit trail.
- Performance and withdrawal random forest demo models with holdout estimates; a three-stage performance/risk/intervention agent workflow; optional NVIDIA NIM summary and LLM judge.
- Optional DeepEval faithfulness, answer relevance, context relevance, and custom support quality evaluation; offline hybrid retrieval ranking metrics.
- React and Vite beige/espresso responsive interface with dashboard charts, search, risk and student views.
- OULAD ingestion utility, model card, architecture and presentation notes.

Risk and prediction outputs are demonstration indicators for advisor review, not validated operational predictions. The app uses imported OULAD profiles when available and seeded synthetic profiles as a clean-install fallback. Similarity uses BM25 keywords, local fixed-width vectors persisted in ChromaDB, and structured feature similarity; vectors are not generated by a pretrained transformer. Read [docs/rubric-coverage.md](docs/rubric-coverage.md) for requirement-by-requirement status, evaluation commands, and limitations.

From `backend/`, run `python scripts/evaluate_retrieval.py` for an offline ranking benchmark. For LLM-as-judge evaluation, install `pip install -r requirements-evaluation.txt`, configure `NVIDIA_API_KEY`, then run `python scripts/evaluate_quality.py`. DeepEval will send the selected profile evidence to the configured NVIDIA endpoint; use synthetic records for a demo evaluation.

## Submission deliverables

Review the item-by-item [submission checklist](docs/submission-checklist.md). It records what is present locally and flags the team roster and repository access checks that require external details.

The complete source includes `backend/`, `frontend/`, and the optional root `frontend.py` Streamlit API client; this file is the project README.

## GitHub upload and the OULAD activity file

`studentVle.csv` is about 433 MB. The GitHub copy uses a lossless `studentVle.csv.gz` version (about 40 MB), tracked with Git LFS; the ingestion script reads either the original CSV or its gzip version. The uncompressed original remains in this local folder and is ignored by Git. Install Git LFS, then run `git lfs install` before staging and pushing the project. Do not upload through GitHub's browser file uploader, which does not apply Git LFS filters.

| Deliverable | File |
|---|---|
| Architecture diagram (PDF and JPEG) | [PDF](deliverables/architecture-diagram.pdf) · [JPEG](deliverables/architecture-diagram.jpg) |
| Design document (PDF) | [PDF](deliverables/design-document.pdf) · [source](docs/design-document.md) |
| API documentation | [PDF](deliverables/api-reference.pdf) · [Markdown](docs/api-reference.md) · [OpenAPI JSON](docs/openapi.json) · interactive `/docs` |
| Dataset details | [PDF](deliverables/dataset-details.pdf) · [Markdown](docs/dataset-details.md) |
| Presentation deck | [PowerPoint](deliverables/presentation.pptx) · [PDF](deliverables/presentation.pdf) |
| Evaluation artifacts | [PDF report](deliverables/evaluation-artifacts.pdf) · [details and statuses](docs/evaluation-artifacts.md) · [retrieval metrics JSON](backend/retrieval-evaluation.json) |
| Evaluation test cases | [20 manual acceptance cases](docs/sample-test-cases.md) |
| Sample outputs | [Synthetic-only student-analysis JSON](deliverables/sample-outputs.json) · [generator](backend/scripts/generate_sample_output.py) |

DeepEval and RAGAS scores are explicitly marked **not run** in the evaluation report; no scores are fabricated. The optional DeepEval runner uses synthetic records only for external judging. RAGAS is not currently integrated.

To regenerate the PDFs and PowerPoint, install `docs/requirements-deliverables.txt` and run `python docs/build_deliverables.py` from the repository root. To refresh OpenAPI, run from `backend/`: `python -c "import json; from pathlib import Path; from app.main import app; Path('../docs/openapi.json').write_text(json.dumps(app.openapi(), indent=2), encoding='utf-8')"`.
