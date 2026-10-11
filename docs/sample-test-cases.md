# Sample Test Cases

These are reproducible manual acceptance cases. They describe expected behavior; they are not a claim that every case has been automated.

| ID | Area | Steps | Expected result |
|---|---|---|---|
| TC-01 | Signup | Create first account with valid name/email/strong password | Account created, token returned, first account role is ADMIN |
| TC-01b | Safe registration | Register another account and try to include `"role":"ADMIN"` in the request | Account is created as ADVISOR; submitted role cannot elevate privileges |
| TC-02 | Input validation | Submit password shorter than 8 characters or lacking required character classes | Request rejected with validation message; no account created |
| TC-03 | Login | Sign in with valid credentials, then invalid password | Valid credentials return token; invalid credentials return 401 |
| TC-04 | Student list | Open Students and set course/region/credits/attempt filters | Rows satisfy all active filters; count/pagination reflects matching rows |
| TC-05 | Empty filter result | Select a combination with no matching historical profiles | Clear no-match explanation is shown; Clear all filters restores results |
| TC-06 | Prioritization | Sort by default priority and inspect high-risk profile | Higher screening priority appears first; profile exposes component evidence |
| TC-07 | Similarity | Open a profile and request similar cases | Up to five distinct historical profiles include keyword and semantic component scores |
| TC-08 | Student analysis | Ask assistant about a valid composite OULAD profile ID | Performance/risk/support agents return evidence, retrieved cases, actions, and limitations |
| TC-09 | Cohort assistant | Ask a cohort-level question without a student ID | Dataset aggregates returned; NIM prose used only if configured/available |
| TC-10 | Intervention create | Create an intervention for an existing student ID | Plan appears in list with chosen status/action; unknown student is rejected |
| TC-11 | Intervention edit/delete | Edit an owned plan, then delete it | Changes persist; deletion removes the plan; unauthorized user receives 403 |
| TC-12 | Feedback | Submit Helpful and Not Helpful ratings | Feedback counts and helpful rate update in evaluation screen |
| TC-13 | Role guard | Non-admin attempts to edit/delete student or access audit | Request rejected with 403 |
| TC-13b | Persistent scope | Admin grants a student to an advisor and a course to a faculty account; sign in as each | Advisor sees only assigned students; faculty sees records only in assigned courses; scope remains after restart |
| TC-13c | Analyst privacy | Sign in as analyst and request a student list/detail or identifiable CSV | Student-level requests are denied; aggregate dashboard and course aggregate CSV remain available |
| TC-13d | Admin account management | Change account role, grant/revoke scope, then inspect audit events | Role and grants update persistently; changes appear in the audit log |
| TC-14 | Data import | Run OULAD importer twice against same folder | First run imports records; second run refreshes, not duplicates, imported IDs |
| TC-15 | Export | Download CSV as authenticated user | Valid CSV includes headers and current student profile data |
| TC-16 | Provider fallback | Disable/invalid NIM key and use assistant | Deterministic evidence-based response remains available with provider limitation |

For live API checks use Swagger at `/docs`. For offline ranking metrics run `python scripts/evaluate_retrieval.py` from `backend/`.
