# Model card: student support demonstration

## Models included

- **Risk indicator:** an explainable weighted heuristic using assessment average/trend, VLE clicks/trend, previous attempts, and completion.
- **Performance prediction:** a random forest regressor trained from available records to estimate assessment score from score trend, activity, completion, attempts, credits, and active weeks.
- **Withdrawal prediction:** a random forest classifier trained to estimate the recorded `Withdrawn` outcome from those same profile features.
- **Similarity retrieval:** BM25 keyword ranking blended with TF-IDF/TruncatedSVD semantic text features and normalized structured profile similarity.

## Data and evaluation

The database uses imported OULAD student-course profiles when present and falls back to seeded synthetic profiles in a clean database. The importer joins assessment and VLE records. Random forest endpoints report holdout MAE/R² and ROC-AUC where both withdrawal classes are available. These are exploratory estimates, not external validation. Retrieval measures use same-course membership as a weak proxy label. DeepEval is optional and needs the evaluation dependencies and a working NVIDIA NIM model/key; a DeepEval report is not included yet.

## Intended use and limits

These outputs help demonstrate how an advisor could locate profiles for human review. They are not validated predictions and must not be used to determine grades, progression, student access, withdrawal, or disciplinary outcomes. Synthetic scores and weak proxy labels do not establish predictive validity, calibration, subgroup fairness, or institutional usefulness. Advisors must check source records and discuss support with students. Validate on institution-approved, time-separated, labeled data before considering operational use.
