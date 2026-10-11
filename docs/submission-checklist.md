# Submission Checklist

**Project:** Eduvantage AI  
**Review date:** 6 October 2026

| Checklist item | Status | Evidence / note |
|---|---|---|
| Source code is complete | Checked | Backend (`backend/app/`), React frontend (`frontend/src/`), optional Streamlit client (`frontend.py`), ingestion and evaluation scripts are present. |
| README is updated | Checked | Root `README.md` covers the project, stack, setup, environment/API keys, local run steps, sample queries, and links to the submission files. |
| Architecture diagram included | Checked | `deliverables/architecture-diagram.pdf` and `.jpg`. |
| Design document included | Checked | `deliverables/design-document.pdf`; editable source: `docs/design-document.md`. |
| Presentation deck included | Checked | `deliverables/presentation.pptx` and `deliverables/presentation.pdf`. |
| APIs are working | Smoke-checked | Live local API health endpoint returned `200`; OpenAPI JSON loaded and includes the agent endpoint. The UI root returned `200`. Protected student/course/analytics routes correctly returned `401` without a token. Existing server logs record successful authenticated requests (`200`) to those routes. This does not exercise every endpoint. |
| Sample data included | Checked | Supplied OULAD CSVs are in `open+university+learning+analytics+dataset/`; deterministic synthetic analysis example: `deliverables/sample-outputs.json`. |
| Repository is accessible | Needs verification | This workspace contains no `.git` directory or remote URL. Confirm the submitted GitHub/GitLab repository link is reachable by the evaluator. |
| Team details are provided | Incomplete | The documents name “Eduvantage AI Capstone Team,” but do not provide individual names, IDs, roles, or contact details. Add the required roster before submission. |
| All deliverables follow naming conventions | Checked | Deliverable filenames use descriptive lowercase kebab-case, with `.pdf`, `.pptx`, `.jpg`, or `.json` extensions as appropriate. |
| Local deployment instructions are included | Checked | `README.md` documents Python virtual environment and dependencies, FastAPI/Uvicorn, React/Vite, optional Streamlit, environment setup, and optional API-key configuration. |
| No secrets or API keys are committed | Locally checked; commit status unverified | `.gitignore` excludes `.env` and `backend/.env`; `backend/.env.example` contains placeholders; a scan of project documentation/source found no populated API-key or secret assignments. Without Git metadata, committed history and remote contents cannot be audited here. |

## Before submission

1. Add the actual team roster (names, student IDs, and roles if required by the institution).
2. Paste the repository URL into the submission portal and verify access using the evaluator's account or an unauthenticated browser session, as appropriate.
3. Verify the remote repository contains no secrets in its current files or history. The local workspace has no Git metadata, so that check cannot be completed from this copy.

## Relevant files

- [README](../README.md)
- [Architecture diagram](../deliverables/architecture-diagram.pdf)
- [Design document](../deliverables/design-document.pdf)
- [API reference](../deliverables/api-reference.pdf)
- [Dataset documentation](../deliverables/dataset-details.pdf)
- [Presentation](../deliverables/presentation.pptx)
- [Evaluation artifacts](../deliverables/evaluation-artifacts.pdf)
