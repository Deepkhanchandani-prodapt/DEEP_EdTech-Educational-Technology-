# Dataset Details — Open University Learning Analytics Dataset (OULAD)

## Dataset name and purpose

**Open University Learning Analytics Dataset (OULAD).** This historical dataset supports analysis of student characteristics, course presentations, assessments, registration/withdrawal, and Virtual Learning Environment activity. In this project it is used to create student-course profiles for advisor-facing cohort analytics, historical similarity, performance/risk demonstrations, and support recommendations.

## Source and local import

The supplied folder is `open+university+learning+analytics+dataset/`. Its `OULAD.names` file describes the dataset. Official source: [OU Analyse — Open dataset](https://analyse.kmi.open.ac.uk/open_dataset). Publication: Kuzilek, Hlosta & Zdrahal, *Open University Learning Analytics dataset*, Scientific Data 4, 170171 (2017), [doi:10.1038/sdata.2017.171](https://doi.org/10.1038/sdata.2017.171).

## Data format

Comma-separated value (CSV) tables with headers. The importer reads the seven files below. It streams the large `studentVle.csv` table and joins the tables by student, module, presentation, assessment, and site identifiers as applicable.

## Key fields

| Source file | Key fields used | Purpose in this project |
|---|---|---|
| `studentInfo.csv` | `id_student`, `code_module`, `code_presentation`, `region`, `highest_education`, `age_band`, `studied_credits`, `num_of_prev_attempts`, `final_result` | Student-course features, metadata filters, historical outcome |
| `studentRegistration.csv` | student/module/presentation IDs, `date_registration`, `date_unregistration` | Registration and withdrawal context |
| `studentAssessment.csv` | `id_assessment`, `id_student`, `date_submitted`, `is_banked`, `score` | Assessment score and submission features |
| `assessments.csv` | `id_assessment`, module/presentation IDs, `assessment_type`, `date`, `weight` | Assessment metadata and join keys |
| `studentVle.csv` | student/site IDs, `date`, `sum_click` | Learning-platform activity volume and timing |
| `vle.csv` | `id_site`, module/presentation IDs, `activity_type`, `week_from`, `week_to` | VLE site metadata and joins |
| `courses.csv` | module/presentation IDs, `module_presentation_length` | Course presentation metadata |

Local CSV row counts (header excluded) were counted from the files in this project:

| File | Rows | Contents and use |
|---|---:|---|
| `studentInfo.csv` | 32,593 | Student-course demographics, studied credits, attempts, final result |
| `studentRegistration.csv` | 32,593 | Registration and withdrawal dates; registration metadata |
| `studentAssessment.csv` | 173,912 | Assessment submission date, banked flag, score |
| `assessments.csv` | 206 | Assessment ID, module/presentation, type, due day, weight |
| `studentVle.csv` | 10,655,280 | Student VLE clicks by site and day; streamed during import |
| `vle.csv` | 6,364 | VLE site-to-module/presentation/activity metadata |
| `courses.csv` | 22 | Module/presentation course length |

The idempotent importer produced **32,593 student-course-presentation profiles** in the local database. Run it from `backend/`:

```powershell
python scripts/ingest_oulad.py ..\open+university+learning+analytics+dataset
```

## Data preprocessing performed and derived profile fields

The importer joins on student ID, module, presentation, and assessment/site IDs. It calculates a mean submitted assessment score, difference between later and earlier assessment means, total VLE clicks, relative early-to-late activity trend, number of active weeks, fraction of assessment IDs with scored submissions, final result, and days since last observed VLE activity. Course, region, highest education, age band, studied credits, and previous attempts remain available as metadata filters.

## Data handling and limitations

- The source identifiers are anonymized in OULAD but should still be treated as sensitive row-level education records.
- The local files are the source of truth for row counts; they differ from headline counts sometimes quoted for other OULAD releases.
- Assessment average is an unweighted mean of available scored submissions in this implementation. It is not the official weighted course mark.
- The activity trend is a descriptive comparison of clicks in the first and second halves of observed activity days. It does not imply learning or causation.
- Missing submissions produce zero completion contribution; unobserved activity is not evidence of disengagement.
- Course/presentation results are historical and should not be interpreted as a validated prediction of a current learner.
- The source release terms and institutional governance must be reviewed before redistribution or any live student-support use.
