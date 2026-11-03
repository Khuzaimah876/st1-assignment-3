# Stage 8 activities and evidence

UG and PG | One evolving group project | Complete this blank record using the Stage 8 handout.

All Assignment 3 stage materials are provided from the beginning. Complete this stage only after the previous applicable stage has been integrated, verified and recorded. Use this supplied record in stage08/ in your EXISTING repository. Preserve project/, all earlier tests, records and responses. Do not download another starter or copy staff solutions. The Stage 8 preparation utility is supplied or run by teaching staff when Stage 8 begins. Follow your tutor’s controlled workflow and the handout. If temporarily supplied, keep it outside the repository in a sibling Stage_8_Assets/ folder; exclude it from Git and the final submission.

Group/tutorial: Thursday 2:30–4:30pm tutorial, Group 6
Members and UG/PG cohorts: Aditya Vungarala (u3321194, UG); Khuzaimah (Khuzaimah876, UG); Manit Mahajan (CEOOFINDIA, UG)
Record owner / contribution links for each member: [complete]

Use concise results and accessible artefact links rather than copying entire logs. Keep human-first entries before consulting GitHub Copilot. Link shared evidence once; do not repeat it across sections. No entries below are specimen answers or claimed results.

## A. Tutorial activities

### A.1 Classify all five statements
For each, choose symptom, evidence or hypothesis/opinion, and explain your reason. These are discussion statements, not confirmed diagnoses.
- Appointment disappears after cancellation.
- The data-store removal path is probably being called.
- The failing test shows store.find_appointment('A1') returns None.
- The service layer is badly designed.
- Traceback points to smartcare/services.py line 42 in the example.
The example line number is illustrative; inspect the actual line in your run. The removal hypothesis must be tested against the current project, which has no public delete operation.

Response and reason:
1. "Appointment disappears after cancellation": **Symptom.** It describes what a user or test observed, not why. It needs checking: "disappears" from lookup, from the list, or both?
2. "The data-store removal path is probably being called": **Hypothesis.** A possible explanation ("probably") that has to be tested. SmartCareDataStore has no public delete method, so it cannot be true as stated. If anything removes the appointment, it would have to be code inside a store method, which is what we would inspect.
3. "The failing test shows store.find_appointment('A1') returns None": **Evidence.** A concrete, observed value from a real run. It narrows the problem to the store lookup, but on its own does not explain why.
4. "The service layer is badly designed": **Opinion.** No observation and no check that could confirm or reject it, so it does not help locate the defect.
5. "Traceback points to smartcare/services.py line 42": **Evidence** of *where the failure was observed*. It is a location, not a cause: the wrong value may have been produced earlier (e.g. in data_store.py) and only noticed at that line.

### A.2 Build a debugging record
Choose the cancelled-history scenario or a same-practitioner/time booking. Before changing code, record expected behaviour, observed behaviour, minimal reproduction, a hypothesis and evidence to inspect. Use a requirement to justify the expectation. Keep the initial hypothesis even if later evidence disproves it.

Response and reason (cancelled-history scenario, written before any code change):
- **Expected behaviour:** after `cancel_appointment('A1')`, the same object is still stored with status CANCELLED. `store.find_appointment('A1')` and `service.find_appointment('A1')` return that exact object, and it is still in `list_appointments()`. Requirement: FR-07 / AC-05.2 (cancelled history remains retrievable this session), BR-06/07 (cancellation changes state, does not delete), FR-08 (lookup by ID).
- **Observed behaviour (tutorial scenario):** after cancelling, lookup of A1 fails (store returns None / service raises LookupError).
- **Minimal reproduction:** fresh SmartCareDataStore and services; register P1 and D1; book A1 for P1/D1 at 2026-10-01 09:00; cancel A1; call `store.find_appointment('A1')`, `service.find_appointment('A1')` and `store.list_appointments()`.
- **Initial hypothesis:** the object is still stored, but the store's lookup is filtering by status (e.g. only returning SCHEDULED appointments) rather than the appointment being removed.
- **Evidence to inspect:** whether A1 is still in `list_appointments()` (stored but not found → lookup problem; missing everywhere → removal problem); its `status` value; the body of `SmartCareDataStore.find_appointment`; whether `Appointment.cancel()` only changes `_status`. We keep this initial hypothesis on record even if the evidence later disproves it.

### A.3 Test defect or product defect
A test expects cancelled appointments to be deleted, but FR-07 says history must be retained. What should be changed? Explain why. Also decide whether a test expecting different practitioners at the same time to conflict reflects AC-04.2. Do not assume every failing test is correct.

Response and reason:
- **Test expecting cancelled appointments to be deleted:** this is a **test defect**. FR-07 and BR-06/07 require the cancelled appointment to be kept with status CANCELLED and stay retrievable (AC-05.2). The test's expectation contradicts the requirement, so the **test** must change: it should assert the same object is still found and listed with status CANCELLED. Changing the code to delete appointments to make the test pass would break a real requirement.
- **Test expecting different practitioners at the same time to conflict:** also a **test defect**. AC-04.2 says another practitioner at the same time is **permitted**; FR-05 only rejects the *same* practitioner at the exact same datetime with a SCHEDULED booking. The test should instead expect the second booking to succeed and both to be stored.
- General point: a failing test is only correct if its expectation comes from the requirements. Check the requirement first, then decide whether the product or the test is wrong.

### A.4 Refactoring smell hunt
Consider a hypothetical 70-line AppointmentService method containing duplicate status strings, direct collection manipulation, printing, validation and four nested conditionals. Identify the smells and propose small refactorings that preserve required behaviour. The direct collection work replaces the old storage-specific scenario; use the existing SmartCareDataStore boundary. Do not implement an extra architecture.
Classify these proposed changes as refactoring, repair or feature: rename appt to appointment; extract a repeated conflict helper; add rescheduling; restore retained cancellation lookup; replace a magic status string with the existing enum. Explain the behaviour that must remain unchanged.

Response and reason:
**Smells in the hypothetical 70-line method:**
- *Long method doing several jobs* (validation, conflict checking, storing, printing): split into small, well-named steps.
- *Duplicate magic status strings* (e.g. `'scheduled'`): use the existing `AppointmentStatus` enum.
- *Direct collection manipulation* (editing a dict/list inside the service): go through the existing `SmartCareDataStore` add/find/list methods instead.
- *Printing inside a service*: services should return objects or raise ValueError/LookupError; the console decides what to print.
- *Four nested conditionals*: use guard clauses (raise early) and extract a helper such as a conflict check.
- *Validation scattered in the service*: keep field validation in the domain constructors and store, as they already are.

**Classification:**
| Change | Type | Behaviour that must stay the same |
|---|---|---|
| Rename `appt` to `appointment` | Refactoring | Everything; it is only a name |
| Extract a repeated conflict helper | Refactoring | Same practitioner + exact time + SCHEDULED is rejected; a different practitioner is allowed; a cancelled slot is free |
| Add rescheduling | Feature | Not part of Stage 8 (new behaviour, PG Stage 10 only) |
| Restore retained cancellation lookup | Repair | Fixes a broken requirement (FR-07 / AC-05.2), so behaviour is meant to change from wrong to right |
| Replace a magic status string with the enum | Refactoring (if the string matched the enum value) | Same status comparisons and results; if the string was wrong, it would be a repair instead |

### A.5 Traceback and hypothesis ranking
Using one actual failure, identify its exception/assertion, expected and observed values, test line, application call path and supporting requirement. List three plausible causes and rank them by fit with the available evidence. For each cause, name a check that could distinguish it from the others. Explain why a traceback alone does not establish the cause.

Response and reason: [complete after running the prepared suite: needs an actual failure]

### A.6 Exit question
Why is changing code immediately after seeing a failure often a poor debugging strategy?

Response and reason: Because the place a failure shows up is often not where it was caused. Editing straight away usually means guessing: you may hide the symptom (e.g. catching the exception or changing the test) while the real defect stays, or you may break other behaviour. Reproducing the failure, checking the requirement, forming a hypothesis and gathering evidence first leads to the smallest correct fix, and the failing test proves the fix worked.


Classification responses (1–5, each with reason): see A.1
Tutorial debugging record — expected; observed; reproduction; hypothesis; evidence to inspect: see A.2
Traceback — exception/assertion; expected/observed values; test line; call path; requirement; ranked causes and discriminating checks: see A.5 (after preparation)

## B. Stage 7 baseline and safe preparation

- Stage 7 code SHA and requirement baseline: [complete]
- Baseline test command / working directory / observed result / evidence: [complete]
- Clean preparation SHA if a record-only commit followed Stage 7: [complete]
- Branch and preparer / how teammates obtained this branch: [complete]
- Downloaded tool version, source SHA256 and --check outcome: [complete]
- --apply and --verify output summaries / artefact references: [complete]
- Bounded diff inspected and recovery location (not committed): [complete]
- Prepared faulty-state commit SHA: [complete]
- Preparation or recovery issues and resolution, if any: [complete]
- Initial prepared full-suite command / result / key failures: [complete]

## C. F8-01 diagnosis and repair

- Symptom / observed behaviour: [complete]
- Expected behaviour and requirement: [complete]
- Minimal synthetic reproduction steps: [complete]
- Meaningful failing test path/name and exact relevant failure: [complete]
- Human hypothesis and intended checks: see E, F8-01.
- Supported root cause and inspected code/runtime evidence: [complete after diagnosis]
- Smallest justified fix / diff / why other behaviour is preserved: [complete]
- Repair SHA / focused verification result: [complete]

## D. F8-02 diagnosis and repair

- Symptom / observed behaviour: [complete]
- Expected behaviour and requirement: [complete]
- Minimal synthetic reproduction steps: [complete]
- Meaningful failing test path/name and exact relevant failure: [complete]
- Human hypothesis and intended checks: see E, F8-02.
- Supported root cause and inspected code/runtime evidence: [complete after diagnosis]
- Smallest justified fix / diff / why other behaviour is preserved: [complete]
- Repair SHA / focused verification result: [complete]

## E. Human-first hypotheses

Complete both entries BEFORE Copilot. C/D supply observed/expected/reproduction/test; retain those initial facts and link them here.

### F8-01 human entry
Likely cause and why plausible: [complete]
Evidence intended to inspect / competing explanation / discriminating check: [complete]
Member and saved sequence/time or commit showing this preceded consultation: [complete]

### F8-02 human entry
Likely cause and why plausible: [complete]
Evidence intended to inspect / competing explanation / discriminating check: [complete]
Member and saved sequence/time or commit showing this preceded consultation: [complete]

## F. GitHub Copilot prompts, findings and human decisions

Use the full handout prompt separately for BOTH defects, after E. Keep each actual prompt or accessible reference; include observed behaviour, expected behaviour, reproduction, failing test, human hypothesis, relevant code, three ranked causes and discriminating checks, with the no-rewrite/no-invented-requirements constraints.

### F8-01 Copilot review
Actual prompt / output reference and member: [complete]
1. Ranked suggestion / evidence check / observed evidence / correct, partly correct or wrong / accept, modify or reject with reason: [complete]
2. Ranked suggestion / evidence check / observed evidence / correct, partly correct or wrong / accept, modify or reject with reason: [complete]
3. Ranked suggestion / evidence check / observed evidence / correct, partly correct or wrong / accept, modify or reject with reason: [complete]
Final human conclusion and comparison with initial hypothesis: [complete]

### F8-02 Copilot review
Actual prompt / output reference and member: [complete]
1. Ranked suggestion / evidence check / observed evidence / correct, partly correct or wrong / accept, modify or reject with reason: [complete]
2. Ranked suggestion / evidence check / observed evidence / correct, partly correct or wrong / accept, modify or reject with reason: [complete]
3. Ranked suggestion / evidence check / observed evidence / correct, partly correct or wrong / accept, modify or reject with reason: [complete]
Final human conclusion and comparison with initial hypothesis: [complete]

## G. Failing to passing regression evidence

| Checkpoint | Code SHA or precise diff | Command and working directory | Actual result and artefact reference |
|---|---|---|---|
| F8-01 before repair | [complete] | [complete] | [complete] |
| F8-01 after repair | [complete] | [complete] | [complete] |
| F8-02 before repair | [complete] | [complete] | [complete] |
| F8-02 after repair | [complete] | [complete] | [complete] |
| Full suite after both repairs, before refactor | [complete] | [complete] | [complete] |

Explain how the assertions detect each relevant incorrect result and protect previous behaviour: [complete]
Unrelated failures investigated / resolution: [complete or not applicable with reason]

## H. Refactoring decision and before/after verification

Smell and exact location: [complete]
Small proposed structural change / why justified: [complete before editing]
External behaviour to preserve / relevant tests: [complete]
Before result: see G, full passing suite.
Actual change / diff / separate refactor SHA: [complete]
Focused and full after-refactor commands / working directory / results / evidence: [complete]
Result — accepted, revised or rejected / reason / behaviour-preservation conclusion: [complete]

## I. Git, human review and integration

Issues for both defects / refactor scope and owners: [complete]
Branch / prepared, repair and refactor checkpoints: [link B/C/D/H]
PR link and another member's reviewer identity: [complete]
Key human feedback, difference from Copilot findings and response/outcome: [complete]
Actual review approval / merge evidence: [complete]
Integrated code SHA and team pull/retest command / working directory / result: [complete]
Evidence-only later SHA / explanation if different: [complete or not applicable]
Each member's substantive contribution and artefact: [complete]

## J. Required reflections

1. Which Copilot diagnosis appeared convincing but lacked evidence? [complete; report honestly if none and discuss the least-supported real suggestion]
2. What evidence changed your group's view? [complete]
3. How did regression tests protect the refactoring? [complete]

## K. Ten formative questions

1. What should an engineer do before changing code in response to a failure?

Response: Reproduce the failure, read the exact error, check the requirement to know what *should* happen, form a hypothesis and gather evidence that confirms or rules it out, and have a failing test that shows the problem.

2. Where should expected behaviour come from during debugging?

Response: From the approved requirements and public contracts (the revision 2 baseline, e.g. FR-05, FR-07, AC-05.2), not from what the code currently does or what a test happens to expect.

3. What is a debugging hypothesis?

Response: A specific, testable explanation of the cause of a failure, with a check that could prove it wrong. For example: "find_appointment returns None because it filters out CANCELLED appointments; if so, A1 will still appear in list_appointments()".

4. What is a regression test and why is it retained?

Response: A test that reproduces a defect that was fixed. It is kept in the suite so that if a later change brings the defect back, the test fails straight away.

5. What is meant by root cause?

Response: The underlying reason the failure happens: the specific faulty decision in the code that, once corrected, removes the symptom, as opposed to where the symptom happened to be noticed.

6. What is refactoring?

Response: Changing the internal structure of code (names, duplication, method size, responsibilities) without changing its external behaviour. All tests pass before and after.

7. What is a swallowed exception?

Response: An exception that is caught and then ignored (e.g. `except Exception: pass`), so the failure is hidden instead of reported or handled, which makes defects much harder to find.

8. What is a code smell?

Response: A sign in the code that it may be hard to understand or change, such as duplication, a very long method, magic strings, unclear names or a class doing work that belongs elsewhere. It is not necessarily a bug.

9. How should GitHub Copilot-generated debugging diagnoses be treated?

Response: As hypotheses, not answers. Each suggestion is checked against the requirement, the actual code and a real test run, then accepted, modified or rejected with a reason. Confident wording is not evidence, and Copilot does not replace human diagnosis or review.

10. What is the Stage 8 engineering rule?

Response: Diagnose before you fix: reproduce, check the requirement, test a hypothesis with evidence, make the smallest repair, keep a regression test, and only refactor when all tests pass, then integrate after human review.

## L. Completion and handover

- [ ] Existing project, earlier tests and stage records preserved.
- [ ] Passing Stage 7 SHA and safe preparation details recorded.
- [ ] Both defects reproduced with meaningful failing tests.
- [ ] Both human hypotheses recorded before Copilot; actual suggestions evaluated with evidence.
- [ ] Supported causes and minimal repairs explained; focused and full regression results recorded.
- [ ] One genuine refactor verified under passing before/after tests.
- [ ] Human PR review, feedback resolution and integrated retest recorded.
- [ ] Tutorial, three reflections and ten formative responses complete.
- [ ] Local recovery metadata excluded from submitted source.
- [ ] Same project and full suite ready for Stage 9 after Stage 8 integration, verification and recording.

Verified integrated code SHA / result: see I.
Submitted SHA and evidence-only difference if any: [complete]
Unresolved issues or incomplete checks / owner / next action: [complete]
Handover note: [complete]