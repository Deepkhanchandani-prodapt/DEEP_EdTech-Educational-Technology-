"""Optional Streamlit demonstration client for the Eduvantage FastAPI service.

Run from the repository root after starting the API:
    streamlit run frontend.py
"""
import os

import requests
import streamlit as st

st.set_page_config(page_title="Eduvantage AI", page_icon="🎓", layout="wide")
st.title("Eduvantage AI")
st.caption("Student Success Intelligence | Advisor review workspace")

if "token" not in st.session_state:
    st.session_state.token = ""
if "user" not in st.session_state:
    st.session_state.user = None

api_url = st.sidebar.text_input(
    "FastAPI URL", value=os.getenv("EDUVANTAGE_API_URL", "http://127.0.0.1:8000")
).rstrip("/")


def api(method, path, **kwargs):
    headers = kwargs.pop("headers", {})
    if st.session_state.token:
        headers["Authorization"] = f"Bearer {st.session_state.token}"
    try:
        response = requests.request(method, f"{api_url}{path}", headers=headers, timeout=45, **kwargs)
    except requests.RequestException as exc:
        st.error(f"Could not reach the API: {exc}")
        return None
    if not response.ok:
        try:
            detail = response.json().get("detail", response.text)
        except ValueError:
            detail = response.text
        st.error(f"API returned {response.status_code}: {detail}")
        return None
    if "text/csv" in response.headers.get("content-type", ""):
        return response.content
    if response.status_code == 204:
        return {}
    try:
        return response.json()
    except ValueError:
        return response.text


if not st.session_state.token:
    st.subheader("Sign in")
    login_tab, register_tab = st.tabs(["Login", "Create account"])
    with login_tab:
        with st.form("login"):
            email = st.text_input("Email", key="login_email")
            password = st.text_input("Password", type="password", key="login_password")
            login = st.form_submit_button("Sign in", type="primary")
        if login:
            result = api("POST", "/api/auth/login", json={"email": email, "password": password})
            if result and result.get("access_token"):
                st.session_state.token = result["access_token"]
                st.session_state.user = result.get("user", {})
                st.rerun()
    with register_tab:
        st.info("The first account registered in a fresh database becomes the initial administrator.")
        with st.form("register"):
            name = st.text_input("Name")
            new_email = st.text_input("Email address")
            new_password = st.text_input("Password (upper/lowercase, number, symbol)", type="password")
            institution = st.text_input("Institution")
            register = st.form_submit_button("Create account", type="primary")
        if register:
            result = api("POST", "/api/auth/register", json={
                "name": name, "email": new_email, "password": new_password,
                "institution": institution, "role": "ADVISOR",
            })
            if result and result.get("access_token"):
                st.session_state.token = result["access_token"]
                st.session_state.user = result.get("user", {})
                st.rerun()
    st.stop()

with st.sidebar:
    user = st.session_state.user or {}
    st.write(f"Signed in as **{user.get('name', user.get('email', 'Advisor'))}**")
    st.caption(user.get("role", ""))
    if st.button("Sign out"):
        api("POST", "/api/auth/logout")
        st.session_state.token = ""
        st.session_state.user = None
        st.rerun()

dashboard_tab, students_tab, assistant_tab, plans_tab = st.tabs(
    ["Dashboard", "Student profiles", "Support assistant", "Intervention plans"]
)

with dashboard_tab:
    st.subheader("Cohort overview")
    dashboard = api("GET", "/api/analytics/dashboard")
    if isinstance(dashboard, dict):
        st.json(dashboard)
    else:
        st.caption("Dashboard metrics are unavailable for this request.")
    courses = api("GET", "/api/courses")
    if courses:
        st.subheader("Course metrics")
        st.dataframe(courses if isinstance(courses, list) else courses.get("items", courses), use_container_width=True)

with students_tab:
    st.subheader("Search and prioritize student profiles")
    with st.form("student_filters"):
        col1, col2, col3 = st.columns(3)
        query = col1.text_input("Student ID contains", key="filter_query")
        course = col2.text_input("Course / presentation", placeholder="AAA · 2013J")
        risk = col3.selectbox("Risk", ["All", "LOW", "MODERATE", "HIGH", "CRITICAL"])
        col4, col5, col6 = st.columns(3)
        region = col4.text_input("Region")
        education = col5.text_input("Education")
        age_band = col6.text_input("Age band")
        find_students = st.form_submit_button("Apply filters", type="primary")
    if find_students or "student_results" not in st.session_state:
        params = {key: value for key, value in {
            "q": query, "course": course, "region": region, "education": education,
            "age_band": age_band, "level": "" if risk == "All" else risk,
            "limit": 100, "offset": 0,
        }.items() if value != ""}
        result = api("GET", "/api/students", params=params)
        if isinstance(result, dict):
            st.session_state.student_results = result.get("items", [])
            st.session_state.student_total = result.get("total", len(st.session_state.student_results))
    records = st.session_state.get("student_results", [])
    st.caption(f"{st.session_state.get('student_total', 0):,} matching profiles (first 100 shown)")
    if records:
        st.dataframe(records, use_container_width=True, hide_index=True)
        ids = [row.get("id", "") for row in records]
        selected = st.selectbox("Inspect student", ids)
        if selected and st.button("Load profile and agent analysis"):
            detail = api("GET", f"/api/students/{selected}")
            analysis = api("POST", "/api/agents/analyze", json={"student_code": selected})
            st.session_state.selected_detail = detail
            st.session_state.selected_analysis = analysis
        if st.session_state.get("selected_detail"):
            st.subheader("Student detail")
            st.json(st.session_state.selected_detail)
        if st.session_state.get("selected_analysis"):
            st.subheader("Performance, risk, and support analysis")
            st.json(st.session_state.selected_analysis)
    else:
        st.info("No matching profiles found. Clear filters or import the OULAD dataset.")

with assistant_tab:
    st.subheader("Ask about the cohort or a student")
    st.caption("Answers use available profile evidence. Review outputs before deciding on student support.")
    with st.form("chat"):
        message = st.text_area("Question", placeholder="Summarize performance and engagement trends for course AAA 2013J.")
        ask = st.form_submit_button("Ask assistant", type="primary")
    if ask and message.strip():
        answer = api("POST", "/api/assistant/chat", json={"message": message.strip()})
        if answer is not None:
            st.json(answer)

with plans_tab:
    st.subheader("Advisor-owned intervention plans")
    with st.form("new_plan"):
        plan_student = st.text_input("Student ID")
        plan_action = st.text_area("Support action")
        plan_status = st.selectbox("Status", ["Needs Attention", "Planned", "In Progress", "Completed"])
        create_plan = st.form_submit_button("Create plan", type="primary")
    if create_plan:
        created = api("POST", "/api/interventions", json={
            "student_code": plan_student, "action": plan_action, "status": plan_status,
        })
        if created:
            st.success("Intervention plan created.")
    plans = api("GET", "/api/interventions")
    if isinstance(plans, list) and plans:
        st.dataframe(plans, use_container_width=True, hide_index=True)
        plan_ids = [item["id"] for item in plans if "id" in item]
        if plan_ids:
            selected_plan = st.selectbox("Plan to edit or delete", plan_ids)
            current = next((item for item in plans if item.get("id") == selected_plan), {})
            with st.form("edit_plan"):
                updated_status = st.selectbox("Updated status", ["Needs Attention", "Planned", "In Progress", "Completed"], index=0)
                updated_action = st.text_area("Updated action", value=current.get("action", ""))
                save_plan = st.form_submit_button("Save changes")
            if save_plan:
                updated = api("PATCH", f"/api/interventions/{selected_plan}", json={
                    "status": updated_status, "action": updated_action,
                })
                if updated:
                    st.success("Plan updated. Refresh the page to view changes.")
            if st.button("Delete selected plan", type="secondary"):
                deleted = api("DELETE", f"/api/interventions/{selected_plan}")
                if deleted is not None:
                    st.success("Plan deleted. Refresh the page to view changes.")
    elif plans == []:
        st.info("No intervention plans are available for this account.")
