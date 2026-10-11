"""DeepEval LLM-as-judge checks for one real local demo profile.

Requires `pip install -r requirements-evaluation.txt` and NVIDIA_API_KEY.
The profile content sent to the configured NVIDIA endpoint is synthetic by default.
"""
import asyncio
import json
import os
import sys
import urllib.request
from pathlib import Path

from dotenv import load_dotenv

load_dotenv(Path(__file__).resolve().parents[1] / ".env")

sys.path.insert(0,str(Path(__file__).resolve().parents[1]))

from deepeval.metrics import AnswerRelevancyMetric, ContextualRelevancyMetric, FaithfulnessMetric, GEval
from deepeval.models.base_model import DeepEvalBaseLLM
from deepeval.test_case import LLMTestCase, LLMTestCaseParams
from sqlalchemy import select

from app.main import SessionLocal, Student, hybrid_similar, performance_agent, risk_agent, student_json, support_agent

class NIMJudge(DeepEvalBaseLLM):
    def __init__(self, api_key, model_name):
        self.api_key=api_key
        self.model_name=model_name

    def load_model(self):
        return self

    def get_model_name(self):
        return f"NVIDIA NIM {self.model_name}"

    def generate(self, prompt: str) -> str:
        payload={"model":self.model_name,"temperature":0,"max_tokens":700,"messages":[{"role":"user","content":prompt}]}
        request=urllib.request.Request("https://integrate.api.nvidia.com/v1/chat/completions",data=json.dumps(payload).encode(),headers={"Authorization":f"Bearer {self.api_key}","Content-Type":"application/json"},method="POST")
        with urllib.request.urlopen(request,timeout=40) as response:
            return json.loads(response.read().decode())["choices"][0]["message"]["content"]

    async def a_generate(self, prompt: str) -> str:
        return await asyncio.to_thread(self.generate,prompt)

if not os.getenv("NVIDIA_API_KEY"):
    raise SystemExit("Set NVIDIA_API_KEY in backend/.env before running DeepEval LLM-as-judge metrics.")

with SessionLocal() as db:
    # Only send seeded synthetic profiles to the external judge. Never choose an
    # imported OULAD row implicitly for an API-backed quality evaluation.
    student=db.scalar(select(Student).where(Student.synthetic.is_(True)).order_by(Student.student_code).limit(1))
    if not student:
        raise SystemExit("No synthetic demo profile found. The external DeepEval run is restricted to synthetic records.")
    peers=db.scalars(select(Student).where(Student.synthetic.is_(True),Student.student_code!=student.student_code).order_by(Student.student_code)).all()
    similar=hybrid_similar(student,peers,limit=3)
    perf=performance_agent(student)
    risk=risk_agent(student)
    support=support_agent(student,similar)
    context=perf["evidence"]+[f"Risk indicator {risk['level']} ({risk['risk_score']}/100)"]
    context += [f"Historical profile {x['id']}: {x['similarity']}% similarity, outcome {x['final_result']}" for x in similar]
    actions="; ".join(support["actions"])
    output=f"{perf['summary']} Risk level {risk['level']} with score {risk['risk_score']}/100. Suggested advisor actions: {actions}"
    test_case=LLMTestCase(input=f"Analyze {student.student_code} and suggest advisor support based on academic and engagement evidence.",actual_output=output,retrieval_context=context,expected_output="A cautious summary grounded in the supplied assessment, engagement, and completion evidence, with human-reviewed support actions.")

judge=NIMJudge(os.environ["NVIDIA_API_KEY"],os.getenv("NVIDIA_MODEL","meta/llama-3.1-8b-instruct"))
metrics=[
    FaithfulnessMetric(threshold=.7,model=judge,include_reason=True),
    AnswerRelevancyMetric(threshold=.7,model=judge,include_reason=True),
    ContextualRelevancyMetric(threshold=.7,model=judge,include_reason=True),
    GEval(name="AdvisorSupportQuality",criteria="Score whether the analysis is accurate to the supplied evidence, explains uncertainty, avoids unsupported causes, and proposes appropriate human-reviewed actions.",evaluation_params=[LLMTestCaseParams.INPUT,LLMTestCaseParams.ACTUAL_OUTPUT,LLMTestCaseParams.RETRIEVAL_CONTEXT],threshold=.7,model=judge),
]
results=[]
for metric in metrics:
    metric.measure(test_case)
    results.append({"metric":metric.__class__.__name__,"score":metric.score,"success":metric.success,"reason":getattr(metric,"reason",None)})
report={"student_code":student.student_code,"dataset":"synthetic demo profiles only","judge":judge.get_model_name(),"metrics":results,"warning":"One synthetic-record demonstration evaluation; not a statistically valid benchmark. No imported OULAD profile was sent to the external judge."}
with open("deepeval-results.json","w",encoding="utf-8") as file:
    json.dump(report,file,indent=2)
print(json.dumps(report,indent=2))
