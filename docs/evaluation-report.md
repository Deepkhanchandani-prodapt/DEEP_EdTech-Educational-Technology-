# Evaluation Report

See the polished [Evaluation Artifacts PDF](../deliverables/evaluation-artifacts.pdf) and the full [Evaluation Artifacts source](evaluation-artifacts.md).

## Results at a glance

The saved 40-query retrieval benchmark reports hybrid Precision@5 **0.450** / MRR **0.681**, semantic-only **0.395** / **0.617**, and keyword-only **0.475** / **0.729**. Same-course membership is a weak relevance proxy, so keyword-only ranks highest under this label and the benchmark is exploratory.

**DeepEval:** not run; no scores available. The optional script has been restricted to synthetic profiles before external judging.  
**RAGAS:** not integrated or run; no scores available.  
**Test cases:** 16 manual acceptance cases in [sample-test-cases.md](sample-test-cases.md); these are not automated test results.  
**Sample outputs:** deterministic synthetic-only API analysis in [deliverables/sample-outputs.json](../deliverables/sample-outputs.json).

Absence of evaluation scores is not a zero score. Do not invent values or use these artifacts to automate consequential student decisions.
