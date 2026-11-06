# Stage 12 activities and evidence

BLANK student response template. Supplied from the beginning in stage12/ in your EXISTING repository; complete it only when you reach Stage 12 after the previous applicable stage is integrated, verified and recorded; preserve project/, tests, earlier records and Git history. UG/common and PG/extended scope must be explicit. Use concise results and versioned links, not copied logs or source. No staff answers or fabricated approvals.

Group/tutorial: Thursday 2:30–4:30pm tutorial, Group 6
Members and UG/PG applicability: Aditya Vungarala (u3321194), Khuzaimah (Khuzaimah876), Manit Mahajan (CEOOFINDIA). All three are UG; PG scope not applicable.



## A Release scope and starting SHA

Release label/version and requirements baseline: SmartCare v1.0 (course release), Assignment 3 revision 2 requirements, UG common scope (FR-01–FR-09, QRY-01–04, FP-01–03, UI requirements; FR-10 retired).
Common starting SHA / branch / applicable members: 9ac14d8dd3816879a76161ae14678ce589e153e5 on main (application code unchanged since the Stage 9 merge 9d738a7); Stage 12 work on branch docs/stage12-release (issue #22); all three members (UG).
PG starting SHA / branch / applicable members or not applicable: Not applicable; all members are UG.
Working-state review and approved integration: git status --short was empty at 9ac14d8; all Stage 6–9 work is integrated through reviewed PRs; no outstanding approved work to integrate.
Protected common candidate and PG differences: Common candidate is main at 9ac14d8; no PG extension.
Feature freeze / owner / verifier: Feature freeze from 9ac14d8 (no new features; only reviewed fixes for genuine release blockers). Owner: Khuzaimah. Verifier: Aditya.



## B Requirements and release readiness matrix

Tutorial activity 1: All tests pass, README setup is incomplete, one dependency is unreviewed and a known limitation is undocumented. Decide Release / Release with conditions / Do not release and justify: [response]

Tutorial activity 2 and actual readiness matrix. Add exact requirement/acceptance IDs, evidence and reviewer; distinguish common/PG applicability.

| Release claim / requirement / scope | Evidence | Location/link and SHA | Reviewer | Sufficient? | Gap/action |
|---|---|---|---|---|---|
| Cancellation history works | [response] | [response] | [response] | [response] | [response] |
| Architecture responsibilities are appropriate | [response] | [response] | [response] | [response] | [response] |
| Rescheduling is safe — PG only | [response] | [response] | [response] | [response] | [response] |
| AI use is responsible — common recheck / PG assurance | [response] | [response] | [response] | [response] | [response] |
| System is maintainable | [response] | [response] | [response] | [response] | [response] |
| FR-01–03 register/find and validation | [response] | [response] | [response] | [response] | [response] |
| FR-04–05 booking/conflict rules | [response] | [response] | [response] | [response] | [response] |
| FR-06–08 cancellation/history/find | [response] | [response] | [response] | [response] | [response] |
| FR-09 and QRY/FP listing/filter/order/purity | [response] | [response] | [response] | [response] | [response] |
| UI full console sequence and error recovery | [response] | [response] | [response] | [response] | [response] |
| Session-only scope / FR-10 retired | [response] | [response] | [response] | [response] | [response] |
| PG RES and assurance integration | [response] | [response] | [response] | [response] | [response] |


## C Full regression results

| Suite/scope | Environment/version | Working directory and command | Tested SHA | Actual result | Evidence link |
|---|---|---|---|---|---|
| Complete common | Python 3.13.1, pytest 8.3.5 (requirements-dev.txt) | `project/`: `python3 -m pytest -q` | 9ac14d8 | 132 passed | Issue #22 |
| Complete PG if applicable | [response] | [response] | [response] | [response] | [response] |
| Affected focused checks after correction | [response] | [response] | [response] | [response] | [response] |
| Full integrated recheck | [response] | [response] | [response] | [response] | [response] |
Prior assertions preserved / reviewed test diff: [response]
Remaining failure / limitation: [response]


## D Console and end to end demonstration

| Demo step | Synthetic setup/input | Expected requirement | Observed result | Evidence/link |
|---|---|---|---|---|
| Problem and stakeholders | Clinic staff register patients and practitioners, book and cancel appointments, and look up or list them during one session | Overview purpose | Explained by Khuzaimah before the demo | project/README.md |
| Register and find Patient and two Practitioners | 1: P1/Alex; 2: P1; 2: P9; 3: D1/Taylor/General practice; 3: D2/Sam/Dermatology; 4: D1 | FR-01–03; unknown lookup recovers | Registered and found P1, D1, D2; P9 gave "Error: Patient not found" and the menu continued | Demo run 6 Nov, branch docs/stage12-release (code as 9ac14d8) |
| Valid booking | 5: A1/P1/D1/2026-12-01 09:00 | FR-04, AC-03.1 | "Booked: A1: P1 with D1, 2026-12-01 09:00, scheduled" | As above |
| Same practitioner exact-time conflict rejected | 5: A2/P1/D1/2026-12-01 09:00; then 7: A2 | FR-05, AC-04.1; no partial appointment | "Error: Practitioner already has a SCHEDULED appointment at this time"; 7: A2 gave "Error: Appointment not found", so nothing was stored | As above |
| Different practitioner same time allowed | 5: A3/P1/D2/2026-12-01 09:00 | AC-04.2 | "Booked: A3: P1 with D2, 2026-12-01 09:00, scheduled" | As above |
| Cancel SCHEDULED and retain/find CANCELLED object | 6: A1; 7: A1 | FR-06/07, AC-05.1, AC-05.2, FR-08 | "Cancelled: A1 … cancelled"; 7: A1 returned "A1: P1 with D1, 2026-12-01 09:00, cancelled" | As above |
| Invalid/repeated cancellation rejected | 6: A1 again; 6: A9 | AC-05.3 | "Error: Only SCHEDULED appointments may be cancelled"; A9 gave "Error: Appointment not found" | As above |
| Default all-status listing | 8: D1, blank status | FR-09, QRY-02 | Listed "A1: P1 with D1, 2026-12-01 09:00, cancelled" (history retained) | As above |
| Explicit filtering / empty vs unknown / deterministic order | 8: D1/scheduled; 8: D9/blank | QRY-02, QRY-04, QRY-03 | D1 scheduled: "No matching appointments."; unknown D9: "Error: Practitioner not found". Equal-time ordering is shown by test_select_breaks_equal_times_by_appointment_id (test_queries.py l.187) because the menu cannot create equal-time SCHEDULED bookings for one practitioner | As above; test_queries.py |
| Invalid date/status/menu/lookup recovery and continued operation | 5: A4 with 2026-02-30 09:00; 8: D1/finished; menu x; accidental inputs "2\" and "A1\" | UI-02 | "Error: Invalid calendar date/time; use YYYY-MM-DD HH:MM"; "Error: Status must be scheduled, cancelled or completed (or blank for all)"; "Unknown choice 'x': enter 0-8."; the accidental inputs were also rejected; the menu continued every time | As above |
| Session-only limitation and normal exit | 0; new process; 2: P1 | FR-10 retired, session-only | "Goodbye. Session data is discarded."; in the new process P1 gave "Error: Patient not found" | As above |
| One meaningful requirement-linked pytest test explained | `python3 -m pytest -q tests/test_regressions.py::test_f8_02_cancelled_appointment_is_retained_and_retrievable` from project/ | FR-07, AC-05.2 | 1 passed. The test cancels A1 and asserts the same object is still listed, returned by both store and service lookup (`is`), with status CANCELLED | test_regressions.py l.46 |
| Architecture and one actual AI decision / known limitation | Domain owns validation and cancel(); store holds the session; services coordinate conflicts; queries are pure; console only interacts. AI decision: Copilot's F8-01 fix guessed `appt.practitioner_id`; we changed only the operator on the real line (fa656fb). Limitation: data is lost on exit | Architecture, responsible AI, limitations | Explained by Khuzaimah | Stage 8 record F, issue #12 |
| PG reschedule identity/participants/time and no-op | Not applicable (UG) | — | — | — |
| PG conflict/invalid status/failure non-mutation | Not applicable (UG) | — | — | — |
| PG old slot / current lookup/list ordering / assurance risks | Not applicable (UG) | — | — | — |
Stable demo owner / fresh process / command: Khuzaimah, 6 Nov 2026, Python 3.13.1, new process: `python3 main.py --interactive` from project/.
PG demonstrations through service/tests or not applicable: Not applicable; UG group.



## E Final code quality and AI review

| Review area | Code/evidence location | Finding or no finding | Correction/no change and recheck |
|---|---|---|---|
| OOP responsibilities and pure-query boundaries | [response] | [response] | [response] |
| PascalCase and snake_case naming | [response] | [response] | [response] |
| Useful type hints and meaningful docstrings | [response] | [response] | [response] |
| Four-space indentation and imports/layout | [response] | [response] | [response] |
| Focused methods / duplication / dead or commented code | [response] | [response] | [response] |
| Globals / leakage / unnecessary inheritance or frameworks | [response] | [response] | [response] |
| No SQLite/persistence/repository ABCs/speculative features | [response] | [response] | [response] |
| Synthetic data / secrets / dependencies / provenance | [response] | [response] | [response] |
| Significant common Copilot contributions and human verification | [response] | [response] | [response] |
| PG plan/diff/test approvals and Stage 11 VERIFY/TRUST | [response] | [response] | [response] |

| AI claim | Affected requirement/code | Human check | Accept/Modify/Reject and reason | Actual outcome/action or no change |
|---|---|---|---|---|
| [response] | [response] | [response] | [response] | [response] |
Access route or approved equivalent / limitations: [response]
Available AI evidence and missing evidence honestly disclosed: [response]


## F README and reproducibility check

| README item | Location | Verifier | Result/gap |
|---|---|---|---|
| Purpose and included common/PG scope | [response] | [response] | [response] |
| Out-of-scope capabilities and known limitations | [response] | [response] | [response] |
| Confirmed teaching Python version and dependency installation | [response] | [response] | [response] |
| Working directory / demo / interactive / test commands | [response] | [response] | [response] |
| Repository structure and architecture responsibilities | [response] | [response] | [response] |
| Responsible AI summary / synthetic-data rule | [response] | [response] | [response] |
| Release label/version and SHA links | [response] | [response] | [response] |
Root README index and project/README verified: [response]
Fresh clone or extracted ZIP / candidate identity: [response]
Verifier and clean environment / actual version: [response]
Setup/run/test commands and observed results: [response]
Missing local file or setup gap / remedy and recheck: [response]


## G Known limitations debt and release notes

Delivered features: [response]
Important fixes: [response]
Architecture/quality improvements: [response]
Known limitations: [response]
AI-assisted development note: [response]

| Debt item | Impact | Priority | Future action | Accepted? / release rationale |
|---|---|---|---|---|
| [response] | [response] | [response] | [response] | [response] |
Session-only synthetic data and minute-precision local time: [response]
Production auth/roles, portal, notifications, billing/insurance, clinical AI exclusions: [response]
Scale/concurrency, timezone policy, operations/monitoring, accessibility/usability limitations: [response]
Difference between accepted scope limit and unresolved required behaviour: [response]
PG assurance residual risks / owner / status or not applicable: [response]


## H Release findings and corrective action

| Requirement/claim | Reproduction/observation | Impact/severity | Owner/action | Corrective diff | Focused/full recheck | Residual limit |
|---|---|---|---|---|---|---|
| [response] | [response] | [response] | [response] | [response] | [response] | [response] |
Justified no-change conclusion if no defect found: [response]
Release blockers still open / status: [response]


## I Git review and integration evidence

Issue / PR / diff links and reviewed SHA: [response]
Independent reviewer / feedback / response: [response]
Integration commit / full recheck: [response]
Tracked and untracked file inspection / cleanliness: [response]
Secrets/staff material/caches/tool-metadata exclusion check: [response]
Candidate recovery plan / known-good SHA: [response]
Named substantive contributions: [response]


## J Human release decision

Decision — READY FOR COURSE RELEASE / READY WITH DOCUMENTED LIMITATIONS / NOT YET READY: [response]
Approver / date / rationale and evidence: [response]
What risks remain / conditions / owners: [response]
Can the team explain the system: [response]
Can a change be recovered: [response]
Common decision / PG decision where different: [response]


## K Final tested release SHA

Exact common tested SHA: [response]
Exact PG tested SHA or not applicable: [response]
Final submitted SHA / repository URL: [response]
Evidence-only later commit and difference explanation: [response]
Executable changes after testing and re-verification: [response]
Source ZIP name / SHA correspondence / extracted comparison: [response]


## L Submission package verification

- [ ] Feature freeze and scoped requirements traced.
- [ ] Applicable full regressions, integrated demo and invalid paths verified.
- [ ] Architecture/code quality and final AI/dependency checks complete.
- [ ] Root README and project/README reproduced by another verifier.
- [ ] Release notes, technical debt and limitations visible.
- [ ] Independent human review, integration and release decision recorded.
- [ ] Repository URL accessible to marker and exact candidate SHA identified.
- [ ] One source ZIP from submitted commit with root README.md and .gitignore.
- [ ] project/ source and all accumulated applicable tests included.
- [ ] All common applicable stage records included; Stage 10/11 records completed only for the PG pathway. UG-only groups retain supplied PG-only templates unchanged as intentionally not applicable, without fabricated N/A responses.
- [ ] No .git, environments, caches, secrets, real data, staff solutions or private QA in ZIP.
- [ ] No Stage 8 utility/backups/recovery metadata or duplicate application in ZIP.
- [ ] Mixed-group common protection and candidate upload routing checked.
- [ ] Group reflection, confidential individual peer forms and common team viva routed separately.

Confirmed assessment item/upload route: [response]
Deadline/timezone: [response]
Repository access arrangement: [response]
Mixed-candidate upload arrangement: [response]
Oral/video recording/accessibility arrangements: [response]
Remaining administration or release dependency: [response]


## M Formative questions

1. What is a release candidate? [response]

2. What is feature freeze and why is it used? [response]

3. What is regression testing in a release context? [response]

4. What is a known limitation? [response]

5. What is technical debt? [response]

6. What are release notes? [response]

7. What is software maintenance? [response]

8. What is the purpose of the individual demonstration/viva? [response]

9. What should the final responsible-AI check establish before release? [response]

10. What is the main course conclusion about AI and the role of the software engineer? [response]


## N Reflection viva and handover

Strongest evidence SmartCare is ready: [response]
Weakest area: [response]
How AI use changed from Stage 1 to Stage 12: [response]
Start doing — engineering and AI use: [response]
Stop doing — engineering and AI use: [response]
Continue doing — engineering and AI use: [response]
What worked / caused rework / future delivery improvement: [response]
One paragraph — If AI can write code why do we still need software engineers: [response]

| Preparation item | Own explanation and evidence link |
|---|---|
| Problem and stakeholders | [response] |
| Two requirements and acceptance criteria | [response] |
| Domain model and architecture | [response] |
| Design trade-off | [response] |
| Meaningful test and its limits / 100 percent coverage | [response] |
| Diagnosed defect and verification | [response] |
| Shared store and session-state/query responsibilities | [response] |
| What would break if session-state lookup/query responsibilities changed? | [response] |
| Why cancellation is domain behaviour / conflict coordination is service behaviour | [response] |
| FR-07 retained history test | [response] |
| Actual AI change rejected/modified or honestly accepted with verification | [response] |
| Unresolved limitation / future production work | [response] |
| Personal implementation contribution | [response] |
| Personal test/review/design/integration contribution | [response] |
| PG agentic change and rescheduling verification | [response] |
| PG responsible-AI risk/remediation or supported no finding | [response] |

Optional bounded-change practice only: validation rule, focused test, safe error-message change, explicit-input query or agreed status rule with test. Explain expected impact before editing, make a small change, run the test, and identify evidence to inspect if unsure. No live AI unless explicitly permitted. Preserve the submitted candidate.

Practice question/change and reasoning: [response or not undertaken]
Separate reflection / peer / common team viva evidence links and routing: [response]
No further coding stage. Later corrections use the published assessment process.
