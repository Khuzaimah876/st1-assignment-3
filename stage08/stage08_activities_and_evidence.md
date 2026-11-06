# Stage 8 activities and evidence

UG and PG | One evolving group project | Complete this blank record using the Stage 8 handout.

All Assignment 3 stage materials are provided from the beginning. Complete this stage only after the previous applicable stage has been integrated, verified and recorded. Use this supplied record in stage08/ in your EXISTING repository. Preserve project/, all earlier tests, records and responses. Do not download another starter or copy staff solutions. The Stage 8 preparation utility is supplied or run by teaching staff when Stage 8 begins. Follow your tutor’s controlled workflow and the handout. If temporarily supplied, keep it outside the repository in a sibling Stage_8_Assets/ folder; exclude it from Git and the final submission.

Group/tutorial: Thursday 2:30–4:30pm tutorial, Group 6
Members and UG/PG cohorts: Aditya Vungarala (u3321194, UG); Khuzaimah (Khuzaimah876, UG); Manit Mahajan (CEOOFINDIA, UG)
Record owner / contribution links for each member: Record maintained by Khuzaimah (sections A.1–A.4, A.6, K; final I and L) and Aditya (B–H via commits on debug/stage08). Contributions: see I. PR: https://github.com/Khuzaimah876/st1-assignment-3/pull/14

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

Response and reason (actual failure from the prepared suite, F8-02):
- **Exception / assertion:** `LookupError: Appointment not found` in tests/test_services.py::test_cancelled_appointment_is_still_retrievable.
- **Expected vs observed:** expected `service.find_appointment('A1')` to return the same appointment with status CANCELLED; observed LookupError (the store returned None).
- **Test line and call path:** test_services.py line 132 `found = service.find_appointment('A1')` → `AppointmentService.find_appointment` (services.py line 136 raises because `self.data_store.find_appointment('A1')` returned None) → `SmartCareDataStore.find_appointment`.
- **Requirement:** FR-07 / AC-05.2 (cancelled history stays retrievable), BR-06/07 (cancel changes status, no delete), FR-08 (lookup by ID).
- **Three plausible causes, ranked by fit:**
  1. The store lookup filters out cancelled appointments. Best fit: the traceback ends where the service receives None from the store, and only cancelled appointments fail. *Check:* after cancelling, is A1 still in `list_appointments()` while `store.find_appointment('A1')` is None?
  2. Cancellation removes A1 from the store. Fits the LookupError too. *Check:* count `list_appointments()` before and after cancel; search data_store.py/services.py for remove/del/pop.
  3. Cancellation replaces the stored object (lookup searches for an object that is no longer there). Least likely. *Check:* read `Appointment.cancel()` and test whether the booked object itself becomes CANCELLED and stays listed.
- **Outcome:** check 1 confirmed (A1 still listed, find returns None); checks 2 and 3 ruled out (count 1 → 1, no remove/del/pop, cancel() only sets `_status` on the same object). See D and F.
- **Why a traceback alone does not establish the cause:** it shows *where* the failure was noticed (services.py line 136), not *why* the store returned None. Causes 1 and 2 produce the identical traceback; only runtime evidence (the list check) and reading the store code separated them.

### A.6 Exit question
Why is changing code immediately after seeing a failure often a poor debugging strategy?

Response and reason: Because the place a failure shows up is often not where it was caused. Editing straight away usually means guessing: you may hide the symptom (e.g. catching the exception or changing the test) while the real defect stays, or you may break other behaviour. Reproducing the failure, checking the requirement, forming a hypothesis and gathering evidence first leads to the smallest correct fix, and the failing test proves the fix worked.


Classification responses (1–5, each with reason): see A.1
Tutorial debugging record — expected; observed; reproduction; hypothesis; evidence to inspect: see A.2
Traceback — exception/assertion; expected/observed values; test line; call path; requirement; ranked causes and discriminating checks: see A.5 (after preparation)

## B. Stage 7 baseline and safe preparation

- Stage 7 code SHA and requirement baseline: d8718e28b3d6d19260572d340adb8188b80c6829 (Stage 7 code, PR #9). Later main commits fb9d97e (PR #10) and 36b1e08 (PR #11) changed records only. Requirements baseline revision 2.
- Baseline test command / working directory / observed result / evidence: `python3 -m pytest -q` in `project/` on main → 73 passed (Python 3.14, pytest 8.3.5)
- Clean preparation SHA if a record-only commit followed Stage 7: d8718e2. Aditya's local main had not yet pulled the record-only PRs #10/#11; the code is identical. main was merged into debug/stage08 afterwards (81f7e03).
- Branch and preparer / how teammates obtained this branch: `debug/stage08`, prepared once by Aditya with the tutor; teammates run `git fetch` and `git checkout debug/stage08`
- Downloaded tool version, source SHA256 and --check outcome: tool 1.1; baseline SHA256 b4a1993e878c59a9df5e9055320702b2d318c5b6055bb1693a3afc25cd8fd375; --check: "preflight PASS … CHECK ONLY: project unchanged; both proposed fault signatures verified in a temporary copy"
- --apply and --verify output summaries / artefact references: --apply: "PREPARED: F8-01 practitioner conflict; F8-02 retained-history lookup … Verified expected failures: test_f8_01_conflict; test_f8_02_history (2 failed)". --verify: "VERIFIED: exactly 2 expected failures; both approved symptom signatures present"
- Bounded diff inspected and recovery location (not committed): `git status` showed only project/smartcare/data_store.py modified; backup in project/.stage8_faults/ (ignored, not committed); tool kept outside the repository
- Prepared faulty-state commit SHA: afbeb59 ("Prepare stage 08")
- Preparation or recovery issues and resolution, if any: None during preparation. The branch was based on d8718e2 rather than the latest main; fixed by merging main into the branch (81f7e03), with no code change.
- Initial prepared full-suite command / result / key failures: `python3 -m pytest -q` in `project/` → 6 failed, 67 passed. F8-01: T-SVC-12 and starter test_conflict_rule_and_different_practitioner "DID NOT RAISE ValueError"; T-SVC-13 and T-SVC-16 "ValueError: Practitioner already has a SCHEDULED appointment" for a different practitioner. F8-02: test_cancelled_appointment_is_still_retrievable "LookupError: Appointment not found"; test_repeated_cancel_raises_value_error_and_keeps_state also LookupError.

## C. F8-01 diagnosis and repair

- Symptom / observed behaviour: The practitioner conflict rule is reversed. Booking the same practitioner (DR1) again at the exact same time is accepted; booking a different practitioner (DR2) at that time is rejected with "ValueError: Practitioner already has a SCHEDULED appointment at this time".
- Expected behaviour and requirement: FR-05 / AC-04.1: same practitioner + exact same datetime + existing SCHEDULED appointment → ValueError and nothing stored. AC-04.2: a different practitioner at the same time is allowed and stored.
- Minimal synthetic reproduction steps: Fresh store; register P1, DR1, DR2; book A1 for P1/DR1 at 2026-10-01 09:00; then `store.has_practitioner_conflict('DR1', 09:00)` and `('DR2', 09:00)`; or book A2 for P1/DR1 and A3 for P1/DR2 at 09:00.
- Meaningful failing test path/name and exact relevant failure: project/tests/test_regressions.py::test_f8_01_conflict_applies_only_to_same_practitioner → `assert False is True` at line 35 (`has_practitioner_conflict('DR1', WHEN)` returned False). Existing tests also failed: test_services.py T-SVC-12 (line 350, DID NOT RAISE ValueError), T-SVC-13 (line 362) and T-SVC-16 (line 393) (ValueError for DR2), test_starter.py::test_conflict_rule_and_different_practitioner (line 127, DID NOT RAISE).
- Human hypothesis and intended checks: see E, F8-01.
- Supported root cause and inspected code/runtime evidence: In `SmartCareDataStore.has_practitioner_conflict` (data_store.py), the practitioner condition was `appointment.practitioner.practitioner_id != practitioner_id`, so a conflict was reported only for *other* practitioners. Runtime: calling the store directly gave DR1 → False, DR2 → True. services.py passes `practitioner.practitioner_id` correctly (line 118), so the fault is in the store, not the caller.
- Smallest justified fix / diff / why other behaviour is preserved: One operator: `!=` → `==` on that line (`git diff`: 1 insertion, 1 deletion). The `exclude_appointment_id`, `date_time` and SCHEDULED conditions are unchanged, so exact-time-only conflicts, cancelled slots being free and the exclude option behave as before.
- Repair SHA / focused verification result: fa656fb. `python3 -m pytest -q tests/test_regressions.py` in `project/` → 1 failed, 1 passed (F8-01 test now passes; F8-02 still failing as expected before its own repair).

## D. F8-02 diagnosis and repair

- Symptom / observed behaviour: After cancelling A1, `find_appointment('A1')` raises "LookupError: Appointment not found", although A1 is still in `list_appointments()`. Cancelling A1 a second time also raises LookupError instead of ValueError.
- Expected behaviour and requirement: FR-07 / AC-05.2 and BR-06/07: cancellation only changes status to CANCELLED and keeps the appointment; it must still be listed and retrievable by ID (FR-08). A repeat cancel must raise ValueError and leave state unchanged.
- Minimal synthetic reproduction steps: Fresh store; register P1 and DR1; book A1 at 2026-10-01 09:00; `cancel_appointment('A1')`; then compare `list_appointments()` with `store.find_appointment('A1')`.
- Meaningful failing test path/name and exact relevant failure: project/tests/test_regressions.py::test_f8_02_cancelled_appointment_is_retained_and_retrievable → `assert None is <Appointment>` at line 55 (`store.find_appointment('A1')` returned None). Existing tests also failed: test_services.py::test_cancelled_appointment_is_still_retrievable (line 132) and test_repeated_cancel_raises_value_error_and_keeps_state (line 141), both LookupError from services.py line 136.
- Human hypothesis and intended checks: see E, F8-02.
- Supported root cause and inspected code/runtime evidence: `SmartCareDataStore.find_appointment` had an extra condition `and appointment.status.value != "cancelled"`, so it skipped stored cancelled appointments. Runtime: count before/after cancel 1 → 1; A1 still in the list with status cancelled; `store.find_appointment('A1')` → None. `grep` found no remove/del/pop; `Appointment.cancel()` only sets `_status` on the same object.
- Smallest justified fix / diff / why other behaviour is preserved: Remove only the status condition so lookup matches by ID: `if appointment.appointment_id == appointment_id.strip():` (`git diff`: 1 insertion, 2 deletions). The blank/invalid-ID ValueError, the `.strip()`, the None-for-unknown-ID contract and the domain's repeat-cancel guard are unchanged.
- Repair SHA / focused verification result: 9d45475. `python3 -m pytest -q tests/test_regressions.py` in `project/` → 2 passed.

## E. Human-first hypotheses

Complete both entries BEFORE Copilot. C/D supply observed/expected/reproduction/test; retain those initial facts and link them here.

### F8-01 human entry
Likely cause and why plausible: I think the `has_practitioner_conflict` method is checking practitioner IDs incorrectly, because the tests show the conflict rule is behaving in reverse. It allows the same practitioner at the same time but rejects a different practitioner at the same time.
Evidence intended to inspect / competing explanation / discriminating check: I'd inspect `has_practitioner_conflict` in `data_store.py` and check how it compares practitioner IDs and appointment times. Other cause: `services.py` could be passing the wrong practitioner ID to the conflict check. Check: call `has_practitioner_conflict` directly with DR1 and then DR2 for the same appointment time and see which one returns `True`.
Member and saved sequence/time or commit showing this preceded consultation: Aditya, written 4 Nov 2026 about 4:25pm AEDT, from the failing test output only (before opening data_store.py or using Copilot). Saved in the commit "Stage 8: human-first hypotheses for F8-01 and F8-02" on debug/stage08, before any Copilot prompt.

### F8-02 human entry
Likely cause and why plausible: I think `find_appointment` is ignoring cancelled appointments, because FR-07 says cancelling should only change the appointment status to CANCELLED, not remove it, but after cancellation the lookup cannot find A1.
Evidence intended to inspect / competing explanation / discriminating check: I'd inspect `find_appointment` in `data_store.py` and check whether it filters out cancelled appointments. Other cause: the cancellation process may be removing A1 from the data store completely. Check: after cancelling A1, call `list_appointments()` and see whether A1 is still present; if it is, the lookup is wrong, and if it is not, the cancellation process removed it.
Member and saved sequence/time or commit showing this preceded consultation: Aditya, written 4 Nov 2026 about 4:25pm AEDT, from the failing test output only (before opening data_store.py or using Copilot). Saved in the commit "Stage 8: human-first hypotheses for F8-01 and F8-02" on debug/stage08, before any Copilot prompt.

## F. GitHub Copilot prompts, findings and human decisions

Use the full handout prompt separately for BOTH defects, after E. Keep each actual prompt or accessible reference; include observed behaviour, expected behaviour, reproduction, failing test, human hypothesis, relevant code, three ranked causes and discriminating checks, with the no-rewrite/no-invented-requirements constraints.

### F8-01 Copilot review
Actual prompt / output reference and member: Aditya, GitHub Copilot Chat in VS Code, 4 Nov 2026 about 4:33pm AEDT, after the human-first commit 8544aea. Prompt gave FR-05/AC-04.1/AC-04.2, observed and expected behaviour, reproduction, the two failing tests, the human hypothesis and data_store.py/services.py, asked for three ranked causes with checks, and said not to rewrite the project, change tests or invent requirements. Full prompt and output: posted as a comment on the F8-01 issue (see I).
1. Ranked suggestion / evidence check / observed evidence / correct, partly correct or wrong / accept, modify or reject with reason: "has_practitioner_conflict uses != instead of ==". Check: call `store.has_practitioner_conflict` directly after booking A1 for DR1 at 09:00, then read the method. Observed: DR1 → False (should be True), DR2 → True (should be False); data_store.py line 110 is `appointment.practitioner.practitioner_id != practitioner_id`. **Partly correct → modified.** The cause is right, but Copilot guessed the attribute as `appt.practitioner_id`, so its suggested replacement line does not match the real code. We change only the operator on the real line.
2. Ranked suggestion / evidence check / observed evidence / correct, partly correct or wrong / accept, modify or reject with reason: "services.py passes the wrong ID (e.g. patient ID)". Check: read the call in services.py and compare with the direct store call. Observed: services.py line 118 passes `practitioner.practitioner_id`; the direct store call (no services.py involved) is still reversed. **Wrong → rejected.**
3. Ranked suggestion / evidence check / observed evidence / correct, partly correct or wrong / accept, modify or reject with reason: "the check compares the stored appointment's patient ID instead of practitioner ID". Check: read every attribute used in has_practitioner_conflict. Observed: it reads `appointment.practitioner.practitioner_id`, `date_time` and `status`; no patient field. **Wrong → rejected.**
Final human conclusion and comparison with initial hypothesis: Root cause is the inverted comparison (`!=`) on the practitioner-ID line of `has_practitioner_conflict` in data_store.py. This matches Aditya's initial hypothesis ("checking practitioner IDs incorrectly"), and his planned DR1/DR2 direct check is what separated it from the services.py alternative. Copilot's top suggestion agreed but needed correcting to the real attribute name; its other two were ruled out by the code and the direct check.

### F8-02 Copilot review
Actual prompt / output reference and member: Aditya, GitHub Copilot Chat in VS Code (new chat), 4 Nov 2026 about 4:45pm AEDT, after the human-first commit 8544aea. Prompt gave FR-07/AC-05.2/BR-06/07/FR-08, observed and expected behaviour, reproduction, the two failing tests, the human hypothesis and data_store.py/services.py/domain.py, asked for three ranked causes with checks, and said not to rewrite the project, change tests or invent requirements. Full prompt and output: posted as a comment on the F8-02 issue (see I).
1. Ranked suggestion / evidence check / observed evidence / correct, partly correct or wrong / accept, modify or reject with reason: "find_appointment filters out CANCELLED appointments". Check: book A1, cancel it, compare `list_appointments()` with `store.find_appointment('A1')`, then read the method. Observed: A1 still in the list with status cancelled, but `find_appointment('A1')` returns None; data_store.py line 94 adds `and appointment.status.value != "cancelled"`. **Correct → accepted with a small modification.** Copilot's example used the enum (`AppointmentStatus.CANCELLED`) and its replacement line dropped the `.strip()`; the real code compares the string value, and our fix only removes the status condition, keeping the blank-ID check and `.strip()`.
2. Ranked suggestion / evidence check / observed evidence / correct, partly correct or wrong / accept, modify or reject with reason: "cancellation removes the appointment from the store". Check: count appointments before/after cancel; search for remove/del/pop. Observed: count 1 → 1, A1 still listed; `grep` found no remove/del/pop in data_store.py or services.py; `cancel_appointment` only calls `appointment.cancel()`. **Wrong → rejected.**
3. Ranked suggestion / evidence check / observed evidence / correct, partly correct or wrong / accept, modify or reject with reason: "cancellation creates a replacement object and drops the stored one". Check: read `Appointment.cancel()` and check the booked object after cancelling. Observed: domain.py line 137 only sets `self._status = AppointmentStatus.CANCELLED` on the same object; the object returned by booking is still in the list and now shows cancelled. **Wrong → rejected.**
Final human conclusion and comparison with initial hypothesis: Root cause is the extra status filter in `SmartCareDataStore.find_appointment`, which hides cancelled appointments that are still stored. This matches Aditya's initial hypothesis ("find_appointment is ignoring cancelled appointments"); his planned `list_appointments()` check showed the record is stored but not found, ruling out removal. The repeated-cancel failure has the same cause: the second cancel cannot find A1, so it raises LookupError before reaching the domain's ValueError guard.

## G. Failing to passing regression evidence

| Checkpoint | Code SHA or precise diff | Command and working directory | Actual result and artefact reference |
|---|---|---|---|
| F8-01 before repair | ad22b26 (regression tests added on faulty code) | `python3 -m pytest -q tests/test_regressions.py` in `project/` | 2 failed; F8-01: `assert False is True` (line 35) |
| F8-01 after repair | fa656fb (`!=` → `==` in has_practitioner_conflict) | same | 1 failed, 1 passed (F8-01 passes; F8-02 not yet repaired) |
| F8-02 before repair | fa656fb (F8-02 filter still present) | same | F8-02: `assert None is <Appointment>` (line 55) |
| F8-02 after repair | 9d45475 (status filter removed from find_appointment) | same | 2 passed |
| Full suite after both repairs, before refactor | 9d45475 | `python3 -m pytest -q` in `project/` | 75 passed (73 earlier tests + 2 regression tests); previously 6 failed, 67 passed |

Explain how the assertions detect each relevant incorrect result and protect previous behaviour: F8-01 asserts the store reports a conflict for DR1 and none for DR2 at the same time, that a second DR1 booking raises ValueError and leaves the list as `[first]`, and that DR2 is then stored — so either direction of the reversed rule fails, as does a fix that blocks everyone. F8-02 asserts the cancelled object stays as the only listed item, that both the store and the service return the *same* object (`is`), that its status is CANCELLED, and that a repeat cancel raises ValueError without changing state — so deleting, hiding, replacing or wrongly re-cancelling the appointment all fail. The 73 earlier tests still pass, protecting the rest of FR-01..FR-08.
Unrelated failures investigated / resolution: Not applicable. All 6 initial failures were traced to F8-01 (4 tests) or F8-02 (2 tests) and all passed after the two repairs; no other failures appeared.

## H. Refactoring decision and before/after verification

Smell and exact location: Magic status string. `SmartCareDataStore.has_practitioner_conflict` in project/smartcare/data_store.py (about line 111) checks `appointment.status.value == "scheduled"` instead of using the existing `AppointmentStatus` enum, which data_store.py already imports.
Small proposed structural change / why justified: Replace that one comparison with `appointment.status is AppointmentStatus.SCHEDULED`. Written before editing (after both repairs, full suite 75 passed at 9d45475). Justified because the enum is the single source of truth for statuses (A.4 smell list); a typo in a string would fail silently, while a wrong enum name raises an error. One line, same file, no new architecture.
External behaviour to preserve / relevant tests: Only SCHEDULED appointments for the same practitioner at the exact same time conflict; a cancelled slot is free; a different practitioner is allowed; `exclude_appointment_id` still works. Protected by test_regressions.py::test_f8_01_conflict_applies_only_to_same_practitioner, T-SVC-12, T-SVC-13, T-SVC-14 (exact datetime only), test_cancelled_slot_can_be_booked_again (cancelled slot is free), T-SVC-16 and the starter conflict test.
Before result: see G, full passing suite.
Actual change / diff / separate refactor SHA: 638f38c. One line in `has_practitioner_conflict`: `and appointment.status.value == "scheduled"):` → `and appointment.status is AppointmentStatus.SCHEDULED):` (`git diff`: 1 insertion, 1 deletion). Plan committed first in b3ae2ad.
Focused and full after-refactor commands / working directory / results / evidence: In `project/`: `python3 -m pytest -q tests/test_regressions.py` → 2 passed; `python3 -m pytest -q` → 75 passed (same as before the refactor).
Result — accepted, revised or rejected / reason / behaviour-preservation conclusion: Accepted. The same 75 tests pass before and after, including every conflict-rule test, so external behaviour is preserved; the code now uses the project's status enum consistently.

## I. Git, human review and integration

Issues for both defects / refactor scope and owners: #12 F8-01 (https://github.com/Khuzaimah876/st1-assignment-3/issues/12) and #13 F8-02 (https://github.com/Khuzaimah876/st1-assignment-3/issues/13), owner Aditya; each holds the actual Copilot prompt and response. Refactor scope (one magic-string replacement in has_practitioner_conflict) stated in PR #14 and section H, owner Aditya. Both issues closed by the merge.
Branch / prepared, repair and refactor checkpoints: `debug/stage08`. Prepared afbeb59 (B); human hypotheses 8544aea (E); failing regression tests ad22b26 (G); F8-01 repair fa656fb (C); F8-02 repair 9d45475 (D); refactor plan b3ae2ad and refactor 638f38c (H); review follow-up da1f109 (I).
PR link and another member's reviewer identity: https://github.com/Khuzaimah876/st1-assignment-3/pull/14, opened by Aditya (u3321194); reviewer Manit Mahajan (CEOOFINDIA), who did not write the repairs.
Key human feedback, difference from Copilot findings and response/outcome: Manit checked each change against the requirements (conflict rule vs FR-05/AC-04.1/AC-04.2; cancelled lookup and blank-ID check vs FR-07/FR-08; enum refactor as behaviour-preserving; coverage of the two regression tests) and reran the suite himself (75 passed). Comparing the PR diff with main (rather than with the faulty code) showed that fault preparation had also removed two docstrings, which tests cannot detect and Copilot never mentioned. Aditya restored them in da1f109 (behaviour unchanged, 75 passed) and replied on the PR. Copilot only reasoned about the failing behaviour; the human review looked at what main would actually receive.
Actual review approval / merge evidence: Approval by CEOOFINDIA: https://github.com/Khuzaimah876/st1-assignment-3/pull/14#pullrequestreview-5764396265. Merged into main by Aditya (u3321194) as merge commit f87e8b6 ("Merge pull request #14 from Khuzaimah876/debug/stage08").
Integrated code SHA and team pull/retest command / working directory / result: f87e8b6. Each member ran `git checkout main && git pull`, then `python3 -m pytest -q` in `project/` and `git log --oneline -1`: Khuzaimah 75 passed at f87e8b6; Aditya 75 passed at f87e8b6; Manit 75 passed at f87e8b6.
Evidence-only later SHA / explanation if different: The commit that completes sections I, J and L is record-only (stage08 file); project code stays identical to f87e8b6.
Each member's substantive contribution and artefact: **Aditya** — ran the staff preparation with the tutor (afbeb59), wrote the human-first hypotheses (8544aea), ran both Copilot prompts and the evidence checks (issues #12/#13, section F), added the failing regression tests (ad22b26), made both repairs (fa656fb, 9d45475), the refactor (638f38c) and the review follow-up (da1f109), opened and merged PR #14 (f87e8b6). **Manit** — independent human review and approval of PR #14 with his own 75-passed rerun; post-merge retest. **Khuzaimah** — tutorial A.1–A.4/A.6 and K (PR #11), coordination of the workflow and record, post-merge retest, final record (I, L).

## J. Required reflections

1. Which Copilot diagnosis appeared convincing but lacked evidence? (Aditya) The diagnosis that seemed most convincing at first was Copilot’s suggestion that the conflict check might be comparing the patient ID instead of the practitioner ID. It sounded plausible because the behaviour was reversed, but there was no evidence for it. When I checked line 110 of `data_store.py`, the code only used `appointment.practitioner.practitioner_id`, so the diagnosis was not supported by the actual implementation.
2. What evidence changed your group's view? (Aditya) The most useful check was calling `store.has_practitioner_conflict()` directly instead of going through `services.py`. The results showed DR1 returned `False` and DR2 returned `True`, which proved the bug was already inside `data_store.py`. This ruled out the theory that `services.py` was passing the wrong practitioner ID, which was confirmed by line 118 passing `practitioner.practitioner_id` correctly.
3. How did regression tests protect the refactoring? (Aditya) The refactor changed `"scheduled"` to `AppointmentStatus.SCHEDULED`, but the tests behaved the same before and after the change. The suite passed with 75 tests before the refactor and still passed afterwards, with the two new regression tests also passing. This showed that the refactor only improved the code structure and did not change behaviour, because any break in the scheduled-appointment logic would have caused the existing and regression tests to fail.

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

- [x] Existing project, earlier tests and stage records preserved.
- [x] Passing Stage 7 SHA and safe preparation details recorded.
- [x] Both defects reproduced with meaningful failing tests.
- [x] Both human hypotheses recorded before Copilot; actual suggestions evaluated with evidence.
- [x] Supported causes and minimal repairs explained; focused and full regression results recorded.
- [x] One genuine refactor verified under passing before/after tests.
- [x] Human PR review, feedback resolution and integrated retest recorded.
- [x] Tutorial, three reflections and ten formative responses complete.
- [x] Local recovery metadata excluded from submitted source.
- [x] Same project and full suite ready for Stage 9 after Stage 8 integration, verification and recording.

Verified integrated code SHA / result: see I.
Submitted SHA and evidence-only difference if any: Code as integrated at f87e8b6; the later record-only commit for I/J/L changes only this file.
Unresolved issues or incomplete checks / owner / next action: None for the code. Sections A and K were drafted with AI help and should be reworded in our own words before submission (owner Khuzaimah). Staff tool and project/.stage8_faults/ remain outside Git.
Handover note: Stage 8 integrated at f87e8b6 with 75 passing tests (73 earlier + 2 regression tests in project/tests/test_regressions.py). Both defects are repaired and protected by regression tests; the refactor is verified. Stage 9 starts from main; `list_practitioner_appointments` in services.py is still the Stage 9 NotImplementedError stub.