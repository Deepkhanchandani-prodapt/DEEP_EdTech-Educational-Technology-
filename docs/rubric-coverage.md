# Capstone rubric coverage

This matrix distinguishes implemented code from optional, credential-backed evaluation and from evidence that still needs a real labeled dataset. It is not a claim of marks earned.

| Rubric area | Weight | Project evidence | Status / limit |
|---|---:|---|---|
| Functional correctness and deliverables | 20% | Student CRUD, risk indicators, support actions, prioritized list, hybrid historical search and API | Implemented; imported OULAD locally, synthetic fallback on clean installs |
| Architecture and design decisions | 10% | React, FastAPI, JWT, SQLAlchemy, SQLite/PostgreSQL, separate retrieval/prediction modules | Implemented and documented |
| LLM selection | 5% | Optional NVIDIA NIM model and model setting | Optional configuration; numeric results remain deterministic |
| Embedding model evaluation | 5% | Local TF-IDF + TruncatedSVD latent semantic representation; keyword and semantic scores exposed | `scripts/evaluate_retrieval.py` measures Precision@5/MRR against same-course weak labels; not a pretrained transformer embedding |
| Retrieval and RAG strategy | 10% | 70% BM25 keyword ranking blended with 30% latent text and structured profile similarity; metadata constraints; retrieved cases supplied to analysis | Implemented; weak same-course benchmark currently favors keyword-only ranking over the hybrid, so tune against advisor-labeled cases |
| Accuracy and quality evaluation | 10% | Holdout regression/ROC-AUC estimates; DeepEval Faithfulness, Answer Relevancy, Contextual Relevancy, custom G-Eval script | Model estimates are demo-data-only. DeepEval needs `requirements-evaluation.txt` and `NVIDIA_API_KEY`; it has not been run without that key |
| Agent design and orchestration | 10% | Performance, risk, and intervention recommendation agents return separate evidence and are coordinated by `/api/agents/analyze` | Implemented as transparent deterministic agents; NIM judge is optional |
| Security and compliance | 5% | Authentication, role checks, input schemas, ID validation, audit log, no automated student action | Implemented for demo; real student data needs institution security/privacy review |
| User experience | 5% | Dashboard, student search/detail, risk, analytics, recommendations, interventions, assistant, reports, evaluations, model, admin, editable profile | Implemented in React; screens use API/database data |
| Innovation and optimization | 5% | Hybrid retrieval, feature-based prioritization, explainable indicators, feedback loop | Implemented; feedback is for human review and does not retrain models |
| Presentation and documentation | 10% | README, architecture diagram, design document, model card, API docs, dataset details, test cases, presentation deck | Deliverable files are indexed in root README; present prototype limitations clearly |
| Testing and robustness | 5% | Pydantic validation, API error handling, frontend build, Python syntax check, benchmark scripts | Basic checks completed; formal regression tests and live DeepEval run remain to be run |

## Running the evaluation evidence

The current 40-query weak-label run is saved at `backend/retrieval-evaluation.json`: hybrid Precision@5 **0.450**, MRR **0.681**; semantic-only Precision@5 **0.395**, MRR **0.617**; keyword-only Precision@5 **0.475**, MRR **0.729**. Under this weak same-course label, keyword-only is stronger. This identifies a real tuning issue; it should not be presented as hybrid beating its baseline. A DeepEval aggregate report is pending.

From `backend/`:

```powershell
python scripts/evaluate_retrieval.py
```

For LLM-as-judge evaluation, install the optional evaluator and configure the NVIDIA key in `backend/.env`:

```powershell
pip install -r requirements-evaluation.txt
python scripts/evaluate_quality.py
```

The retrieval benchmark uses same-course membership as a weak proxy label. The DeepEval sample evaluates one current local record. Neither is a substitute for a held-out, institutionally approved, advisor-labeled benchmark.
