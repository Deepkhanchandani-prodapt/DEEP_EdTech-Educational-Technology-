"""Offline hybrid retrieval benchmark using course membership as a weak relevance label."""
import json
import sys
from pathlib import Path
from statistics import mean

sys.path.insert(0,str(Path(__file__).resolve().parents[1]))

from sqlalchemy import select

from app.main import SessionLocal, Student, hybrid_similar

with SessionLocal() as db:
    rows=db.scalars(select(Student).order_by(Student.student_code)).all()
    if len(rows)<3:
        raise SystemExit("Import or seed at least three student profiles first.")
    sample=rows[:min(40,len(rows))]
    reports={"hybrid":[],"semantic":[],"keyword":[]}
    for source in sample:
        candidates=[s for s in rows if s.student_code!=source.student_code]
        results=hybrid_similar(source,candidates,limit=len(candidates))
        relevant={s.student_code for s in candidates if s.course==source.course}
        if not relevant: continue
        for method,field in [("hybrid","similarity"),("semantic","semantic_match"),("keyword","keyword_match")]:
            ranked=sorted(results,key=lambda item:item[field],reverse=True)[:5]
            hits=[index for index,item in enumerate(ranked,1) if item["id"] in relevant]
            reports[method].append({"precision_at_5":len(hits)/5,"mrr":1/min(hits) if hits else 0})
    result={name:{"queries":len(values),"precision_at_5":round(mean(x["precision_at_5"] for x in values),3) if values else 0,"mrr":round(mean(x["mrr"] for x in values),3) if values else 0} for name,values in reports.items()}
    output={"relevance_label":"Same course as query profile; weak proxy for historical-case relevance, not advisor relevance judgment.","queries":len(sample),"results":result,"warning":"Synthetic/default records limit these retrieval metrics; use expert-labeled institutional cases for valid evaluation."}
    with open("retrieval-evaluation.json","w",encoding="utf-8") as file: json.dump(output,file,indent=2)
    print(json.dumps(output,indent=2))
