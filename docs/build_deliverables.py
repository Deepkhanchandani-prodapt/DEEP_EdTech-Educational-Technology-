"""Generate submission PDFs and the editable presentation deck.

Install docs/requirements-deliverables.txt, then run: python docs/build_deliverables.py
All generated files are written to deliverables/ at the repository root.
"""
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "deliverables"
OUT.mkdir(exist_ok=True)

from PIL import Image, ImageDraw, ImageFont
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.lib.pagesizes import A3, A4, landscape, letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (SimpleDocTemplate, Paragraph, Spacer, Table,
    TableStyle, PageBreak, Image as PdfImage, KeepTogether)
from reportlab.pdfgen import canvas as pdfcanvas
from pptx import Presentation
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.util import Inches, Pt

INK = colors.HexColor("#28251f")
GOLD = colors.HexColor("#a87d38")
MUTED = colors.HexColor("#756f66")
PAPER = colors.HexColor("#f4f0e8")
LINE = colors.HexColor("#e4dccf")
GREEN = colors.HexColor("#426a50")

font_candidates = [Path("C:/Windows/Fonts/arial.ttf"), Path("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf")]
bold_candidates = [Path("C:/Windows/Fonts/arialbd.ttf"), Path("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf")]
regular_font = next((p for p in font_candidates if p.exists()), None)
bold_font = next((p for p in bold_candidates if p.exists()), None)
if regular_font and bold_font:
    pdfmetrics.registerFont(TTFont("ProjectSans", str(regular_font)))
    pdfmetrics.registerFont(TTFont("ProjectSans-Bold", str(bold_font)))
    BODY, HEAVY = "ProjectSans", "ProjectSans-Bold"
else:
    BODY, HEAVY = "Helvetica", "Helvetica-Bold"

styles = getSampleStyleSheet()
styles.add(ParagraphStyle(name="CoverTitle", parent=styles["Title"], fontName=HEAVY, fontSize=27, leading=32, textColor=INK, alignment=TA_LEFT, spaceAfter=10))
styles.add(ParagraphStyle(name="DeckSubtitle", parent=styles["Normal"], fontName=BODY, fontSize=11, leading=16, textColor=MUTED, spaceAfter=14))
styles.add(ParagraphStyle(name="Section", parent=styles["Heading2"], fontName=HEAVY, fontSize=15, leading=19, textColor=INK, spaceBefore=11, spaceAfter=6, keepWithNext=True))
styles.add(ParagraphStyle(name="Subsection", parent=styles["Heading3"], fontName=HEAVY, fontSize=10.5, leading=14, textColor=GOLD, spaceBefore=7, spaceAfter=4, keepWithNext=True))
styles.add(ParagraphStyle(name="BodyProject", parent=styles["BodyText"], fontName=BODY, fontSize=9, leading=13.2, textColor=INK, spaceAfter=5))
styles.add(ParagraphStyle(name="SmallProject", parent=styles["BodyText"], fontName=BODY, fontSize=7.6, leading=10, textColor=MUTED, spaceAfter=3))
styles.add(ParagraphStyle(name="BulletProject", parent=styles["BodyText"], fontName=BODY, fontSize=8.7, leading=12.4, textColor=INK, leftIndent=13, firstLineIndent=-8, bulletIndent=1, spaceAfter=3))
styles.add(ParagraphStyle(name="Cell", parent=styles["BodyText"], fontName=BODY, fontSize=7.4, leading=9.5, textColor=INK))
styles.add(ParagraphStyle(name="CellHead", parent=styles["BodyText"], fontName=HEAVY, fontSize=7.6, leading=9.5, textColor=colors.white))

def para(text, style="BodyProject"):
    return Paragraph(text, styles[style])

def bullets(items):
    return [Paragraph("• " + item, styles["BulletProject"]) for item in items]

def make_table(rows, widths, header=True):
    data=[]
    for ri,row in enumerate(rows):
        data.append([para(str(v), "CellHead" if header and ri==0 else "Cell") for v in row])
    table=Table(data,colWidths=widths,repeatRows=1 if header else 0,hAlign="LEFT")
    table.setStyle(TableStyle([
        ("BACKGROUND",(0,0),(-1,0),colors.HexColor("#353128")) if header else ("BACKGROUND",(0,0),(-1,-1),colors.white),
        ("ROWBACKGROUNDS",(0,1 if header else 0),(-1,-1),[colors.white,colors.HexColor("#faf7f1")]),
        ("GRID",(0,0),(-1,-1),0.35,LINE), ("VALIGN",(0,0),(-1,-1),"TOP"),
        ("LEFTPADDING",(0,0),(-1,-1),6), ("RIGHTPADDING",(0,0),(-1,-1),6),
        ("TOPPADDING",(0,0),(-1,-1),5), ("BOTTOMPADDING",(0,0),(-1,-1),5),
    ]))
    return table

def footer(canvas, doc):
    canvas.saveState()
    w,h=doc.pagesize
    canvas.setStrokeColor(LINE); canvas.line(18*mm,14*mm,w-18*mm,14*mm)
    canvas.setFont(BODY,7); canvas.setFillColor(MUTED)
    canvas.drawString(18*mm,9*mm,"Eduvantage AI | Student Success Intelligence")
    canvas.drawRightString(w-18*mm,9*mm,f"Page {doc.page}")
    canvas.restoreState()

def build_architecture_image():
    # Three aligned rows make the complete flow legible at both slide and PDF scale.
    W,H=2000,1510
    img=Image.new("RGB",(W,H),(247,244,237)); d=ImageDraw.Draw(img)
    regular=ImageFont.truetype(str(regular_font),20) if regular_font else ImageFont.load_default()
    small=ImageFont.truetype(str(regular_font),16) if regular_font else ImageFont.load_default()
    bold=ImageFont.truetype(str(bold_font),23) if bold_font else ImageFont.load_default()
    title=ImageFont.truetype(str(bold_font),43) if bold_font else ImageFont.load_default()
    ink="#29251f"; muted_ink="#70695f"; line="#896f46"
    d.text((58,34),"EDUVANTAGE AI  |  SYSTEM ARCHITECTURE",font=title,fill=ink)
    d.text((61,91),"OULAD data flows through local retrieval and advisor-reviewed analysis; optional services are identified explicitly.",font=regular,fill=muted_ink)

    def wrapped(text,font,max_width):
        words=text.split(); rows=[]; current=""
        for word in words:
            candidate=(current+" "+word).strip()
            if current and d.textbbox((0,0),candidate,font=font)[2] > max_width:
                rows.append(current); current=word
            else: current=candidate
        if current: rows.append(current)
        return rows

    def box(x,y,w,h,heading,lines,fill="#fffdf9",accent="#a87d38",tag=None):
        d.rounded_rectangle((x,y,x+w,y+h),radius=18,fill=fill,outline="#d9d1c5",width=3)
        d.rounded_rectangle((x,y,x+9,y+h),radius=5,fill=accent)
        d.text((x+23,y+18),heading,font=bold,fill=ink)
        cy=y+60
        for item in lines:
            for row in wrapped(item,small,w-48):
                d.text((x+24,cy),row,font=small,fill=muted_ink); cy+=25
            cy+=3
        if tag:
            tw=d.textbbox((0,0),tag,font=small)[2]
            d.rounded_rectangle((x+w-tw-40,y+h-37,x+w-13,y+h-10),radius=8,fill="#f0ece4")
            d.text((x+w-tw-27,y+h-34),tag,font=small,fill=muted_ink)

    def arrow(points,label=None,dashed=False,color=line,width=5,label_at=None):
        import math
        for start,end in zip(points,points[1:]):
            x1,y1=start; x2,y2=end
            if dashed:
                dist=math.hypot(x2-x1,y2-y1); ux=(x2-x1)/dist; uy=(y2-y1)/dist
                step=20; dash=11; offset=0
                while offset<dist:
                    stop=min(offset+dash,dist)
                    d.line((x1+ux*offset,y1+uy*offset,x1+ux*stop,y1+uy*stop),fill=color,width=width)
                    offset+=step
            else: d.line((x1,y1,x2,y2),fill=color,width=width)
        x1,y1=points[-2]; x2,y2=points[-1]
        ang=math.atan2(y2-y1,x2-x1); length=19
        d.polygon([(x2,y2),(x2-length*math.cos(ang-.48),y2-length*math.sin(ang-.48)),(x2-length*math.cos(ang+.48),y2-length*math.sin(ang+.48))],fill=color)
        if label:
            lx,ly=label_at or ((points[0][0]+points[-1][0])//2,(points[0][1]+points[-1][1])//2-24)
            bb=d.textbbox((0,0),label,font=small); pad=7
            d.rounded_rectangle((lx-pad,ly-pad,lx+bb[2]+pad,ly+bb[3]+pad),radius=6,fill="#f7f4ed")
            d.text((lx,ly),label,font=small,fill=muted_ink)

    # The first four stages move left to right; the next four return right to left.
    # The final row resumes left to right and terminates at the advisor review point.
    x_top=[55,545,1035,1525]; x_mid=[1525,1035,545,55]; x_bottom=[55,545,1035]
    node_w=420; node_h=205; y_top=205; y_mid=510; y_bottom=815
    stages=[
        ("01  Source data",["OULAD CSV tables","Assessments, registration, VLE activity"],"#f8f1e4","#a87d38"),
        ("02  Preprocessing",["Stream large activity file; join source tables","Aggregate features; repeatable profile upsert"],"#edf2eb","#426a50"),
        ("03  Profile unit",["One student × module × presentation","Assessment, engagement and outcome fields"],"#fffdf9","#a87d38"),
        ("04  Local vectors",["TF-IDF text features + TruncatedSVD / LSA","Structured numeric and category features"],"#edf2eb","#426a50"),
        ("05  Vector database",["Not implemented in this version","Bypassed; no vector store"],"#efede9","#9c958b"),
        ("06  Retrieval",["BM25 + local semantic + structured similarity","Metadata filters; similar profile evidence"],"#edf2eb","#426a50"),
        ("07  RAG / language model",["Retrieved evidence grounds the analysis","Optional NVIDIA NIM prose; deterministic fallback"],"#f0ebf3","#75648c"),
        ("08  Analysis agents",["Performance → risk → support workflow","Sequential roles share evidence in process"],"#f8f1e4","#a87d38"),
        ("09  API layer",["FastAPI routes and Pydantic validation","Student/course scope checks; aggregate-only analyst routes"],"#f8f1e4","#a87d38"),
        ("10  Role-aware interface",["React + Vite pages change by role","Optional Streamlit demonstration client"],"#eee5d4","#a87d38"),
        ("11  Advisor oversight",["Review assigned evidence and similar cases","Create or edit support plans; give feedback"],"#e9efe6","#426a50"),
    ]
    coords=[(x,y_top) for x in x_top]+[(x,y_mid) for x in x_mid]+[(x,y_bottom) for x in x_bottom]
    for i,(heading,lines,fill,accent) in enumerate(stages):
        box(*coords[i],node_w,node_h,heading,lines,fill,accent,"NOT USED" if i==4 else None)

    # Draw connectors first, so arrowheads meet card edges cleanly.
    for i in range(3):
        x=x_top[i]+node_w; arrow([(x+5,y_top+node_h//2),(x_top[i+1]-8,y_top+node_h//2)])
    # The absent vector DB is explicitly bypassed: vector features go straight to retrieval.
    arrow([(x_top[3]+node_w//2,y_top+node_h+4),(x_top[3]+node_w//2,y_mid-32),(x_mid[1]+node_w//2,y_mid-32),(x_mid[1]+node_w//2,y_mid-9)],"local features → in-process ranking",label_at=(1290,463))
    for j in range(1,3):
        x=x_mid[j]; arrow([(x-6,y_mid+node_h//2),(x_mid[j+1]+node_w+8,y_mid+node_h//2)])
    arrow([(x_mid[3]+node_w//2,y_mid+node_h+4),(x_mid[3]+node_w//2,y_bottom-9)],"analysis",label_at=(x_mid[3]+node_w//2+14,770))
    for j in range(2):
        x=x_bottom[j]+node_w; arrow([(x+5,y_bottom+node_h//2),(x_bottom[j+1]-8,y_bottom+node_h//2)])

    # Data persistence is a supporting service connected directly to the API.
    support_y=1190
    box(55,support_y,900,190,"PERSISTENCE  |  SQLAlchemy",["SQLite local default; PostgreSQL supported","Profiles · users · intervention plans · feedback · audit events"],"#eaf0f3","#54748a")
    # API node is at x=55. The offset connector keeps its entry distinct from the user flow.
    arrow([(x_bottom[0]+node_w//2,y_bottom+node_h+5),(x_bottom[0]+node_w//2,support_y-35)],"read / write",label_at=(x_bottom[0]+node_w//2+15,1100))
    arrow([(x_bottom[2]+node_w//2,y_bottom+node_h+4),(x_bottom[2]+node_w//2,1160),(900,1160),(900,support_y-9)],"plans & feedback",label_at=(1010,1127))

    box(1035,support_y,910,190,"EVALUATION & SAFEGUARDS",["40-query retrieval benchmark: P@5 / MRR; same-course label is a weak proxy","DeepEval and RAGAS: not run; scores are not reported","Human review · JWT / RBAC · validation · audit trail"],"#fffdf9","#426a50")
    # Route the offline benchmark around the outer edge so it does not cross advisor flow.
    arrow([(x_top[3]+node_w//2,y_top+node_h+4),(x_top[3]+node_w//2,465),(1970,465),(1970,1160),(1490,1160),(1490,support_y-9)],"offline retrieval evaluation",dashed=True,color="#66806b",label_at=(1515,1127))

    d.text((58,1435),"Primary flow is numbered. Gray card marks an absent vector store. Dashed arrow marks offline evaluation; advisors retain control of student decisions.",font=small,fill=muted_ink)
    path=OUT/"architecture-diagram.jpg"; img.save(path,quality=94)
    return path

arch_img=build_architecture_image()

def pdf_doc(filename,title,subtitle,story,pagesize=A4):
    doc=SimpleDocTemplate(str(OUT/filename),pagesize=pagesize,rightMargin=18*mm,leftMargin=18*mm,topMargin=19*mm,bottomMargin=19*mm,title=title,author="Eduvantage AI Capstone Team")
    doc.build(story,onFirstPage=footer,onLaterPages=footer)

# Architecture PDF (diagram is also provided as a high-resolution JPEG).
arch_story=[para("System Architecture", "CoverTitle"),para("Eduvantage AI · Student Success Intelligence", "DeckSubtitle"),PdfImage(str(arch_img),width=260*mm,height=196.3*mm),Spacer(1,3*mm),para("Numbered arrows show the end-to-end path and advisor handoff. SQL persistence is a supporting service connected to the API; evaluation is an offline side path. Gray stages are not implemented. NVIDIA NIM is optional and server-side; credentials remain in backend/.env.","SmallProject")]
pdf_doc("architecture-diagram.pdf","Eduvantage AI Architecture","Local-first architecture diagram",arch_story,landscape(A3))

# Design document PDF.
design=[para("Design Document", "CoverTitle"),para("Eduvantage AI · Student Success Intelligence · Version 1.0 · 6 October 2026", "DeckSubtitle"),
para("1. Purpose and scope","Section"),para("An advisor-facing student-success prototype that organizes historical academic and learning-activity evidence, similarity search, screening indicators, and human-owned support plans. The system is decision support, not an automated enrollment, grading, or intervention decision maker."),
para("2. Users and workflows","Section"),*bullets(["Advisors and faculty review student-course profiles, apply cohort filters, inspect evidence, ask the assistant, and maintain intervention plans.","Administrators manage data and workspace operations; analysts inspect course trends, model estimates, exports, and evaluation notes.","Main workflow: authenticate → dashboard → filter/prioritize → inspect profile and similar cases → review recommendation → record plan → submit feedback."]),
para("3. Architecture and components","Section"),para("React/Vite provides the browser UI. FastAPI provides REST endpoints, Pydantic validation, authentication and role enforcement. SQLAlchemy persists user, student, intervention, feedback, and audit tables to SQLite locally or PostgreSQL by DATABASE_URL. Local retrieval and deterministic scoring run in the backend; optional NVIDIA NIM prose and judging run server-side."),PdfImage(str(arch_img),width=170*mm,height=94.5*mm),
para("4. Data model and processing","Section"),para("The OULAD importer creates one student × module × presentation record. It joins studentInfo, studentRegistration, studentAssessment, assessments, studentVle, vle, and courses. It streams the large activity CSV, aggregates clicks and active weeks, derives assessment means/trends and completion, then upserts records idempotently. See dataset-details.pdf and dataset-details.md for counts and assumptions."),
para("5. Retrieval, agents, and scoring","Section"),para("Hybrid case retrieval blends BM25 keyword ranking with local TF-IDF/TruncatedSVD semantic text and structured feature similarity. Metadata filters can constrain module/presentation, region, education, age band, credits, and previous attempts. A shortlist reduces latent fitting cost. Three deterministic agents report performance, risk factors, and suggested advisor actions. Optional NIM produces evidence-constrained prose and a separate judge; numeric risk fields stay deterministic."),
para("6. Prediction and feedback","Section"),para("A RandomForestRegressor estimates assessment score and a RandomForestClassifier estimates withdrawal label from available profile features. Holdout metrics are calculated on local records. Advisors can submit feedback; the current system stores ratings for review but does not automatically retrain from feedback."),
para("7. Security, privacy, and oversight","Section"),*bullets(["Password hashing, signed expiring JWT bearer tokens, role checks, request validation, and audit events.","The NVIDIA key is configured in ignored backend/.env and is never sent to the frontend.","OULAD IDs are anonymized; row-level education data still requires controlled access and institutional governance.","Risk scores are heuristic indicators, not calibrated probabilities or causal explanations. Human review is required."]),
para("8. Limitations and next work","Section"),para("The benchmark uses same-course membership as a weak relevance label; keyword-only currently exceeds the hybrid score. Models lack external validation, calibration, subgroup fairness review, and prospective evidence. DeepEval output is pending. Next steps are advisor-labeled retrieval relevance data, repeatable API regression tests, institutional privacy/security review, and prospective model evaluation before any real operational use.")]
design += [
para("9. Technology selection and justification", "Section"),
make_table([["Technology", "Selection and rationale"], ["Language / API", "Python 3.11+, FastAPI, Pydantic, Uvicorn for typed REST validation and data/ML ecosystem."], ["UI / database", "React 18 + Vite primary site; optional Streamlit demo client. SQLAlchemy with SQLite locally and PostgreSQL as an option."], ["LLM", "Optional NVIDIA NIM using configured NVIDIA_MODEL. It drafts evidence-grounded prose and judge feedback; deterministic core remains available."], ["Semantic representation", "Local TF-IDF + TruncatedSVD/LSA, not a pretrained embedding model. No vector database is used; candidates are ranked in process."], ["ML", "scikit-learn random-forest demonstrations and local retrieval evaluation."]], [31*mm, 143*mm]),
para("10. Retrieval strategy and RAG boundaries", "Section"),
para("The retrieval document is one structured student × module × presentation profile. The importer streams and aggregates the source tables; it does not split prose into overlapping token chunks. Retrieval applies course/presentation, region, education, age-band, credits, and attempts filters, then combines BM25 keyword relevance, local TF-IDF/LSA text similarity, and structured feature similarity. Selected cases ground the analysis workflow. No pretrained embedding endpoint or vector store exists in this version."),
para("11. Agent roles and communication", "Section"),
para("The performance analyst summarizes assessment and activity evidence; the risk assessor assigns a heuristic band and factors; the intervention recommender proposes human-reviewed actions using prior outputs and retrieved cases. FastAPI calls these roles sequentially in one request, passing typed dictionaries/results in process. Optional NIM prose/judging is supplemental and cannot change deterministic numeric risk fields."),
para("12. Evaluation strategy and current metrics", "Section"),
para("The 40-query retrieval benchmark reports Precision@5 and MRR against same-course membership as a weak relevance proxy: hybrid 0.450 / 0.681; semantic-only 0.395 / 0.617; keyword-only 0.475 / 0.729. The proxy currently favors keyword-only. Optional DeepEval covers faithfulness, answer relevance, context relevance, and custom support quality, but no aggregate DeepEval run is included. Manual sample cases are in docs/sample-test-cases.md. Do not claim pending evaluation as a result."),
para("13. Local deployment requirement", "Section"),
para("Run the backend with FastAPI/Uvicorn from backend/ (`uvicorn app.main:app --reload`). Run the full React/Vite interface from frontend/ (`npm run dev`) or the optional Streamlit demo from the repository root (`streamlit run frontend.py`). Both call the same API. Python dependencies are listed in backend/requirements.txt. Environment and API-key setup is in README.md; secrets stay out of source control."),
para("14. Challenges, trade-offs, and limitations", "Section"),
para("Streaming makes the 10.6M-row VLE import practical on a local machine. Local TF-IDF/LSA avoids an external embedding service, but it is less semantically general than a pretrained encoder. No vector DB avoids infrastructure, but in-process ranking is less scalable. Historical model estimates are not operationally validated; feedback is stored but does not automatically retrain models. Risk indicators require human review."),
para("15. Persistent role scopes", "Section"),
para("A user_access table stores advisor student grants and faculty course grants. Registration does not accept user-selected roles; an administrator assigns roles and scopes. Server-side queries constrain individual record operations and student CSV exports. Analysts receive aggregate reports only. Administrators can update roles and grant or revoke scopes from the UI; changes persist across application restarts.")]
pdf_doc("design-document.pdf","Eduvantage AI Design Document","Architecture, data, analysis, safeguards and limitations",design)

# Dataset details PDF.
dataset=[para("Dataset Details", "CoverTitle"),para("Open University Learning Analytics Dataset (OULAD) · Local project import", "DeckSubtitle"),
para("Source and local use","Section"),para("The supplied OULAD.names file describes data about students, course presentations, assessments, and VLE interactions. The local importer creates 32,593 student-course-presentation profiles. Course presentation suffixes B and J are described in the source documentation as February and October presentations. Official project information: analyse.kmi.open.ac.uk/open_dataset. Citation: Kuzilek, Hlosta & Zdrahal, Scientific Data 4, 170171 (2017), doi:10.1038/sdata.2017.171."),
para("Format and purpose","Section"),para("Seven comma-separated CSV tables with header rows. They are used here to build historical student-course profiles for academic and engagement trend review, metadata filtering, similarity search, risk-screening demonstrations, and support suggestions."),
make_table([["CSV file","Local rows","Imported use"],["studentInfo.csv","32,593","Student demographics, education, credits, attempts, final result"],["studentRegistration.csv","32,593","Registration / withdrawal dates"],["studentAssessment.csv","173,912","Assessment submissions, scores, banking flags"],["assessments.csv","206","Assessment schedule, type, weight and join IDs"],["studentVle.csv","10,655,280","Student VLE clicks by site/day; streamed and aggregated"],["vle.csv","6,364","Site metadata and activity type"],["courses.csv","22","Module-presentation durations"]],[42*mm,26*mm,106*mm]),
para("Key field names","Section"),para("Student/course keys: id_student, code_module, code_presentation. Filters: region, highest_education, age_band, studied_credits, num_of_prev_attempts. Assessment: id_assessment, date_submitted, score, is_banked, weight. Activity: id_site, date, sum_click, activity_type. Course metadata: module_presentation_length. These source columns are joined and aggregated into the profile fields below."),
para("Import command","Section"),para("From backend/: python scripts/ingest_oulad.py ../open+university+learning+analytics+dataset. Import is repeatable and refreshes matching IDs instead of duplicating them."),
para("Derived fields","Section"),*bullets(["Assessment score: mean of available scored submissions (unweighted). Score trend: later-half mean minus earlier-half mean when both exist.","Activity: total clicks, active weeks and relative click change between halves of observed activity days.","Completion: fraction of presentation assessments with a scored submission. Outcome and source metadata are retained.","Student identifiers are combined with module/presentation so repeated learners remain distinct by course presentation."]),
para("Important limitations","Section"),*bullets(["Assessment average is not an official weighted module mark; assessment weights are not applied by the importer.","VLE clicks indicate recorded activity only, not comprehension, effort, or causation.","The local release has its own measured row counts; do not substitute counts from a different OULAD release.","Treat anonymized student-level rows as sensitive. Follow source license and institutional data-governance rules before redistribution or operational use."]),
para("Reference","Section"),para("Official dataset page: https://analyse.kmi.open.ac.uk/open_dataset · Publication DOI: https://doi.org/10.1038/sdata.2017.171")]
pdf_doc("dataset-details.pdf","OULAD Dataset Details","Local data inventory, joins, derived features and cautions",dataset)

# Evaluation artifacts: measured retrieval results, pending judge evaluations, test cases, and a synthetic sample.
evaluation_story=[
para("Evaluation Artifacts", "CoverTitle"),
para("Measured retrieval results, transparent evaluation status, test cases, and sample outputs", "DeckSubtitle"),
para("Retrieval benchmark — 40 queries", "Section"),
para("Relevance is labeled by same-course membership, a weak proxy rather than advisor relevance judgments. The local release includes synthetic/default data; interpret these scores as exploratory."),
make_table([["Retrieval mode","Precision@5","MRR"],["Hybrid keyword + TF-IDF/LSA + structured","0.450","0.681"],["Semantic-only","0.395","0.617"],["Keyword-only","0.475","0.729"]],[89*mm,42*mm,42*mm]),
para("Interpretation", "Subsection"),
para("Keyword-only ranks best under this proxy. The result does not establish that hybrid retrieval is superior. Same-course membership can mark profiles relevant even when individual records are not meaningfully similar. See backend/retrieval-evaluation.json for the saved result."),
para("DeepEval scores", "Section"),
para("Status: NOT RUN; no DeepEval scores are reported. An optional script evaluates Faithfulness, Answer Relevancy, Contextual Relevancy, and custom advisor-support quality using NVIDIA NIM. It is restricted to synthetic profiles. One-record outputs are demonstrations, not representative metrics."),
para("RAGAS scores", "Section"),
para("Status: NOT RUN; no RAGAS integration or scores are available. Do not treat missing scores as zero or invent values. A run needs a question/context/answer/reference dataset and a configured judge provider."),
para("Test cases", "Section"),
para("Twenty manual acceptance cases are provided in docs/sample-test-cases.md. They cover authentication and validation, filters, prioritization, similarity, analysis, intervention CRUD, feedback, role controls, ingestion, exports, and provider fallback. These are documented cases, not an automated test pass report."),
para("Sample outputs", "Section"),
para("deliverables/sample-outputs.json is a deterministic analysis response generated from seeded synthetic profiles only, without an NVIDIA/NIM call. It includes performance evidence, heuristic risk factors, retrieved examples, advisor suggestions, and limitations. Regenerate from backend/ with python scripts/generate_sample_output.py."),
para("Reproducibility and limitations", "Section"),
para("From backend/, run python scripts/evaluate_retrieval.py to refresh the offline ranking file. To generate optional DeepEval scores, install requirements-evaluation.txt, configure NVIDIA_API_KEY and NVIDIA_MODEL in ignored backend/.env, then run python scripts/evaluate_quality.py. Use only synthetic data for external judge calls. Retrieval labels and one-record evaluations are insufficient for operational or safety claims; obtain advisor-labeled judgments and institutional review."),
]
pdf_doc("evaluation-artifacts.pdf","Eduvantage AI Evaluation Artifacts","Results, score status, cases, and samples",evaluation_story)

# API documentation PDF.
api_story=[para("API Reference", "CoverTitle"),para("FastAPI REST service · Interactive Swagger UI at http://127.0.0.1:8000/docs · OpenAPI JSON at /openapi.json", "DeckSubtitle"),
para("Authentication","Section"),make_table([["Method","Path","Purpose"],["POST","/api/auth/register","Create account; first account becomes administrator"],["POST","/api/auth/login","Password login; returns bearer token"],["POST","/api/auth/google","Google credential verification when configured"],["POST / GET / PATCH","/api/auth/logout · /me","Logout event; profile read/update"]],[32*mm,54*mm,88*mm]),
para("Students and analytics","Section"),make_table([["Method","Path","Purpose"],["GET","/api/students","Search, filter, sort and paginate profiles"],["POST / PATCH / DELETE","/api/students[/{code}]","Create / update / delete (administrator for mutations)"],["GET","/api/students/{code}","Student details, timeline, recommendations"],["GET","/api/students/{code}/similar","Hybrid historical retrieval with metadata constraints"],["GET","/api/analytics/dashboard","Cohort stats, course trends, risk and intervention pipeline"],["GET","/api/courses","Course-level analytics"],["GET","/api/models/predict/{code}","Random forest demo predictions and holdout metrics"]],[32*mm,57*mm,85*mm]),
para("Assistant and support","Section"),make_table([["Method","Path","Purpose"],["POST","/api/assistant/chat","Cohort question or student-ID analysis"],["POST","/api/agents/analyze","Performance/risk/support agents, similar cases, optional NIM summary/judge"],["POST","/api/recommendations","Advisor support suggestions for a student"],["GET / POST","/api/interventions","List/create plans"],["PATCH / DELETE","/api/interventions/{id}","Update/delete plan (owner/admin rules)"],["POST","/api/feedback","Save advisor rating/comment"],["GET","/api/analytics/evaluation","Feedback/evaluation configuration summary"]],[32*mm,57*mm,85*mm]),
para("Administration and utilities","Section"),make_table([["Method","Path","Purpose"],["POST","/api/admin/ingest","Admin CSV metadata import; upload size cap applies"],["GET","/api/admin/audit","Administrator audit log"],["GET","/api/export/students.csv","Download student CSV"],["GET","/api/students/export.csv","Alternate CSV export"],["GET","/api/health","Unauthenticated service health"]],[32*mm,57*mm,85*mm]),
para("Auth, validation, and full schema","Section"),para("Attach Authorization: Bearer <access_token> to protected routes. Input validation errors return 422; missing/invalid credentials return 401; role denial returns 403. Complete request/response models and parameters are exported to openapi.json. The backend also serves Swagger UI at /docs and ReDoc at /redoc.")]
api_story += [
para("Sample request / response: authentication", "Section"),
para("Request: POST /api/auth/login with JSON {email, password}. Response: {access_token, token_type: bearer, user: {name, email, role}}. Use the returned token as Authorization: Bearer &lt;access_token&gt; for protected calls."),
para("Sample request / response: student filtering", "Section"),
para("Request: GET /api/students?course=AAA%20%C2%B7%202013J&amp;level=HIGH&amp;limit=2&amp;offset=0 with a bearer token. Response: {items: [student profile objects], total: count, limit: 2, offset: 0}. Each profile includes score, clicks, risk score/band, completion, trends, and priority score."),
para("Sample request / response: agent analysis", "Section"),
para("Request: POST /api/agents/analyze with JSON {student_code: OU00001_AAA_2013J}. Response includes summary, performance_analysis, risk_analysis, support_recommendation, agent_workflow, retrieved_cases, evidence, key_factors, and optional judge status."),
para("Sample request / response: assistant", "Section"),
para("Request: POST /api/assistant/chat with JSON {message: Summarize the performance and engagement trends for course AAA 2013J}. Response includes summary, agent_workflow, evidence, similar_cases, recommended_intervention, limitations, and optional judge status."),
para("Sample request / response: intervention CRUD", "Section"),
para("Create with POST /api/interventions and JSON {student_code, action, status}. Response includes {id, student_code, status, action}. Update with PATCH /api/interventions/{id}; delete with DELETE /api/interventions/{id}. Ownership or administrator permissions apply."),
para("Role-scoped access management", "Section"),
para("The first account in an empty database is administrator; later registrations are advisors and cannot set their own role. GET /api/admin/users lists accounts and grants; PATCH /api/admin/users/{user_id} changes a role; POST /api/admin/access grants an advisor student ID or faculty course; DELETE /api/admin/access/{grant_id} revokes it. These changes are stored in the database. Advisor and faculty data is limited to grants; administrators see workspace records. GET /api/analytics/reports.csv returns course aggregates within the signed-in account scope (analysts receive cohort aggregates). Analysts cannot access student-level reports or identifiable endpoints."),
para("All other request and response schemas", "Section"),
para("The endpoint inventory above covers all application routes, including Google authentication, profile CRUD, analytics, CSV, predictions, feedback, administration, and health. Exact required fields, parameter bounds, response media types, and validation schemas are available in deliverables/openapi.json and the running Swagger UI at /docs.")]
pdf_doc("api-reference.pdf","Eduvantage AI API Reference","Route index and authentication conventions",api_story)

# Presentation content and editable PPTX.
slides=[
 ("Eduvantage AI","Student Success Intelligence","Capstone project | advisor-facing evidence and support workflow"),
 ("Problem and business need","Assessment, registration, and learning-activity signals are spread across records.","Advisors need a reviewable way to prioritize follow-up and understand the evidence behind a concern."),
 ("Solution overview","One workspace for cohort analytics, student profiles, historical search, recommendations, plans, and feedback.","The system organizes evidence; advisors retain decision authority."),
 ("Architecture","OULAD -> streaming preprocessing -> profiles -> local TF-IDF/LSA -> in-process retriever","FastAPI orchestrates analysis; React/Vite presents it. No pretrained embedding service or vector DB is used."),
 ("Data flow","CSV -> joins and aggregation -> student-course-presentation profile -> filtered retrieval -> advisor UI","The VLE event file is streamed; local import contains 32,593 aggregated profiles."),
 ("Technology stack","Python / FastAPI / Pydantic / SQLAlchemy / scikit-learn / React / Vite / Streamlit","SQLite default; PostgreSQL supported. Optional NVIDIA NIM uses a server-side key."),
 ("Role-based access","Admin manages accounts and grants; faculty scope is by course; advisor scope is by student.","Analysts see aggregate reports only. Roles and grants persist in the database and are enforced by the API."),
 ("Agent workflow","Performance analysis -> risk assessment -> support recommendation","Sequential in-process roles share evidence through the API orchestrator; an advisor reviews suggested actions."),
 ("Demo walkthrough","Sign in -> filter cohort -> inspect a profile -> ask assistant -> create/edit a plan","Use React at 127.0.0.1:5173 or Streamlit at localhost:8501; API docs at 127.0.0.1:8000/docs."),
 ("Evaluation results","40-query retrieval: hybrid P@5 0.450 / MRR 0.681; keyword P@5 0.475 / MRR 0.729","Same-course relevance is a weak proxy. DeepEval aggregate report is pending; do not claim unrun metrics."),
 ("Challenges and learnings","Local retrieval improves deployment simplicity but has no indexed vector store or pretrained semantic encoder.","Need advisor-labeled retrieval judgments, model calibration/fairness review, and institutional privacy review before operational use.")]

prs=Presentation(); prs.slide_width=Inches(13.333); prs.slide_height=Inches(7.5)
def rgb(h): return RGBColor.from_string(h.strip('#'))
for idx,(heading,body,foot) in enumerate(slides):
    slide=prs.slides.add_slide(prs.slide_layouts[6])
    bg=slide.background.fill; bg.solid(); bg.fore_color.rgb=rgb("F4F0E8")
    rect=slide.shapes.add_shape(MSO_SHAPE.RECTANGLE,0,0,Inches(.18),prs.slide_height); rect.fill.solid();rect.fill.fore_color.rgb=rgb("A87D38");rect.line.fill.background()
    tx=slide.shapes.add_textbox(Inches(.75), Inches(.55), Inches(11.8), Inches(.5)).text_frame
    p=tx.paragraphs[0];p.text=f"EDUVANTAGE AI     /     CAPSTONE PRESENTATION";p.font.name="Aptos";p.font.size=Pt(10);p.font.bold=True;p.font.color.rgb=rgb("A87D38")
    hbox=slide.shapes.add_textbox(Inches(.75), Inches(1.45), Inches(11.8), Inches(1.0)).text_frame
    p=hbox.paragraphs[0];p.text=heading;p.font.name="Aptos Display";p.font.size=Pt(32 if idx else 36);p.font.bold=True;p.font.color.rgb=rgb("29251F")
    card=slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE,Inches(.75), Inches(2.7), Inches(11.85), Inches(2.35))
    card.fill.solid();card.fill.fore_color.rgb=rgb("FFFDF9");card.line.color.rgb=rgb("E4DCCF")
    tf=card.text_frame;tf.clear();tf.margin_left=Inches(.35);tf.margin_right=Inches(.35);tf.margin_top=Inches(.28);tf.vertical_anchor=MSO_ANCHOR.MIDDLE
    p=tf.paragraphs[0];p.text=body;p.font.name="Aptos";p.font.size=Pt(23 if idx==0 else 20);p.font.color.rgb=rgb("29251F");p.font.bold=True
    p=tf.add_paragraph();p.text="\n"+foot;p.font.name="Aptos";p.font.size=Pt(14);p.font.color.rgb=rgb("756F66")
    footerbox=slide.shapes.add_textbox(Inches(.75), Inches(6.7), Inches(11.8), Inches(.35)).text_frame
    p=footerbox.paragraphs[0];p.text=f"Eduvantage AI  ·  {idx+1:02d} / {len(slides):02d}";p.font.name="Aptos";p.font.size=Pt(9);p.font.color.rgb=rgb("756F66")
    if idx==3:
        slide.shapes.add_picture(str(arch_img), Inches(8.15), Inches(3.75), width=Inches(3.9))
prs.save(OUT/"presentation.pptx")

# A matching PDF slide deck, exactly one landscape page per slide.
deck_path=OUT/"presentation.pdf"
pw,ph=landscape(A4)
c=pdfcanvas.Canvas(str(deck_path),pagesize=(pw,ph),pageCompression=1)
for idx,(heading,body,foot) in enumerate(slides):
    c.setFillColor(colors.HexColor("#f4f0e8"));c.rect(0,0,pw,ph,fill=1,stroke=0)
    c.setFillColor(colors.HexColor("#a87d38"));c.rect(0,0,4*mm,ph,fill=1,stroke=0)
    c.setFont(HEAVY,9);c.drawString(18*mm,ph-18*mm,"EDUVANTAGE AI  /  CAPSTONE PRESENTATION")
    c.setFillColor(INK);c.setFont(HEAVY,27);c.drawString(18*mm,ph-43*mm,heading)
    c.setFillColor(colors.white);c.setStrokeColor(LINE);c.roundRect(18*mm,ph-115*mm,pw-36*mm,54*mm,5*mm,fill=1,stroke=1)
    if idx==3:
        c.setFillColor(INK);c.setFont(HEAVY,15)
        for j,line in enumerate(["React/Vite → FastAPI → SQLAlchemy", "SQLite / PostgreSQL", "OULAD streaming import · optional NVIDIA NIM"]):
            c.drawString(27*mm,ph-(79+j*13)*mm,line)
        c.drawImage(str(arch_img),pw-133*mm,ph-111*mm,width=104*mm,height=58*mm,preserveAspectRatio=True,anchor="c",mask="auto")
    else:
        c.setFillColor(INK);c.setFont(HEAVY,17)
        lines=[]
        for paragraph in (body,foot):
            words=paragraph.split(); line=""
            for word in words:
                candidate=(line+" "+word).strip()
                if pdfmetrics.stringWidth(candidate,HEAVY if not lines else BODY,17 if not lines else 13)>pw-62*mm:
                    lines.append(line);line=word
                else:line=candidate
            if line:lines.append(line)
            lines.append("")
        y=ph-79*mm
        for j,line in enumerate(lines):
            if line:
                c.setFont(HEAVY if j==0 else BODY,17 if j==0 else 13)
                c.drawString(27*mm,y,line)
            y-=9*mm if j==0 else 7*mm
    c.setFillColor(MUTED);c.setFont(BODY,9);c.drawString(18*mm,12*mm,f"Eduvantage AI  |  {idx+1:02d} / {len(slides):02d}")
    c.showPage()
c.save()

print("Generated deliverables:")
for p in sorted(OUT.iterdir()):
    if p.is_file(): print(f"- {p.name} ({p.stat().st_size:,} bytes)")
