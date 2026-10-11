# API Documentation

FastAPI serves Swagger UI at `http://127.0.0.1:8000/docs`, ReDoc at `/redoc`, and the full machine-readable contract at [`openapi.json`](openapi.json) or `/openapi.json`. OpenAPI defines every endpoint's parameters, request schema, response schema, and validation response. `/api/health`, `/api/auth/register`, `/api/auth/login`, and `/api/auth/google` are public. `/api/auth/logout` and `/api/auth/me` require a bearer token, as do the other protected `/api/*` routes.

## Endpoint inventory and request/response formats

`JSON body: schema` names refer to the schemas in OpenAPI. For responses, JSON routes return the documented `200` schema; CSV routes return downloadable `text/csv`; `/` returns HTML. Path and query parameters are shown explicitly. This index covers all application routes.

| Method | Endpoint | Request format | Successful response |
|---|---|---|---|
| GET | `/` | No body or parameters | HTML home page |
| POST | `/api/auth/register` | JSON `RegisterIn` | JSON access token and user |
| POST | `/api/auth/login` | JSON `LoginIn` | JSON access token and user |
| POST | `/api/auth/google` | JSON `GoogleLoginIn` | JSON access token and user |
| POST | `/api/auth/logout` | Bearer token; no body | JSON logout status |
| GET | `/api/auth/me` | Bearer token; no body | JSON current user profile |
| PATCH | `/api/auth/me` | JSON profile update | JSON updated profile |
| GET | `/api/admin/users` | Administrator bearer token | JSON account list with assigned scopes |
| PATCH | `/api/admin/users/{user_id}` | Administrator token; JSON `{"role":"FACULTY"}` (or other supported role) | JSON role update status |
| POST | `/api/admin/access` | Administrator token; JSON `{"user_id":2,"course":"AAA"}` or `{"user_id":2,"student_code":"OU12345_AAA_2013J"}` | JSON saved scope grant |
| DELETE | `/api/admin/access/{grant_id}` | Administrator bearer token | JSON revocation status |
| GET | `/api/students` | Query: `q`, `course`, `region`, `education`, `age_band`, `credits`, `attempts`, `level`, `sort_by`, `limit`, `offset` | JSON paginated student profiles |
| POST | `/api/students` | JSON student profile | JSON created profile |
| GET | `/api/export/students.csv` | Bearer token; no body | CSV download |
| GET | `/api/students/{code}` | Path: `code` | JSON detail, timeline, and recommendation |
| PATCH | `/api/students/{code}` | Path: `code`; JSON fields to update | JSON updated profile |
| DELETE | `/api/students/{code}` | Path: `code` | JSON deletion status |
| GET | `/api/analytics/dashboard` | No body or parameters | JSON cohort metrics and trends |
| GET | `/api/courses` | No body or parameters | JSON course metrics |
| GET | `/api/analytics/reports.csv` | Bearer token; scope-filtered for the signed-in role | CSV course-level report without student identifiers |
| POST | `/api/recommendations` | JSON `RecommendationIn` | JSON support recommendations |
| POST | `/api/assistant/chat` | JSON `ChatIn` | JSON answer and supporting evidence |
| GET | `/api/students/{code}/similar` | Path: `code`; optional query/metadata filters and `limit` | JSON ranked similar profiles and scores |
| POST | `/api/agents/analyze` | JSON `AnalyzeIn` | JSON performance, risk, and intervention analysis |
| GET | `/api/models/predict/{code}` | Path: `code` | JSON demo prediction and estimates |
| GET | `/api/interventions` | Bearer token; no body | JSON role-visible intervention plans |
| POST | `/api/interventions` | JSON `InterventionCreate` | JSON created plan |
| PATCH | `/api/interventions/{intervention_id}` | Path ID; JSON plan updates | JSON updated plan |
| DELETE | `/api/interventions/{intervention_id}` | Path ID | JSON deletion status |
| POST | `/api/feedback` | JSON `FeedbackIn` | JSON saved feedback status |
| GET | `/api/analytics/evaluation` | No body or parameters | JSON feedback/evaluation summary |
| POST | `/api/admin/ingest` | Multipart CSV upload; administrator | JSON import result |
| GET | `/api/admin/audit` | Administrator; no body | JSON audit-event list |
| GET | `/api/students/export.csv` | Bearer token; no body | CSV download |
| GET | `/api/health` | No body or token required | JSON service health |

## Sample requests and responses

The examples use placeholder values. Fields returned for profiles and analysis vary with the selected record and imported data. For exact required fields, constraints, and complete examples as served by the running version, use Swagger UI or OpenAPI schemas.

### Register and obtain a token

```http
POST /api/auth/register
Content-Type: application/json

{"name":"Demo Advisor","email":"advisor@example.edu","password":"use-a-private-demo-password","institution":"Example College"}
```

Example response (`200`):

```json
{"access_token":"<signed-token>","token_type":"bearer","user":{"name":"Demo Advisor","email":"advisor@example.edu","role":"ADVISOR"}}
```

The first account in a new database is assigned `ADMIN`; later registrations start as `ADVISOR`. Only an administrator can change roles or assign scopes. Faculty grants use course codes; advisor grants use student profile IDs. Analysts receive aggregate-only reporting access.

### Assign course scope to faculty

```http
POST /api/admin/access
Authorization: Bearer <admin-token>
Content-Type: application/json

{"user_id":2,"course":"AAA"}
```

Example response: `{"id":1,"user_id":2,"course":"AAA","student_code":null}`. To assign an advisor, send `{"user_id":3,"student_code":"OU12345_AAA_2013J"}`. Revoke a grant with `DELETE /api/admin/access/{grant_id}`. `GET /api/admin/users` returns role and grant details for the access management screen.

### Filter and prioritize students

```http
GET /api/students?course=AAA%20%C2%B7%202013J&level=HIGH&limit=2&offset=0
Authorization: Bearer <access_token>
```

Example response (`200`, abbreviated):

```json
{"items":[{"id":"OU00001_AAA_2013J","course":"AAA · 2013J","level":"HIGH","risk_score":72,"priority_score":78,"score":42.5,"clicks":318,"completion":0.54}],"total":1,"limit":2,"offset":0}
```

### Find historical profiles similar to a student

```http
GET /api/students/OU00001_AAA_2013J/similar?limit=3&region=East%20Anglian%20Region
Authorization: Bearer <access_token>
```

Example response (`200`, abbreviated):

```json
{"student_code":"OU00001_AAA_2013J","matches":[{"code":"OU00042_AAA_2013J","similarity":0.84,"keyword_score":0.76,"semantic_score":0.81,"risk_level":"HIGH"}]}
```

### Run the multi-agent analysis

```http
POST /api/agents/analyze
Authorization: Bearer <access_token>
Content-Type: application/json

{"student_code":"OU00001_AAA_2013J"}
```

Example response (`200`, abbreviated):

```json
{"student_code":"OU00001_AAA_2013J","summary":"OU00001_AAA_2013J has a high indicator based on academic and engagement signals.","performance_analysis":{"agent":"performance_analysis","summary":"Assessment results are below average; activity is declining."},"risk_analysis":{"agent":"risk_assessment","level":"HIGH","explainable_factors":["Low assessment average"]},"support_recommendation":{"agent":"intervention_recommendation","actions":["Offer an advisor check-in and agree on a short study plan."]},"retrieved_cases":[],"llm_used":false}
```

### Ask the grounded assistant

```http
POST /api/assistant/chat
Authorization: Bearer <access_token>
Content-Type: application/json

{"message":"Summarize the main assessment and engagement trends for course AAA 2013J."}
```

Example response (`200`, abbreviated):

```json
{"summary":"The available dataset has student-course profiles and retrieved examples relevant to this question.","agent_workflow":[{"agent":"dataset_performance_analysis","summary":"Cohort summary based on local profiles."}],"evidence":["Dataset aggregate and retrieved profile examples"],"similar_cases":[],"llm_used":false}
```

### Create an intervention plan

```http
POST /api/interventions
Authorization: Bearer <access_token>
Content-Type: application/json

{"student_code":"OU00001_AAA_2013J","action":"Arrange an advisor check-in and review progress next week.","status":"Needs Attention"}
```

Example response (`200`, abbreviated):

```json
{"id":1,"student_code":"OU00001_AAA_2013J","action":"Arrange an advisor check-in and review progress next week.","status":"Needs Attention"}
```

## Errors and access

- `401`: missing, invalid, or expired authentication.
- `403`: authenticated user lacks the required role or ownership.
- `404`: requested record does not exist or is outside the caller's assigned scope.
- `422`: input validation failed; response includes field-level validation details.

Advisor and faculty student lists, details, recommendations, analysis, predictions, interventions, and student-level CSV exports are limited to their explicit grants. Analysts use aggregate dashboards and the aggregate CSV route; student-level endpoints are denied. Administrators can manage roles and grants. CSV upload is administrator-only and capped at 15 MB. Google OAuth requires server-side client configuration; password-based login remains available without it.
