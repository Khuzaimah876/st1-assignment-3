# Stage 7 Testing and Verification Record

Group/tutorial: Thursday 2:30–4:30pm tutorial, Group 6  Members/cohorts: Aditya Vungarala (u3321194, UG); Khuzaimah (Khuzaimah876, UG); Manit Mahajan (CEOOFINDIA, UG)
Requirements baseline: SmartCare A3 Requirements Baseline 2026, revision 2.
Use the same project/. Link actual evidence; keep responses concise. Blank fields are for your group. Copy rows only as needed.

All Assignment 3 stage materials are provided from the beginning. Complete this stage only after the previous applicable stage has been integrated, verified and recorded. Use this supplied record in stage07/ in your EXISTING repository. Preserve project/, all earlier tests, records and responses. Do not download another starter or copy staff solutions.

## A Tutorial Activities

### Activity 1 Requirement to test

For each requirement, propose one positive test, one negative test and the key assertion.

| Requirement | Positive test | Negative test | Key assertion |
|---|---|---|---|
| FR-01 Register patient | Register `P1`, `Alice Example` in a fresh store | Register a second patient with ID `P1` (or ` P1 `) | Positive: `find_patient('P1') is patient` and `list_patients() == [patient]`. Negative: `ValueError` raised, and the store still holds only the original object with its original name |
| FR-05 Prevent practitioner conflict | Book `DR2` at the same time `DR1` is already booked | Book `DR1` again at the exact same datetime while the first booking is SCHEDULED | Positive: both appointments are stored. Negative: `ValueError` raised and `list_appointments() == [first]` (the rejected booking was not stored) |
| FR-06 Cancel appointment | Cancel a SCHEDULED appointment `A1` | Cancel `A1` a second time (or cancel a COMPLETED appointment) | Positive: the returned object `is` the booked one and `status is CANCELLED`. Negative: `ValueError` raised and the status is unchanged |
| FR-07 Retain cancelled history | Cancel `A1`, then look it up and list appointments | Look up an ID that was never booked | Positive: `find_appointment('A1') is appointment` with `status is CANCELLED`, and it is still in `list_appointments()`. Negative: `LookupError` (absence is reported, and nothing is fabricated) |

### Activity 2 Strong or weak assertion

For each, select Strong for stated behaviour or Weak/unclear and explain why. State the behaviour and limits.

`assert True`
Judgement: Weak/unclear  Why: It can never fail, so it proves nothing. It only shows that the earlier lines ran without raising an exception.

`assert appointment is not None`
Judgement: Weak/unclear  Why: It shows that something came back, but not that it is the correct appointment, that it has the right status, or that it was stored. A wrong or newly made object would still pass.

`assert appointment.status == AppointmentStatus.CANCELLED`
Judgement: Strong for stated behaviour  Why: It checks the required status after cancellation (AC-05.1). Limits: it does not show that the object is the stored one, that it is still retrievable (FR-07), or that other appointments were left alone.

`assert len(results) > 0`
Judgement: Weak/unclear  Why: It only checks that the list is not empty. Wrong records, duplicates or extra items would all still pass. It should compare against the exact expected contents.

`assert data_store.find_appointment('A1') is appointment`
Judgement: Strong for stated behaviour  Why: The `is` check proves the store returns the same object, not a lookalike, so it supports storage and retained lookup (AC-06.1 / AC-05.2). Limits: it does not check status, so it needs a status assertion alongside it.

### Activity 3 Boundary thinking

Design boundary or edge cases for blank identifiers, whitespace-only names, same-time practitioner bookings, cancelled appointments and invalid status transitions.
For each input/state, expected result and supporting contract:
- **Blank identifiers:** `''`, `'   '`, `'\t'`, `None` as a patient, practitioner or appointment ID → `ValueError`, nothing stored. Contract: IDs are strings, trimmed and non-blank (`required_text`). Edge: `' P1 '` is trimmed to `P1`, so registering it again is a duplicate (`ValueError`), while `'p1'` is a different ID because IDs are case-sensitive.
- **Whitespace-only names:** `Patient('P1', '   ')` or a specialty of `'   '` → `ValueError`. Contract: names and specialty are required text. A name with outer spaces, `' Alex '`, is accepted and stored as `'Alex'`.
- **Same-time practitioner bookings:** with `DR1` SCHEDULED at 09:00, booking `DR1` at exactly 09:00 → `ValueError`. `DR2` at 09:00 → allowed (AC-04.2). `DR1` at 09:01 → allowed, because a conflict needs the exact datetime and no duration rule exists.
- **Cancelled appointments:** after `A1` (DR1, 09:00) is cancelled, booking DR1 at 09:00 → allowed, because only SCHEDULED appointments conflict. `A1` is still retrievable with status CANCELLED (FR-07).
- **Invalid status transitions:** cancelling CANCELLED → `ValueError`, status stays CANCELLED. Cancelling COMPLETED (supplied at construction) → `ValueError`, status stays COMPLETED. Contract: FR-06 permits cancellation only from SCHEDULED. Assigning `appointment.status = ...` directly → `AttributeError`, because status is a read-only property.

### Activity 4 Critique GitHub Copilot tests

GitHub Copilot generates five tests, all of which pass. Two only assert that objects are not None, one asserts True, and two assume SMS notifications exist. Identify what is wrong and rewrite the test intentions.

| Candidate | What is wrong | Rewritten test intention |
|---|---|---|
| 1 (`assert patient is not None` after registration) | Passes even if the patient is not stored or is a different object; does not check AC-01.1 | Register `P1`, then assert `find_patient('P1') is patient` and `list_patients() == [patient]` |
| 2 (`assert appointment is not None` after booking) | Does not check status, storage or the participants | Book `A1`, then assert `find_appointment('A1') is appointment`, `status is SCHEDULED`, and that `appointment.patient` / `appointment.practitioner` are the registered objects (AC-03.1) |
| 3 (`assert True`) | Can never fail, so it gives no evidence | Choose a real behaviour, e.g. a repeated cancel raises `ValueError` and the status stays CANCELLED (AC-05.3) |
| 4 (SMS sent on booking) | Invents a requirement; SmartCare has no notification feature, so the test checks a mock or a made-up method | Reject. If booking confirmation is the concern, test the real observable result: the stored SCHEDULED appointment |
| 5 (SMS sent on cancellation) | Invents a requirement again, and needs unnecessary mocking | Reject. Test FR-06/FR-07 instead: the cancelled appointment is the same object, CANCELLED, and still retrievable |

### Tutorial exit question

Why can 100% code coverage coexist with poor software verification?
Coverage only records that lines ran. A test can run every line and assert nothing, assert something weak (`is not None`), or check a made-up rule. Coverage also cannot show missing behaviour, such as a requirement nobody wrote code for. Verification needs assertions that compare results against the requirement.

## B Requirement to Test Traceability Matrix

Assign TEST IDs before implementation or generation. Use canonical AC IDs with their actual meaning; quote supporting revision 2 contracts when no canonical AC is assigned. Blank-ID validation is not AC-01.2. Identify supplied versus student-authored evidence.

S = supplied starter check (`tests/test_starter.py`); S6 = student-authored in Stage 6 (`tests/test_services.py`, first section); S7 = student-authored in Stage 7 (`tests/test_domain.py` and the Stage 7 section of `tests/test_services.py`). All results were observed in the full run recorded in J (73 passed).

| Requirement | Acceptance criterion | Test ID | Test type | Test name / location | Expected behaviour | Result / observed status | Supplied or student-authored |
|---|---|---|---|---|---|---|---|
| FR-01 | AC-01.1 (partial domain evidence) | T-DOM-01 | Domain, positive | `test_domain.py::test_patient_stores_trimmed_id_and_name` | Valid fields are stored and trimmed (no storage, so partial) | Passed | S7 |
| FR-01 | Revision 2 contract: "IDs are trimmed, non-blank" | T-DOM-02 | Domain, negative/boundary | `test_domain.py::test_blank_patient_id_is_rejected` (5 inputs) | `ValueError` | Passed | S7 |
| FR-01 | Revision 2 contract: required name | T-DOM-03 | Domain, negative/boundary | `test_domain.py::test_blank_patient_name_is_rejected` | `ValueError` | Passed | S7 |
| FR-01 | Contract: "Read-only identity" | T-DOM-04 | Domain, negative | `test_domain.py::test_patient_id_is_read_only` | `AttributeError`; ID unchanged | Passed | S7 |
| FR-01 | AC-01.1 (complete service evidence) | T-SVC-01 | Service, positive | `test_services.py::test_register_patient_stores_the_returned_object` | Same object found and listed | Passed | S7 |
| FR-01 | AC-01.2 | (supplied) | Service, negative | `test_starter.py::test_duplicate_patient_preserves_original` | `ValueError`; original kept | Passed | S |
| FR-01 | AC-01.2 (trimmed boundary) | T-SVC-02 | Service, boundary | `test_services.py::test_register_trimmed_duplicate_patient_id_is_rejected` | `' P1 '` rejected; store unchanged | Passed | S7 |
| FR-01 | Contract: IDs case-sensitive | T-SVC-03 | Service, boundary | `test_services.py::test_patient_ids_differing_only_by_case_are_distinct` | `p1` stored separately | Passed | S7 |
| FR-01 | Revision 2 contract: required name | T-SVC-04 | Service, negative | `test_services.py::test_register_patient_blank_name_leaves_store_unchanged` | `ValueError`; store empty | Passed | S7 |
| FR-02 | AC-02.1 / AC-02.2 | (Stage 6) | Service, positive/negative/boundary | `test_services.py::test_find_patient_*` (6 tests) | Same object; `LookupError`; `ValueError`; trimmed; case-sensitive | Passed | S6 |
| FR-03 | Practitioner registration (no canonical AC quoted) | T-DOM-05, T-DOM-06 | Domain, positive/negative | `test_domain.py::test_practitioner_stores_trimmed_fields`, `::test_practitioner_blank_required_field_is_rejected` | Fields stored; each blank field → `ValueError` | Passed | S7 |
| FR-03 | Practitioner registration | T-SVC-05, T-SVC-06 | Service, positive/boundary | `test_services.py::test_register_practitioner_stores_the_returned_object`, `::test_register_trimmed_duplicate_practitioner_id_is_rejected` | Stored and found; trimmed duplicate rejected, original kept | Passed | S7 |
| FR-03 (supporting lookup) | Lookup contract: "returns the actual stored Practitioner … unknown ID raises LookupError" | (Stage 6) | Service | `test_services.py::test_find_practitioner_*` (6 tests) | As stated | Passed | S6 |
| FR-04 | AC-03.1 (partial domain evidence) | T-DOM-07 | Domain, positive | `test_domain.py::test_new_appointment_starts_scheduled` | SCHEDULED; same participants and time | Passed | S7 |
| FR-04 | Revision 2 contract: ID, participants, minute-precision naive datetime, valid status | T-DOM-08 to T-DOM-11 | Domain, negative/boundary | `test_domain.py::test_appointment_blank_id_is_rejected`, `::test_appointment_requires_patient_and_practitioner_objects`, `::test_appointment_rejects_invalid_date_time` (4 inputs), `::test_appointment_rejects_invalid_status` | `ValueError` | Passed | S7 |
| FR-04 / FR-08 | AC-03.1, AC-06.1 | T-SVC-07 | Service, positive | `test_services.py::test_book_appointment_stores_scheduled_appointment` | Stored, SCHEDULED, registered participants, same object on lookup | Passed | S7 |
| FR-04 | AC-03.2 | T-SVC-08 | Service, negative | `test_services.py::test_book_unknown_participant_is_rejected_and_nothing_stored` (2 cases) | `LookupError`; store empty | Passed | S7 |
| FR-04 | Validation contract (minute precision) | T-SVC-09 | Service, boundary | `test_services.py::test_book_invalid_date_time_is_rejected_and_nothing_stored` | `ValueError`; store empty | Passed | S7 |
| FR-04 | Uniqueness of appointment ID | T-SVC-10 | Service, boundary | `test_services.py::test_book_trimmed_duplicate_appointment_id_keeps_original` | `ValueError`; original kept | Passed | S7 |
| FR-08 | AC-06.1 negative | T-SVC-11 | Service, negative | `test_services.py::test_find_unknown_appointment_raises_lookup_error` | `LookupError` | Passed | S7 |
| FR-05 | AC-04.1 / AC-04.2 | (supplied) | Service | `test_starter.py::test_conflict_rule_and_different_practitioner` | Conflict rejected; DR2 allowed | Passed | S |
| FR-05 | AC-04.1 | T-SVC-12 | Service, negative | `test_services.py::test_same_practitioner_same_time_conflict_leaves_store_unchanged` | `ValueError`; rejected booking not stored | Passed | S7 |
| FR-05 | AC-04.2 | T-SVC-13 | Service, positive | `test_services.py::test_different_practitioner_same_time_is_allowed` | Both stored | Passed | S7 |
| FR-05 | AC-04.1 boundary (exact datetime) | T-SVC-14 | Service, boundary | `test_services.py::test_same_practitioner_one_minute_later_is_allowed` | 09:01 allowed | Passed | S7 |
| FR-06 | AC-05.1 (domain) | T-DOM-12 | Domain, positive | `test_domain.py::test_cancel_changes_status` | CANCELLED; ID/time kept | Passed | S7 |
| FR-06 | AC-05.3 (domain) | T-DOM-13 | Domain, negative | `test_domain.py::test_repeated_cancellation_is_rejected` | `ValueError`; still CANCELLED | Passed | S7 |
| FR-06 | Contract: "cancellation only from SCHEDULED" | T-DOM-14 | Domain, negative | `test_domain.py::test_completed_appointment_cannot_be_cancelled` | `ValueError`; still COMPLETED | Passed | S7 |
| FR-06 | Contract: "Read-only … state changed only through public domain operations" | T-DOM-15 | Domain, negative | `test_domain.py::test_appointment_status_cannot_be_assigned_directly` | `AttributeError`; still SCHEDULED | Passed | S7 |
| FR-06 / FR-07 | AC-05.1, AC-05.2, AC-05.3 | (Stage 6) | Service | `test_services.py::test_cancel_*`, `::test_cancelled_appointment_is_still_retrievable`, `::test_repeated_cancel_raises_value_error_and_keeps_state` | As stated | Passed | S6 |
| FR-07 | AC-05.2 (listing) | T-SVC-15 | Service, positive | `test_services.py::test_cancelled_appointment_remains_in_listing` | Still listed with CANCELLED | Passed | S7 |
| FR-06 | AC-05.1 (target only) | T-SVC-16 | Service, positive | `test_services.py::test_cancel_changes_only_the_targeted_appointment` | A1 CANCELLED, A2 SCHEDULED | Passed | S7 |
| FR-05 / FR-07 | AC-04.1 (SCHEDULED only) + AC-05.2 | T-SVC-17 | Service, boundary | `test_services.py::test_cancelled_and_rebooked_slot_keeps_both_records` | Slot rebookable; both records retained | Passed | S7 |

## C Test Design

Use descriptive test names such as test_cancel_changes_status() or test_blank_patient_id_is_rejected(). Explain what new evidence each case adds.

| Test ID | Requirement | Acceptance criterion | Positive / Negative / Boundary | Test intention | Observable result expected | Added evidence beyond supplied tests |
|---|---|---|---|---|---|---|
| T-DOM-02 | FR-01 | Blank-ID contract | Negative/boundary | Blank, tab, `None` and int IDs are rejected | `ValueError` for each | Supplied test tries only `' '`; this adds empty, tab and non-string |
| T-DOM-07 | FR-04 | AC-03.1 (partial) | Positive | New appointment keeps actual participants and SCHEDULED | `status is SCHEDULED`, `patient is patient` | Domain-level check without the service; isolates the constructor |
| T-DOM-10 | FR-04 | Minute-precision contract | Boundary | Seconds, microseconds, timezone and string are rejected | `ValueError` | Not tested before |
| T-DOM-14 | FR-06 | Only from SCHEDULED | Negative | COMPLETED cannot be cancelled at domain level | `ValueError`; still COMPLETED | Stage 6 tested this through the service only |
| T-SVC-02 | FR-01 | AC-01.2 | Boundary | Trimmed duplicate is still a duplicate | `ValueError`; store unchanged | Supplied tests only use the exact same ID |
| T-SVC-03 | FR-01 | Case-sensitive IDs | Boundary | `p1` and `P1` are different patients | Both stored | Shows trimming does not also lowercase |
| T-SVC-07 | FR-04/08 | AC-03.1, AC-06.1 | Positive | Booking stores the correct linked record | Same object; SCHEDULED; registered participants | Also checks the stored date/time and the participants match service lookups |
| T-SVC-12 | FR-05 | AC-04.1 | Negative | Rejected conflict does not get stored | `list_appointments() == [first]` | Supplied conflict test does not check state after rejection |
| T-SVC-14 | FR-05 | AC-04.1 boundary | Boundary | Conflict needs the exact time only | 09:01 allowed | Guards against an invented "same hour/day" rule |
| T-SVC-15 | FR-07 | AC-05.2 | Positive | Cancelled record is still in the list | Listed, CANCELLED | Stage 6 checked lookup, not listing |
| T-SVC-16 | FR-06 | AC-05.1 | Positive | Cancel affects only its target | Other appointment still SCHEDULED | New: detects cancelling the wrong or all records |
| T-SVC-17 | FR-05/07 | AC-04.1 + AC-05.2 | Boundary | Rebooking a cancelled slot keeps history | Both records in the list | Stage 6 checked the rebooking only, not that the old record is kept |

## D Arrange Act Assert Record

Arrange test data; act on one meaningful behaviour; assert the required observable outcome. Use the specific current exception with pytest.raises where needed.

| Test ID | Arrange | Act | Assert | Why meaningful / why assertion proves criterion |
|---|---|---|---|---|
| T-DOM-13 | New Appointment A1, cancelled once | `appointment.cancel()` again inside `pytest.raises(ValueError)` | `status is CANCELLED` | Uses the specific `ValueError`, not a broad catch. The status check shows the failed call did not change state (AC-05.3) |
| T-SVC-01 | Fresh store + PatientService | `register_patient('P1', 'Alice Example')` | `find_patient('P1') is patient`; `list_patients() == [patient]` | Proves storage through the workflow (AC-01.1), not just construction. `is` rules out a copy |
| T-SVC-07 | Store with P1, DR1, DR2 | `book_appointment('A1','P1','DR1',WHEN)` | Found `is` booked; list `== [booked]`; SCHEDULED; participants `is` the registered objects | Covers every part of AC-03.1: registered participants, unique ID, stored, SCHEDULED |
| T-SVC-12 | P1, P2, DR1; A1 booked DR1 at WHEN | Book A2 for DR1 at WHEN inside `pytest.raises(ValueError)` | `list_appointments() == [first]`; `find_appointment('A2') is None` | A different patient shows the conflict is about the practitioner (AC-04.1). The state check shows nothing partial was stored |
| T-SVC-14 | A1 booked DR1 at 09:00 | Book A2 for DR1 at 09:01 | A2 found; two stored | Boundary of the exact-time rule. It fails if conflict is widened to an invented duration rule (confirmed in J) |
| T-SVC-15 | A1 booked | `cancel_appointment('A1')` | `list_appointments() == [booked]` with CANCELLED | Retained history means it is still listed, not deleted (AC-05.2) |
| T-SVC-16 | A1 (DR1), A2 (DR2) booked | `cancel_appointment('A1')` | A1 CANCELLED, A2 SCHEDULED | Would fail if cancel changed the wrong or every appointment |

## E Domain Test Evidence

Cover Patient/Practitioner construction and validation; Appointment construction, initial status, cancellation and illegal/repeated transitions. Preserve the four reference intentions described in handout Part C.

Reference intentions preserved: blank patient ID rejected (T-DOM-02); new appointment starts SCHEDULED (T-DOM-07); cancellation changes status (T-DOM-12); repeated cancellation rejected (T-DOM-13).

| Test ID | Behaviour | Test file/function | Result |
|---|---|---|---|
| T-DOM-01 | Patient stores trimmed ID and name | `tests/test_domain.py::test_patient_stores_trimmed_id_and_name` | Passed |
| T-DOM-02 | Blank/invalid patient ID → ValueError (5 parametrised inputs) | `tests/test_domain.py::test_blank_patient_id_is_rejected` | Passed (5/5) |
| T-DOM-03 | Blank patient name → ValueError (3 inputs) | `tests/test_domain.py::test_blank_patient_name_is_rejected` | Passed (3/3) |
| T-DOM-04 | Patient ID is read-only | `tests/test_domain.py::test_patient_id_is_read_only` | Passed |
| T-DOM-05 | Practitioner stores trimmed fields | `tests/test_domain.py::test_practitioner_stores_trimmed_fields` | Passed |
| T-DOM-06 | Each blank practitioner field → ValueError (4 inputs) | `tests/test_domain.py::test_practitioner_blank_required_field_is_rejected` | Passed (4/4) |
| T-DOM-07 | New appointment SCHEDULED with actual participants/time | `tests/test_domain.py::test_new_appointment_starts_scheduled` | Passed |
| T-DOM-08 | Blank appointment ID → ValueError | `tests/test_domain.py::test_appointment_blank_id_is_rejected` | Passed |
| T-DOM-09 | Participants must be Patient/Practitioner objects | `tests/test_domain.py::test_appointment_requires_patient_and_practitioner_objects` | Passed |
| T-DOM-10 | Invalid date/time → ValueError (4 inputs) | `tests/test_domain.py::test_appointment_rejects_invalid_date_time` | Passed (4/4) |
| T-DOM-11 | Invalid status → ValueError | `tests/test_domain.py::test_appointment_rejects_invalid_status` | Passed |
| T-DOM-12 | Cancel SCHEDULED → CANCELLED | `tests/test_domain.py::test_cancel_changes_status` | Passed |
| T-DOM-13 | Repeated cancel → ValueError, unchanged | `tests/test_domain.py::test_repeated_cancellation_is_rejected` | Passed |
| T-DOM-14 | Cancel COMPLETED → ValueError, unchanged | `tests/test_domain.py::test_completed_appointment_cannot_be_cancelled` | Passed |
| T-DOM-15 | Status cannot be assigned directly | `tests/test_domain.py::test_appointment_status_cannot_be_assigned_directly` | Passed |

## F Service Test Evidence

Use fresh shared SmartCareDataStore state, registered objects and completed Stage 6 services.

Every Stage 7 service test calls `make_services()` (or creates its own store), which builds one new `SmartCareDataStore` shared by all three services, so no state carries between tests.

| Test ID | Behaviour | Requirement / criterion | Test file/function | Result |
|---|---|---|---|---|
| T-SVC-01 | Registered patient is stored and found | FR-01 / AC-01.1 | `tests/test_services.py::test_register_patient_stores_the_returned_object` | Passed |
| T-SVC-02 | Trimmed duplicate patient rejected, original kept | FR-01 / AC-01.2 | `tests/test_services.py::test_register_trimmed_duplicate_patient_id_is_rejected` | Passed |
| T-SVC-03 | Case-different IDs are distinct | FR-01 / case-sensitive contract | `tests/test_services.py::test_patient_ids_differing_only_by_case_are_distinct` | Passed |
| T-SVC-04 | Blank name rejected, nothing stored | FR-01 / validation contract | `tests/test_services.py::test_register_patient_blank_name_leaves_store_unchanged` | Passed |
| T-SVC-05 | Registered practitioner stored and found | FR-03 | `tests/test_services.py::test_register_practitioner_stores_the_returned_object` | Passed |
| T-SVC-06 | Trimmed duplicate practitioner rejected | FR-03 | `tests/test_services.py::test_register_trimmed_duplicate_practitioner_id_is_rejected` | Passed |
| T-SVC-07 | Valid booking stored and found | FR-04, FR-08 / AC-03.1, AC-06.1 | `tests/test_services.py::test_book_appointment_stores_scheduled_appointment` | Passed |
| T-SVC-08 | Unknown patient/practitioner rejected | FR-04 / AC-03.2 | `tests/test_services.py::test_book_unknown_participant_is_rejected_and_nothing_stored` | Passed (2/2) |
| T-SVC-09 | Invalid booking time rejected | FR-04 / validation contract | `tests/test_services.py::test_book_invalid_date_time_is_rejected_and_nothing_stored` | Passed |
| T-SVC-10 | Duplicate appointment ID keeps original | FR-04 | `tests/test_services.py::test_book_trimmed_duplicate_appointment_id_keeps_original` | Passed |
| T-SVC-11 | Unknown appointment lookup → LookupError | FR-08 | `tests/test_services.py::test_find_unknown_appointment_raises_lookup_error` | Passed |
| T-SVC-12 | Conflict rejected, store unchanged | FR-05 / AC-04.1 | `tests/test_services.py::test_same_practitioner_same_time_conflict_leaves_store_unchanged` | Passed |
| T-SVC-13 | Different practitioner same time allowed | FR-05 / AC-04.2 | `tests/test_services.py::test_different_practitioner_same_time_is_allowed` | Passed |
| T-SVC-14 | One minute later allowed | FR-05 / AC-04.1 boundary | `tests/test_services.py::test_same_practitioner_one_minute_later_is_allowed` | Passed |
| T-SVC-15 | Cancelled appointment still listed | FR-07 / AC-05.2 | `tests/test_services.py::test_cancelled_appointment_remains_in_listing` | Passed |
| T-SVC-16 | Cancel affects only the target | FR-06 / AC-05.1 | `tests/test_services.py::test_cancel_changes_only_the_targeted_appointment` | Passed |
| T-SVC-17 | Cancelled slot rebooked, history kept | FR-05, FR-07 | `tests/test_services.py::test_cancelled_and_rebooked_slot_keeps_both_records` | Passed |

## G Negative and Boundary Cases

Connect cases to actual contracts and verify unchanged state after rejection.

| Behaviour | Boundary/invalid input | Expected result | Test ID |
|---|---|---|---|
| Patient ID validation | `''`, `'   '`, `'\t'`, `None`, `101` | `ValueError` (risk: a tab or non-string slipping through) | T-DOM-02 |
| Required names/specialty | `'   '` or `None` | `ValueError` (risk: a whitespace name being stored) | T-DOM-03, T-DOM-06, T-SVC-04 (store stays empty) |
| Duplicate after trimming | `' P1 '`, `'DR1 '`, `' A1 '` | `ValueError`; original object and fields unchanged (risk: trimming applied after the duplicate check) | T-SVC-02, T-SVC-06, T-SVC-10 |
| Case-sensitive IDs | `'p1'` vs `'P1'` | Two distinct patients (risk: IDs being normalised to one case) | T-SVC-03 |
| Unknown participants | `P404`, `DR404` | `LookupError`; no appointment stored | T-SVC-08 |
| Date/time precision | seconds, microseconds, timezone-aware, string | `ValueError`; nothing stored | T-DOM-10, T-SVC-09 |
| Exact-time conflict | DR1 at 09:00 vs 09:00 / 09:01 | 09:00 → `ValueError`, store unchanged; 09:01 → allowed (risk: the rule being wider or narrower than "exact time") | T-SVC-12, T-SVC-14 |
| Cancelled booking frees slot | Cancel A1 then rebook same slot | Allowed; A1 still kept as CANCELLED | T-SVC-17 |
| Repeated cancellation | Cancel CANCELLED | `ValueError`; still CANCELLED | T-DOM-13 |
| Cancel COMPLETED | COMPLETED at construction | `ValueError`; still COMPLETED | T-DOM-14 |
| Direct state change | `appointment.status = CANCELLED`, `patient.patient_id = 'P2'` | `AttributeError`; unchanged (risk: bypassing the domain guard) | T-DOM-04, T-DOM-15 |
| Invalid status/participants | `'scheduled'` text; IDs instead of objects | `ValueError` | T-DOM-09, T-DOM-11 |

## H GitHub Copilot Test Design

Select ONE real acceptance criterion. Complete human-first fields before using Copilot. Do not require an accepted generated test.

Requirement: FR-05 Prevent practitioner conflict
Acceptance criterion: AC-04.1 / AC-04.2: "Same practitioner/exact time/SCHEDULED conflicts; another practitioner at the same time is allowed."
Behaviour to test: `AppointmentService.book_appointment` rejects a second SCHEDULED booking for the same practitioner at the exact same datetime with `ValueError`, and stores nothing new. A different practitioner at that time, or a slot whose earlier booking was cancelled, is allowed.
Human-first test idea/categories: (1) Valid: DR2 at the same time → stored. (2) Invalid: DR1 again at the same time → `ValueError` and store unchanged. (3) Boundaries: one minute later is allowed; a cancelled booking does not block the slot; a different patient with the same practitioner still conflicts. Recorded as T-SVC-12, T-SVC-13, T-SVC-14 and T-SVC-17 before Copilot was used.
Prompt and purpose: The handout Part F prompt, with the Requirement and Acceptance criterion fields filled in exactly as above. Purpose: compare Copilot's candidates with our human-first design.

> **[TO DO, member running Copilot]** Paste the prompt into GitHub Copilot Chat with your own account. Then fill one entry below for each significant candidate it gives. Run any candidate you keep and record the real result. Do not fill these in until Copilot has actually been used.

For each significant candidate, copy this entry as needed:
- Copilot test idea/candidate: [complete]
- What it claims to verify: [complete]
- Requirement trace: [complete]
- Assertion quality: [complete]
- Human critique: [complete]
- Decision: [Accept / Modify / Reject]
- Reason: [complete]
- Final test reference if accepted/modified: [link or not retained]
- Actual verification result: [complete; do not claim an unrun test passed]

Before accepting: traces to a requirement/criterion; can fail for the right reason; assertion checks required behaviour; no invented business rule; no unnecessary private implementation dependence. Reject/modify weak assertions, invented requirements, excessive mocking, duplicates, wrong exceptions, obsolete architecture and unnecessary dependencies.

## I Weak Copilot Test Reflection

> **[TO DO after H]** Answer from the actual Copilot output. Things to look for: a candidate that only checks `pytest.raises` without checking the store afterwards, one that uses `is not None`, an invented duration or patient-conflict rule, or one that reads `store._appointments` directly.

Which Copilot-generated test looked convincing but was weak? [response]
Why was it weak? [response]
How did you strengthen it? [response]
Accepted / modified / rejected test decisions and evidence: [link actual decisions in H]

## J Regression Run

Run python -m pytest from project/. Retain all accumulated tests. Record the tested SHA accurately.

| Command | Working directory | Code SHA | Passed | Failed | Failure summary | Product defect / test defect / unresolved | Evidence and interpretation |
|---|---|---|---|---|---|---|---|
| `python3 -m pytest` (baseline) | `project/` | 1e9cc49 (main after Stage 6, PR #7) | 28 | 0 | None | None | Stage 6 baseline intact: 8 supplied + 20 Stage 6 tests. Python 3.14.3, pytest 8.3.5 |
| `python3 -m pytest` (with Stage 7 tests) | `project/` | Branch `test/stage07-regression-suite` on top of 1e9cc49; **[add branch commit SHA]** | 73 | 0 | None | None | 8 supplied + 38 service (20 Stage 6 + 18 Stage 7 cases) + 27 domain cases. Production code unchanged |
| `python -m pytest` (integrated) | `project/` | **[main SHA after merging the Stage 7 PR]** | [complete] | [complete] | [complete] | [complete] | [Each member pulls main and records their own run] |

Individual test runs and changed-order independence evidence:
- `python3 -m pytest tests/test_domain.py::test_cancel_changes_status` → 1 passed
- `python3 -m pytest tests/test_services.py::test_same_practitioner_one_minute_later_is_allowed` → 1 passed
- All 60 test functions passed as node IDs in reverse order, and again in shuffled order → 73 passed each time
- Files in a different order: `python3 -m pytest tests/test_services.py tests/test_domain.py tests/test_starter.py` → 73 passed
Optional tutor-led demonstration notes: Not used in class. As a private sanity check (not assessed), we temporarily changed `Appointment.cancel` to allow COMPLETED → CANCELLED. T-DOM-14 and the Stage 6 COMPLETED test failed. We also temporarily widened the conflict check to the same day, and T-SVC-14 failed. The code was restored and the full suite rerun: 73 passed.
A meaningful test should detect a relevant incorrect result. Students do not have to perform the demonstration or submit failure/restoration evidence for assessment. The tutor restores the example and reruns its tests. This is not a Stage 8 fault activity.
Requirement → test → failure/observation → diagnosis → change → verification: FR-05 AC-04.1 → T-SVC-14 → failed when the conflict rule was temporarily widened to "same day" → diagnosis: a product defect against the "exact time" criterion (the test was correct) → change reverted → full suite 73 passed. No real product or test defects were found in the Stage 6 code.

## K What the Suite Still Does Not Prove

What does your test suite still not prove? Behaviour across sessions (data is in-memory only); the console menu and `main.py` user flow; Stage 9 queries (`list_practitioner_appointments` still raises `NotImplementedError` and is untested by design); any input we did not think of; and validation that SmartCare meets the clinic's real needs. Passing tests show only the scenarios we wrote.
Coverage if used: Not used.
Which uncovered areas matter, and why does coverage percentage alone not establish correctness? Coverage was not measured. Even so, the areas above matter more than a percentage: coverage would show that lines ran, not that our assertions match the acceptance criteria.
Optional fixtures/parametrisation used and why, if any: `@pytest.mark.parametrize` is used for blank IDs/names, practitioner fields, invalid date/times and unknown participants. Each input is a different invalid case of the same rule, so one test function covers them without copy-paste. No fixtures: plain helper functions (`make_participants`, `make_services`) create fresh state in each test, matching the Stage 6 style.

## L Git and Review Evidence

Use links rather than copying GitHub history. Continue the Stage 6 workflow; no commit/PR count, conflict or individual test quota is imposed.

| Issue/task | Branch | PR | Reviewer | Key feedback | Outcome |
|---|---|---|---|---|---|
| https://github.com/Khuzaimah876/st1-assignment-3/issues/8 | `test/stage07-regression-suite` | [PR link] | [different member] | [complete] | [complete] |

## M Contribution Evidence

Record actual work in test design, implementation, review, traceability, diagnosis, necessary fixes and integration. Do not include confidential peer ratings.

| Member | Actual contribution | Evidence link |
|---|---|---|
| Khuzaimah (Khuzaimah876) | [e.g. added test_domain.py and the Stage 7 service tests; drafted the traceability matrix; ran the regression and order checks; disclose AI assistance] | [commit/PR link] |
| Aditya Vungarala (u3321194) | [complete] | [link] |
| Manit Mahajan (CEOOFINDIA) | [complete] | [link] |

## N Formative Questions

1. What question does verification answer?
"Did we build the product right?" In other words, does the implementation meet the specified requirements and acceptance criteria?

2. What question does validation answer?
"Did we build the right product?" In other words, does the specified product meet the users' real need?

3. What is a unit test?
An automated test of one small unit, such as one object or method, in isolation. It checks one behaviour with a clear expected result, e.g. `Appointment.cancel()` changing SCHEDULED to CANCELLED.

4. What is a pytest fixture?
A function marked `@pytest.fixture` that provides setup (such as a fresh store) to the tests that ask for it by parameter name. A function-scoped fixture gives every test new state.

5. What is parametrisation in pytest?
`@pytest.mark.parametrize` runs the same test function once for each listed input. Each run is reported separately, e.g. blank, tab and `None` IDs.

6. What is regression testing?
Rerunning the whole accumulated test suite after a change, to check that behaviour which used to work still works.

7. What does code coverage tell us, and what does it not prove?
It shows which lines or branches ran during the tests. It does not prove the assertions are meaningful, that requirements are correct or complete, or that missing behaviour has been tested.

8. What makes an assertion weak?
It could pass while the required behaviour is broken. Examples: `assert True`, `is not None`, `len(x) > 0`, catching a broad exception, or not checking state after a rejected operation.

9. What is the appropriate role of GitHub Copilot as a test assistant?
To suggest candidate test ideas after we have done our own design. Humans check each candidate against the requirement, reject invented rules or weak assertions, and run the tests themselves. Copilot does not decide what counts as evidence.

10. What is the Stage 7 engineering rule?
Every test must trace to a real requirement or contract and be able to fail for the right reason. Record the results honestly, and never change production code or delete tests just to get a green run.

## O Stage Completion

Tested Stage 7 main SHA: [complete after merge]
Full-suite result: [complete after merge; expected 73 passed if nothing else changes]
Unresolved defects and effect on baseline: None found. Stage 9 `list_practitioner_appointments` and the console TODOs are intentionally incomplete and outside Stage 7.
Clean working tree and integration evidence: [each member: `git status` clean on main + their pytest result]
Stage 8 handover status: Same application, 73-test regression suite and this traceability matrix are handed over; no Stage 8 work done.
All tutorial/formative responses and traceability/Copilot decisions complete: [confirm once H, I, L, M and O are filled]