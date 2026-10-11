"""Write a deterministic, synthetic-only student-analysis example artifact."""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from sqlalchemy import select
from app.main import (
    SessionLocal, Student, hybrid_similar, performance_agent, risk_agent,
    student_json, support_agent,
)

root = Path(__file__).resolve().parents[2]
output_path = root / "deliverables" / "sample-outputs.json"

with SessionLocal() as db:
    profiles = db.scalars(
        select(Student).where(Student.synthetic.is_(True)).order_by(Student.student_code)
    ).all()
    if len(profiles) < 2:
        raise SystemExit("At least two synthetic demo profiles are required to build this sample.")
    target, peers = profiles[0], profiles[1:]
    matches = hybrid_similar(target, peers, limit=3)
    performance = performance_agent(target)
    risk = risk_agent(target)
    support = support_agent(target, matches)
    sample = {
        "artifact": "Deterministic student-analysis sample",
        "data_source": "Synthetic demo profiles only; no NVIDIA/NIM call is made.",
        "request": {"student_code": target.student_code},
        "response": {
            "student_code": target.student_code,
            "summary": f"{target.student_code} has a {risk['level'].lower()} indicator (risk score {risk['risk_score']}/100) based on academic and engagement signals.",
            "risk_assessment": student_json(target),
            "performance_analysis": performance,
            "risk_analysis": risk,
            "support_recommendation": support,
            "agent_workflow": [performance, risk, support],
            "retrieved_cases": matches,
            "evidence": performance["evidence"],
            "key_factors": risk["explainable_factors"],
            "recommended_intervention": support["actions"],
            "confidence": "Heuristic indicator; review source data with the student.",
            "limitations": "Synthetic example. Risk is a demonstration heuristic and is not a causal finding or validated prediction.",
            "llm_used": False,
            "judge": {"status": "not_configured", "approved": None},
        },
    }

output_path.parent.mkdir(parents=True, exist_ok=True)
output_path.write_text(json.dumps(sample, indent=2), encoding="utf-8")
print(f"Wrote synthetic-only sample output to {output_path}")
