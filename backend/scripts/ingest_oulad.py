"""Import the public OULAD CSV files into Eduvantage's student table.

Run from backend/: python scripts/ingest_oulad.py ../open+university+learning+analytics+dataset
The large studentVle file is streamed; it is never loaded into memory at once.
"""
import csv
import gzip
import sys
from collections import defaultdict
from datetime import datetime
from pathlib import Path

BACKEND = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BACKEND))
from app.main import SessionLocal, Student  # noqa: E402


def open_csv_text(path):
    path = Path(path)
    if not path.is_file() and Path(f"{path}.gz").is_file():
        path = Path(f"{path}.gz")
    if path.suffix == ".gz":
        return gzip.open(path, "rt", encoding="utf-8-sig", newline="")
    return path.open("r", encoding="utf-8-sig", newline="")


def read_rows(path):
    with open_csv_text(path) as f:
        yield from csv.DictReader(f)


def main(folder):
    folder = Path(folder).resolve()
    required = ["studentInfo.csv", "studentRegistration.csv", "studentAssessment.csv", "studentVle.csv", "assessments.csv", "courses.csv", "vle.csv"]
    missing = [name for name in required if not (folder / name).is_file() and not (folder / f"{name}.gz").is_file()]
    if missing:
        raise SystemExit("Missing OULAD files: " + ", ".join(missing))

    def key(row):
        return (row["id_student"], row["code_module"], row["code_presentation"])

    info = {key(row): row for row in read_rows(folder / "studentInfo.csv")}
    registration = {key(row): row for row in read_rows(folder / "studentRegistration.csv")}
    course_length = {(r["code_module"], r["code_presentation"]): int(r["module_presentation_length"] or 1) for r in read_rows(folder / "courses.csv")}
    assessment_module = {}
    assessment_counts = defaultdict(int)
    for r in read_rows(folder / "assessments.csv"):
        assessment_module[r["id_assessment"]] = (r["code_module"], r["code_presentation"])
        assessment_counts[(r["code_module"], r["code_presentation"])] += 1
    activity_types = {r["id_site"]: r["activity_type"] for r in read_rows(folder / "vle.csv")}

    assessments = defaultdict(list)
    for i, r in enumerate(read_rows(folder / "studentAssessment.csv"), 1):
        ck = assessment_module.get(r["id_assessment"])
        if ck and r["score"]:
            try:
                assessments[(r["id_student"], *ck)].append((int(r["date_submitted"] or 0), float(r["score"]), int(r["id_assessment"])))
            except ValueError:
                pass
    print(f"Loaded {len(info):,} student-course registrations and assessment records.", flush=True)

    activity = defaultdict(lambda: [0, set(), defaultdict(int)])
    vle_path = folder / "studentVle.csv"
    count = 0
    with open_csv_text(vle_path) as f:
        for row in csv.DictReader(f):
            count += 1
            try:
                k = key(row)
                day = int(row["date"] or 0)
                clicks = int(row["sum_click"] or 0)
                a = activity[k]
                a[0] += clicks
                a[1].add(day // 7)
                a[2][day] += clicks
            except (KeyError, ValueError):
                continue
            if count % 2_500_000 == 0:
                print(f"Read {count:,} learning-activity rows…", flush=True)
    print(f"Aggregated {count:,} learning-activity rows.", flush=True)

    inserted = updated = 0
    with SessionLocal() as db:
        existing = {s.student_code: s for s in db.query(Student).filter(Student.synthetic.is_(False)).all()}
        batch = []
        for k, profile in info.items():
            sid, module, presentation = k
            code = f"OU{sid}_{module}_{presentation}"[:40]
            length = max(1, course_length.get((module, presentation), 1))
            scores = sorted(assessments.get(k, []))
            unique = {x[2] for x in scores}
            average = sum(x[1] for x in scores) / len(scores) if scores else 0.0
            first_half = [x[1] for x in scores if x[0] <= length / 2]
            second_half = [x[1] for x in scores if x[0] > length / 2]
            score_trend = (sum(second_half) / len(second_half) - sum(first_half) / len(first_half)) if first_half and second_half else 0.0
            clicks, weeks, by_day = activity.get(k, (0, set(), {}))
            days = sorted(by_day)
            split = max(1, len(days) // 2)
            early = sum(by_day[d] for d in days[:split])
            late = sum(by_day[d] for d in days[split:])
            engagement_trend = max(-100.0, min(100.0, (late - early) / max(1, early) * 100)) if len(days) > 1 else 0.0
            registration_row = registration.get(k, {})
            try:
                reg_day = int(registration_row.get("date_registration", 0) or 0)
            except ValueError:
                reg_day = 0
            last_activity = f"{max(0, length - max(days, default=0))} days ago" if days else "No activity"
            final_result = profile.get("final_result") or "Unknown"
            # Scores and outcomes follow OULAD's published percentage/result categories.
            values = dict(course=f"{module} · {presentation}", region=profile.get("region") or "Unknown", education=profile.get("highest_education") or "Unknown", age_band=profile.get("age_band") or "Unknown", credits=int(profile.get("studied_credits") or 0), attempts=int(profile.get("num_of_prev_attempts") or 0), score=round(average, 2), score_trend=round(score_trend, 2), clicks=clicks, engagement_trend=round(engagement_trend, 2), active_weeks=len(weeks), completion=min(1.0, len(unique) / max(1, assessment_counts.get((module, presentation), 1))), final_result=final_result, last_activity=last_activity, synthetic=False)
            obj = existing.get(code)
            if obj:
                for name, value in values.items():
                    setattr(obj, name, value)
                updated += 1
            else:
                batch.append(Student(student_code=code, **values))
                inserted += 1
            if len(batch) >= 1000:
                db.add_all(batch); db.commit(); batch.clear()
        if batch:
            db.add_all(batch)
        db.commit()
    print(f"OULAD import complete: {inserted:,} profiles added, {updated:,} existing profiles refreshed.")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        raise SystemExit("Usage: python scripts/ingest_oulad.py <directory-containing-OULAD-CSVs>")
    main(sys.argv[1])
