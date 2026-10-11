# Evaluation Artifacts

**Project:** Eduvantage AI  
**Report date:** 6 October 2026

This package separates measured results, manual acceptance cases, and model-quality evaluations that are pending. The application supports advisor review; none of the metrics below validate operational decisions.

## Retrieval results

The saved 40-query benchmark is [`backend/retrieval-evaluation.json`](../backend/retrieval-evaluation.json). It uses same-course membership as a weak relevance proxy, not human judgments of profile similarity.

| Retrieval mode | Queries | Precision@5 | MRR |
|---|---:|---:|---:|
| Hybrid keyword + TF-IDF/LSA + structured profile | 40 | 0.450 | 0.681 |
| Semantic-only | 40 | 0.395 | 0.617 |
| Keyword-only | 40 | 0.475 | 0.729 |

Keyword-only ranks best under this proxy. Do not claim that hybrid retrieval outperforms its baseline. Same-course relevance can reward course membership even when individual profiles are not meaningfully similar. The benchmark is exploratory and its source records include synthetic/default data; institutionally approved, advisor-labeled relevance judgments are needed for meaningful quality assessment.

Re-run from `backend/`:

```powershell
python scripts/evaluate_retrieval.py
```

## DeepEval scores

**Status: not run; no scores are available.** The optional script is [`backend/scripts/evaluate_quality.py`](../backend/scripts/evaluate_quality.py). It evaluates one synthetic profile using Faithfulness, Answer Relevancy, Contextual Relevancy, and a custom advisor-support G-Eval through NVIDIA NIM. It now selects synthetic profiles only and states this in the report; it will not choose an imported OULAD row for external judging.

To run it, install `backend/requirements-evaluation.txt`, configure `NVIDIA_API_KEY` and an available `NVIDIA_MODEL` in ignored `backend/.env`, then run:

```powershell
cd backend
pip install -r requirements-evaluation.txt
python scripts/evaluate_quality.py
```

The generated `backend/deepeval-results.json` is a one-record demonstration result, not a statistically representative benchmark. Preserve the exact model ID, run time, scores, and judge reasons when reporting a future run. Failed or skipped metrics must stay marked as such.

## RAGAS scores

**Status: not run; no scores are available.** RAGAS is not currently integrated as an evaluation script or installed evaluation dependency. The project must not report fabricated RAGAS values. An RAGAS run requires a defined evaluation dataset containing question, retrieved contexts, answer, and reference answer, plus a configured judge/embedding provider and documented metric versions. The current retrieval proxy does not by itself provide those reference answers.

## Test cases

The project includes 20 manual acceptance cases in [`sample-test-cases.md`](sample-test-cases.md), including role-safe registration, persisted advisor/faculty scopes, aggregate-only analyst access, admin scope management, and the existing authentication, retrieval, intervention, import, and export workflows. They are documented manual cases, not an automated passing test report.

## Sample output

[`deliverables/sample-outputs.json`](../deliverables/sample-outputs.json) contains one deterministic analysis response generated from seeded synthetic profiles only. The artifact is labeled synthetic and uses no NVIDIA/NIM call. Recreate it from `backend/` with:

```powershell
python scripts/generate_sample_output.py
```

The sample includes performance evidence, a heuristic risk band and factors, retrieved synthetic profiles, advisor suggestions, and limitations. Example values are illustrative and are not a validated prediction.

## Interpretation and limits

- The 40-query retrieval set and one-record DeepEval script are too small and weakly labeled for claims of broad quality or safety.
- DeepEval and RAGAS are different evaluation methods; absence of a score is not a zero score.
- Use only synthetic profiles for external LLM judging unless a separate, explicit data-governance review approves another evaluation dataset.
- Do not use these results to automate grading, retention, or intervention decisions.
