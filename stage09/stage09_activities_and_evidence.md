# Stage 9 activities and evidence

Common UG and PG record. All Assignment 3 stage materials are provided from the beginning. Complete this stage only after the previous applicable stage has been integrated, verified and recorded. Use this supplied record in stage09/ in your EXISTING repository. Preserve project/, all earlier tests, records and responses. Do not download another starter or copy staff solutions. Use the Stage 9 handout and Overview/revision 2 baseline. Keep responses concise and link accessible artefacts; do not paste entire logs or private peer ratings.

Group: Thursday 2:30–4:30pm tutorial, Group 6
Members and responsibilities: Aditya Vungarala (UG): human review and approval of PR #16; Khuzaimah (Khuzaimah876, UG): merged PR #16; Manit Mahajan (CEOOFINDIA, UG): Stage 9 implementation and this record.
Stage 8 integrated SHA, command, working directory and actual result: f87e8b62e5242318918c606fcd11604d48d54db2 (merge of PR #14); python3 -m pytest -q in project/ → 75 passed (as recorded in the Stage 8 record)

## A. Tutorial activities

### A1 Session state classification

| Information | Required session/domain or transient state? | Requirement or reason |
|---|---|---|
| Patient identity |Required session/domain state |FR-01/02 and BR-01: appointments must point at a real registered patient (BR-04) |
| Appointment history |Required |FR-07/08 and BR-06/07: a cancelled appointment stays retrievable for the session. |
| Temporary menu choice |Transient |It only drives one pass of the menu loop. No requirement needs it afterwards. |
| Practitioner specialty |Required |FR-03 makes specialty part of a practitioner’s registration, and the Practitioner object stores it. | 
| Debug print output |Transient |It’s diagnostic text for a developer. Nothing in the requirements depends on it. |
| Appointment status |Required |SCHEDULED, CANCELLED and COMPLETED (BR-08) drive cancellation, conflicts and filtering. |

What is intentionally lost on exit?  All patients, practitioners and appointments are kept in memory only, so everything is lost when the program closes. Transient items such as the menu choice and debug output are never kept at all.

### A2 Interface and domain data plan

Plan before AI. This replaces schema/key design; no database tables are required.

| Function or component | Explicit inputs and types | Outputs | Responsibility and validation | Domain source / existing constraint |
|---|---|---|---|---|
| appointment_sort_key |One Appointment |A (datetime, str) pair: date/time, then appointment ID |Describes the ordering only. It checks nothing, because the domain already validated the appointment when it was built. It has no side effects. |Appointment.date_time is naive and minute precision. appointment_id is a trimmed string. |
| select_appointments |list[Appointment], practitioner_id: str, status: AppointmentStatus None |A new, sorted list[Appointment] holding the same objects |Filters by practitioner, then by status if one is given, then sorts with the named key. It assumes valid inputs and doesn’t decide whether the practitioner is registered. It doesn’t mutate the source or print. |Uses appointment.practitioner.practitioner_id and the AppointmentStatus enum. |
| Service listing |practitioner_id: str, status: AppointmentStatus None |A new sorted list. [] is a valid result. |Validates the ID and checks the practitioner exists. It checks the status is an enum or None, then gets the appointments from the store and calls the query with the registered ID. |The existing ID contract and the store’s lookup. |
| Console |Typed text: menu choice, IDs, date/time, status text |Printed messages |Prompts, converts status text to an enum and date text with parse_date_time, then calls services and prints. It catches ValueError and LookupError so the loop continues. It holds no business rules. |The strict YYYY-MM-DD HH:MM parser and the service contracts. |

Relate patient ID/name, practitioner ID/name/specialty, and appointment ID/actual participants/date_time/status to the existing contracts: Patient and practitioner: IDs are strings, trimmed, non-blank and case-sensitive. Names and specialty are required and non-blank. Appointment ID: unique among appointments. Participants: an appointment holds the actual registered Patient and Practitioner objects, not their ID strings. Time: date_time is a naive local datetime with no seconds. Status: a AppointmentStatus enum value, never plain text.

### A3 Responsibility violations

| Conceptual case | Violation | Correct boundary and reason |
|---|---|---|
| Appointment.cancel reads input |A domain object is doing user interaction. Its rule now can’t run without someone typing, so it’s hard to test and can’t be reused by any other interface NFR-02/03. |Appointment.cancel only checks is this SCHEDULED? and changes the status, raising ValueError if not. The console asks for the ID, and the service finds the appointment and calls cancel |
| Service prints/reads the menu |The service is mixing workflow coordination with presentation. A test of booking would have to fake keyboard input or capture output. |The service takes plain arguments and returns objects or raises ValueError or LookupError. Only the console prompts and prints. |
| Query sorts its source in place |appointments.sort(...) changes the caller’s list, which is a hidden side effect. It breaks the rule that source order stays unchanged QRY-03, FP-01, FP-02, and the next caller sees a surprise. |The query builds a new list and returns it, for example with sorted(...), so the source is left alone. |
| Store prints Appointment saved |The store’s job is only to hold the session’s collections. Printing is presentation, so it creates hidden output that clutters tests and ties storage to one kind of screen. |The store stores and returns. If a message is wanted, the console prints it after the service call succeeds. |

### A4 Sorting comparison

For `appointments.sort(key=appointment_sort_key)` and `result = sorted(appointments, key=appointment_sort_key)`, predict source order, return value and result identity. Give a meaningful mutation check: appointments.sort(key=appointment_sort_key) sorts the original list in place and returns None. The source order changes, and anyone using that list sees the change. result = sorted(appointments, key=appointment_sort_key) creates and returns a new sorted list. The original list stays unchanged, and result is not appointments is True. Both lists still contain the same Appointment objects. Mutation check: Start with an unsorted appointments list and save a copy of its original order. After running the query, check that the source list still matches the copy and that the result is a different list. This catches accidental changes to the original list.

Score-example prediction and explanation of passing the named key: For scores = [('Bea', 8), ('Ali', 8), ('Chen', 5)], using sorted(scores, key=score_key) with (score, name) as the key gives: [('Chen', 5), ('Ali', 8), ('Bea', 8)] Chen comes first because 5 is the lowest score. Ali comes before Bea because their scores are equal, so the name breaks the tie. Using key=score_key passes the function to sorted(), which calls it for each item. Using key=score_key() calls the function immediately instead, which is incorrect.

### A5 Exit question

Explain cancellation versus deletion, and checks for same-session lookup, all-status listing and SCHEDULED-only exclusion: Cancellation changes the appointment’s status to CANCELLED and keeps the same object in the store, instead of deleting it, because FR-07 and BR-06/07 require cancelled history to stay available for the session, and because deleting it would lose the record of what was booked. To show this, I’d cancel an appointment and look it up by ID to check I get the same object (is) with CANCELLED status, then list the practitioner’s appointments with no status filter to check the cancelled one still appears in the right order, and check the store’s collection still holds it. A SCHEDULED-only list should omit it because its status no longer matches that filter (QRY-02), so I’d list with SCHEDULED and confirm it’s absent, then with CANCELLED and confirm it’s present. The store keeps everything, and the query decides what to show. 

## B. Human design and contracts

Complete before GitHub Copilot. Record any interface/integrity decision and its reasoning: Decisions made before the Copilot review: (1) select_appointments only filters and sorts appointments. It doesn't check whether a practitioner is registered because that's the service's job. This keeps the query simple and easy to test. (2) The console converts status text into an AppointmentStatus enum, while the service checks that the value is valid and raises ValueError if it isn't. (3) The service passes the registered practitioner’s actual ID to the query, so IDs with extra spaces don’t cause incorrect results. (4) The menu creates the store and services once and reuses them throughout the session so records aren’t lost. (5) The console catches ValueError and LookupError to show expected errors and return to the menu without hiding actual bugs. Tests also check that failed operations leave the stored data unchanged.


| Requirement | Input / session data | Operation and responsible component | Expected result or error | Test / evidence |
|---|---|---|---|---|
|QRY-01 |List with D1’s and D2’s appointments, requested ID D1 |select_appointments (pure query) |Only D1’s appointments; D2’s are the control and are excluded |test_select_returns_only_the_requested_practitioner |
|QRY-02 |Appointments with SCHEDULED, CANCELLED and COMPLETED, status omitted or one enum value |select_appointments |Omitted or None gives every status; an enum gives only that status; no match gives a new [] |test_select_default_status_includes_every_status, test_select_explicit_status_keeps_only_that_status, test_select_status_with_no_matches_returns_new_empty_list |
|QRY-03 |Unsorted list, and equal-time cancelled/completed fixtures with IDs A3, A1, A2 |select_appointments using appointment_sort_key |Ascending by (date/time, ID); source order and fields unchanged |test_select_orders_by_date_time_ascending, test_select_breaks_equal_times_by_appointment_id, test_select_does_not_change_source_order_or_objects |
|QRY-04 |Store with D1 registered, plus unknown, blank and non-enum inputs |list_practitioner_appointments (service) | No matches gives a new []. Unknown ID raises LookupError. Blank ID or non-enum status raises ValueError. Records unchanged after failure.|test_listing_known_practitioner_without_appointments_is_empty, test_listing_unknown_practitioner_raises_lookup_error, test_listing_non_enum_status_raises_value_error, test_failed_listing_leaves_records_unchanged |
|FP-01 |Same inputs called twice |select_appointments |Same result both times; no store, printing or mutation |test_select_is_repeatable_for_unchanged_inputs, test_select_does_no_input_output, plus a code read |
|FP-02 |Empty, already-sorted and unsorted lists |select_appointments |A distinct list each time, holding the same unchanged objects |test_select_returns_distinct_list_for_empty_input, test_select_returns_a_new_list_with_the_same_objects, test_select_unsorted_result_is_not_the_source_list |
|FP-03 |One appointment, and a spy key |appointment_sort_key |Returns (date_time, appointment_id), and the query really uses it |test_sort_key_is_date_time_then_appointment_id, test_select_uses_the_named_key_for_ordering |
|UI-01 |One session store with P1, D1, D2 and the demo bookings |Console calls the services; the services apply the rules |Conflict rejected, other practitioner allowed, cancellation shows CANCELLED, all-status then SCHEDULED-only lists, freed slot rebooked |test_console_ui01_demonstration_sequence, test_service_workflow_register_book_cancel_list_rebook, test_subprocess_interactive_session_end_to_end |
|UI-02 |Bad menu choice, blank/unknown/duplicate IDs, bad date, repeat cancel, bad status |Console catches ValueError and LookupError; the services reject |Each error is reported, the menu continues, no partial state, and a failed booking doesn’t reserve its ID |test_console_recovers_from_invalid_input_without_changing_state, test_console_failed_booking_does_not_reserve_the_id, test_service_rejections_preserve_state_and_reserve_nothing|

Cover QRY-01–04, FP-01–03, UI-01–02 and relevant FR-01–09. Explain empty versus unknown versus invalid, enum conversion, actual object identity, error handling and unchanged state on rejection: The queries and menu cover FR-01 to FR-09, QRY-01 to QRY-04, FP-01 to FP-03 and UI-01 to UI-02. The service handles registration, lookup, booking, conflicts and cancellation, while Stage 9 adds appointment listing and the menu. There are three different outcomes: empty means the practitioner exists but has no matching appointments, so an empty list is returned. Unknown means the practitioner ID does not exist, so a LookupError is raised. Invalid means the input is incorrect, such as a blank ID or invalid status, so a ValueError is raised. Status text is converted into an AppointmentStatus enum at the menu level. The service only accepts an enum or None, preventing invalid text from silently passing through. The queries return the actual stored Appointment objects, not copies. Tests use is to confirm object identity. They also use sorted() and appointment_sort_key to return a new sorted list without changing the original. Finally, the menu catches expected errors and displays a message instead of crashing. Tests also check that rejected operations leave the stored data unchanged and do not reserve appointment IDs.

## C. Implementation and query verification

| Requirement / test ID | Code location | Case and meaningful assertion | Actual result | Evidence link |
|---|---|---|---|---|
|QRY-01 practitioner isolation |queries.py select_appointments |D1 and D2 appointments in one list; the D1 result equals [mine] and excludes the D2 control (test_select_returns_only_the_requested_practitioner, test_listing_excludes_other_practitioners) |PASSED: python -m pytest -q from project/ on main at 9d738a7 (132 passed in 0.26s) |https://github.com/Khuzaimah876/st1-assignment-3/blob/9d738a70ed57caba0996738d09a2149cd9aac334/project/tests/test_queries.py |
|QRY-02 default all and each enum |select_appointments |None or omitted status returns all three statuses; each enum returns exactly its own appointment; an unmatched status returns a new [] (test_select_default_status_includes_every_status, test_select_explicit_status_keeps_only_that_status, test_select_status_with_no_matches_returns_new_empty_list) |PASSED: python -m pytest -q from project/ on main at 9d738a7 (132 passed in 0.26s) |https://github.com/Khuzaimah876/st1-assignment-3/blob/9d738a70ed57caba0996738d09a2149cd9aac334/project/tests/test_queries.py |
|QRY-03 order and tie-break |appointment_sort_key, select_appointments |Unsorted input comes back earliest first. Equal-time cancelled/completed fixtures come back A1, A2, A3 by ID. Time is compared before ID (test_select_orders_by_date_time_ascending, test_select_breaks_equal_times_by_appointment_id, test_select_time_beats_id_in_ordering) |PASSED: python -m pytest -q from project/ on main at 9d738a7 (132 passed in 0.26s) |https://github.com/Khuzaimah876/st1-assignment-3/blob/9d738a70ed57caba0996738d09a2149cd9aac334/project/tests/test_queries.py |
|FP-03 named-key reuse |appointment_sort_key |The key equals (date_time, appointment_id). A spy key that orders by ID changes the result order, so the query really uses it (test_sort_key_is_date_time_then_appointment_id, test_select_uses_the_named_key_for_ordering) |PASSED: python -m pytest -q from project/ on main at 9d738a7 (132 passed in 0.26s) |https://github.com/Khuzaimah876/st1-assignment-3/blob/9d738a70ed57caba0996738d09a2149cd9aac334/project/tests/test_queries.py |
|FP-01 repeated calls and no I/O |select_appointments |Two calls on unchanged input give equal results, and capsys shows nothing was printed (test_select_is_repeatable_for_unchanged_inputs, test_select_does_no_input_output) |PASSED: python -m pytest -q from project/ on main at 9d738a7 (132 passed in 0.26s) |https://github.com/Khuzaimah876/st1-assignment-3/blob/9d738a70ed57caba0996738d09a2149cd9aac334/project/tests/test_queries.py |
|FP-02 fresh lists |select_appointments |Empty, already-sorted and unsorted inputs each return a list that is not the source and holds the same objects (test_select_returns_distinct_list_for_empty_input, test_select_returns_a_new_list_with_the_same_objects, test_select_unsorted_result_is_not_the_source_list) |PASSED: python -m pytest -q from project/ on main at 9d738a7 (132 passed in 0.26s) |https://github.com/Khuzaimah876/st1-assignment-3/blob/9d738a70ed57caba0996738d09a2149cd9aac334/project/tests/test_queries.py |
|Source unchanged |select_appointments, appointment_sort_key |Order, identity and fields are snapshotted before the call and compared after (test_select_does_not_change_source_order_or_objects, test_sort_key_does_not_change_the_appointment) |PASSED: python -m pytest -q from project/ on main at 9d738a7 (132 passed in 0.26s) |https://github.com/Khuzaimah876/st1-assignment-3/blob/9d738a70ed57caba0996738d09a2149cd9aac334/project/tests/test_queries.py |
|QRY-04 known-empty |services.py list_practitioner_appointments |Known practitioner with no appointments, or no matching status, returns a new [] and no error (test_listing_known_practitioner_without_appointments_is_empty, test_listing_no_matching_status_is_empty_not_an_error) |PASSED: python -m pytest -q from project/ on main at 9d738a7 (132 passed in 0.26s) |https://github.com/Khuzaimah876/st1-assignment-3/blob/9d738a70ed57caba0996738d09a2149cd9aac334/project/tests/test_queries.py |
|QRY-04 unknown and invalid |list_practitioner_appointments |Unknown ID raises LookupError; blank or non-text ID raises ValueError; a non-enum status such as 'scheduled' raises ValueError (test_listing_unknown_practitioner_raises_lookup_error, test_listing_blank_or_invalid_id_raises_value_error, test_listing_non_enum_status_raises_value_error) |PASSED: python -m pytest -q from project/ on main at 9d738a7 (132 passed in 0.26s) |https://github.com/Khuzaimah876/st1-assignment-3/blob/9d738a70ed57caba0996738d09a2149cd9aac334/project/tests/test_queries.py |
|Retained history and identity |list_practitioner_appointments, store |After cancellation the default and CANCELLED lists include the same object, and the SCHEDULED list omits it. Padded IDs still match (test_listing_keeps_cancelled_history_for_default_and_cancelled, test_listing_returns_stored_objects_in_order, test_listing_trimmed_practitioner_id_still_finds_appointments) |PASSED: python -m pytest -q from project/ on main at 9d738a7 (132 passed in 0.26s) |https://github.com/Khuzaimah876/st1-assignment-3/blob/9d738a70ed57caba0996738d09a2149cd9aac334/project/tests/test_queries.py |
|Rejection leaves state unchanged |list_practitioner_appointments |Records snapshotted before and after a failed request are equal (test_failed_listing_leaves_records_unchanged) |PASSED: python -m pytest -q from project/ on main at 9d738a7 (132 passed in 0.26s) |https://github.com/Khuzaimah876/st1-assignment-3/blob/9d738a70ed57caba0996738d09a2149cd9aac334/project/tests/test_queries.py |

Include practitioner isolation, every enum status/default all, equal-time ID tie-break, named-key reuse, repeated calls, empty/already-sorted fresh lists, unchanged source order/fields, known-empty/unknown/invalid service cases and retained history.

Purity explanation from code inspection, including absence of hidden state and I/O: select_appointments is pure because everything it uses comes in through its arguments and everything it produces goes out through its return value. It has no module-level variable, no store reference and no input() or print(). It loops over the list it’s given and only reads each appointment’s practitioner ID and status. It collects matches into a new local list and returns sorted(...) of that list, so the caller’s list and the objects in it are never modified. appointment_sort_key just reads two fields and returns them, with no side effects.
What the tests do and do not establish: The tests show that for the inputs I chose, the query selects the right practitioner and status, orders correctly, returns a new list holding the same objects, leaves the source order and fields unchanged, prints nothing, and gives the same answer on repeat calls. The service tests show that unknown, invalid and empty cases are kept apart and that failed requests leave the records unchanged. They don’t prove purity in general, because I can only check the cases I thought of, and a hidden global or side effect in a case I didn’t test could go unnoticed, which is why the code inspection is also needed. They also don’t prove the requirements themselves are the right ones (validation versus verification), and they say nothing about the interactive console. That is what D covers.

## D. Integrated console and workflow evidence

| Scenario / acceptance ID | Reproducible inputs / artefact | Expected result | Observed result and state check | Evidence link |
|---|---|---|---|---|
| UI-01 full menu workflow |Run python main.py --interactive from project/. Register P1, D1 and D2. Book A1, test a conflicting booking with D1, then book A2 with D2. Cancel A1, find it, list appointments with blank and scheduled status, rebook the freed slot with A3 and exit. |Registration and lookups work. Same-practitioner conflicts are rejected, different practitioners can share a time slot, cancelled appointments remain in history, status filtering works and freed slots can be rebooked. |All matched. A1 was booked and cancelled. A2 was successfully booked with D2 after the D1 conflict was rejected, proving the failed attempt did not reserve its ID. Listing showed cancelled and scheduled appointments correctly. A3 successfully used the freed slot. Exit confirmed session data was discarded. IDs are case sensitive. |test_console_ui01_demonstration_sequence, test_subprocess_interactive_session_end_to_end; https://github.com/Khuzaimah876/st1-assignment-3/blob/9d738a70ed57caba0996738d09a2149cd9aac334/project/tests/test_workflows.py. |
| UI-02 invalid-input recovery |Three sessions testing invalid menu choices, blank IDs, unknown patients and practitioners, duplicate registration, malformed and impossible dates, duplicate appointment IDs, unknown appointments, repeated cancellation and invalid statuses. Restart and search for P1. |Each rejection displays a clear error, the menu continues, no partial state is stored and failed bookings do not reserve IDs. A new session starts empty. |All expected errors appeared. Four failed A1 bookings were followed by a successful A1 booking. Duplicate bookings did not overwrite the original appointment. Repeated cancellation preserved the cancelled appointment. Restarting correctly returned "Patient not found" for P1. |test_console_recovers_from_invalid_input_without_changing_state, test_console_failed_booking_does_not_reserve_the_id, test_subprocess_new_session_starts_empty; https://github.com/Khuzaimah876/st1-assignment-3/blob/9d738a70ed57caba0996738d09a2149cd9aac334/project/tests/test_workflows.py |
| Automated service workflow |Run python -m pytest -q from project/. Integrated workflow in tests/test_workflows.py |Duplicate, unknown and conflict rejections preserve state. Different practitioners are allowed. Cancelled history is retained, filtering works and freed slots can be rebooked |132 tests passed in 0.21 seconds before committing. Rejected operations were checked against before-and-after state snapshots. |test_service_workflow_register_book_cancel_list_rebook, test_service_rejections_preserve_state_and_reserve_nothing https://github.com/Khuzaimah876/st1-assignment-3/blob/9d738a70ed57caba0996738d09a2149cd9aac334/project/tests/test_workflows.py. |

Include registration/find, booking, conflict rejection, different-practitioner booking, cancellation, retrieval, listing/filtering, freed slot and exit; duplicate/unknown/blank IDs, malformed/impossible date, invalid status, unknown choice and repeated cancellation. Identify before/after state and subsequent successful action.

## E. GitHub Copilot review and human decisions

Human design completed before AI: A1–A5 and B in this record were completed before the Copilot session. The Stage 9 implementation and the draft record text were produced with Claude's help, then run, tested and checked by me against the requirements, as disclosed in the PR #17 description.
Actual prompt/context supplied: Act as a code reviewer for SmartCare, an in-memory Python appointment app. Review the supplied `queries.py`, `services.py` and `tests/test_queries.py` (132 tests currently pass). Check query purity, validation, error handling, object identity, enum filtering, sorting, source non-mutation, component responsibilities, appointment history and missing tests. Confirm that queries return a new sorted list without modifying stored data, and that services raise the correct errors or return an empty list when appropriate. Identify any workflow, console or data integrity risks. Rank findings as Critical, Important or Optional, reference the relevant code and tests, and separate actual issues from optional improvements. Don't invent requirements, redesign the domain or introduce new frameworks.

Actual response: 
```text
SmartCare Query and Console Integration Review

Scope reviewed

queries
services
test_workflows

Review performed against the stated contracts:

Query returns a new list
Filters by practitioner and optional status
None status means all statuses
Ordering uses (date_time, appointment_id) via appointment_sort_key
Source collection and appointment objects are not modified
Service raises:
LookupError for unknown practitioner
ValueError for blank ID or non-enum status
Returns [] when no matches exist
Executive Summary
Critical

No critical defects are evidenced in the supplied files.

Important

Several contract points are implemented but are not directly proven by the supplied tests, particularly around query purity, list identity, object identity preservation, and ordering edge cases.

Optional

A number of additional query and console tests could strengthen regression protection and better demonstrate compliance with the stated requirements.

1. Explicit Inputs, Purity and Source Non-Mutation
Observed Evidence
Query is explicit and dependency-free

select_appointments() receives all required inputs as parameters:

Python
def select_appointments(
appointments,
practitioner_id,
status=None
)

No datastore, console, global state or I/O is accessed.

Query performs read-only processing

The implementation:

Python
selected = []
...
selected.append(appointment)
return sorted(selected, key=appointment_sort_key)

creates a new result list and never assigns to appointment fields or the input collection.

Service delegates collection processing to query

AppointmentService.list_practitioner_appointments() retrieves data and calls:

Python
return select_appointments(
self.data_store.list_appointments(),
practitioner.practitioner_id,
status,
)

This is a clean separation between workflow and collection selection logic.

Finding
Important: Source non-mutation contract is not directly tested

The implementation appears pure, but the supplied tests do not explicitly verify:

source appointment list unchanged
source ordering unchanged
appointment objects unchanged
returned list is a distinct list object
Evidence to Check

Look for tests proving:

Python
result is not source_list

and:

Python
source_before == source_after

and:

Python
result[0] is original_appointment

I do not see such tests in the supplied workflow tests.

2. Domain, Service, Data-Store and Console Responsibilities
Observed Evidence
Query responsibility

The query only:

filters
sorts
returns data

No validation, persistence or UI behaviour appears in the query.

Service responsibility

The service:

validates status type
resolves practitioner existence
coordinates workflow
invokes the query

without performing console I/O.

Console boundary behaviour

Workflow tests verify:

textual status inputs
invalid menu choices
user error reporting
session continuation after failures

Examples:

Python
'8', 'D1', 'scheduled'

and

Python
'8', 'D1', 'done'

demonstrate conversion and validation occurring at the UI boundary.

Finding
Important: Responsibility separation appears correct

No evidence was found that:

queries touch the datastore
services perform console I/O
console directly manipulates stored appointments

based on the supplied files.

3. Validation and Recovery Without Partial State Changes
Observed Evidence
Booking failures preserve state

The test:

Python
before = stored_state(store)
...
assert stored_state(store) == before

covers:

duplicate IDs
unknown patient
unknown practitioner
practitioner conflict
invalid time

and verifies no store mutation occurred.

Failed booking does not reserve IDs

The test demonstrates:

Python
A1

can be booked after an earlier failed attempt.

Console recovery

The console test intentionally chains many failures and continues operating successfully afterward.

Finding
Important: Strong evidence of recovery behaviour

The supplied tests provide good evidence that invalid operations do not leave partial state changes behind.

4. Correct Object Identity, Enum Filtering and Ordering
Observed Evidence
Enum filtering uses identity
Python
if status is not None and appointment.status is not status:
continue

This is consistent with enum identity comparison.

Service validates enum type
Python
if status is not None and not isinstance(status, AppointmentStatus):
raise ValueError(...)

This satisfies the stated non-enum rejection contract.

Ordering key
Python
return appointment.date_time, appointment.appointment_id

matches the contract.

Ordering behaviour evidence

Console tests verify chronological ordering and retention of cancelled history.

Findings
Important: Object identity preservation is not directly tested

The query appends existing objects:

Python
selected.append(appointment)

so identity should be preserved.

However I do not see a test proving:

Python
returned_obj is stored_obj
Evidence to Check

Look for assertions similar to:

Python
assert result[0] is appointment

or:

Python
assert all(x is y ...)

None are visible in the supplied tests.

Important: Secondary ordering by appointment_id is not directly tested

The implementation correctly uses:

Python
(date_time, appointment_id)

I do not see a test where two appointments share the same datetime and practitioner, requiring tie-breaking on appointment ID.

Evidence to Check

A test with:

Python
A2 @ 09:00
A1 @ 09:00

for the same practitioner/history scenario would directly verify tie-breaking. No such proof appears in the supplied test file.

5. Retained History and Integrity Risks
Observed Evidence
Cancelled appointments remain stored

Workflow tests verify:

Python
assert appointments.list_practitioner_appointments('D1') == [first]

after cancellation.

Rebooking after cancellation

The tests demonstrate:

cancellation retains record
practitioner slot becomes available
new appointment can be booked

without deleting history.

Console listing includes cancelled history

Explicitly verified:

"The all-status listing keeps the cancelled history"

Finding
Important: History retention requirement is well supported

The tests strongly support the intended behaviour that cancellation changes status rather than removing records.

Optional: No explicit test that listing cannot mutate history

The query is implemented read-only.

However there is no direct test that repeated list operations leave appointment status and store contents unchanged.

Evidence to Check

A before/after snapshot around repeated listing calls.

6. Missing Query, Workflow and Console Tests
Important Missing Query Tests
Q1. Returned list is a new list

Evidence currently missing:

Python
assert result is not source_list

Reason: The contract explicitly requires a new list.

Q2. Source list order remains unchanged

Example check:

Python
before = list(source)
select_appointments(...)
assert source == before

Reason: Direct proof of non-mutation.

Q3. Returned objects are the same objects

Example:

Python
assert result[0] is appointment_a

Reason: Protects against accidental copying/reconstruction.

Q4. No matches returns empty list

Service contract mentions:

Python
[]

for known practitioner with no matches.

I see this exercised indirectly through status filtering, but not a dedicated query-level test.

Q5. Tie-break ordering by appointment_id

Verify:

Python
same datetime
A1 before A2

using appointment_sort_key.

Important Missing Service Tests
S1. Non-enum status raises ValueError

Contract implemented:

Python
not isinstance(status, AppointmentStatus)

I do not see a service-level test calling:

Python
list_practitioner_appointments("D1", "scheduled")

and asserting ValueError.

S2. Unknown practitioner raises LookupError

Implemented here:

Python
if practitioner is None:
raise LookupError(...)

I do not see a dedicated service test for this path.

Optional Console Tests
C1. Empty practitioner list result

Known practitioner with:

Python
no appointments

should display the appropriate empty-result message.

C2. Completed-status filter end-to-end

The console tests cover "completed" as a filter value, but only against data that appears not to contain completed appointments.

A test with an actual completed appointment would verify the full path.

C3. Repeated listing stability

Run multiple list commands and verify:

same output ordering
no status changes
no record creation
Ranked Findings
Critical
None evidenced from the supplied files.
Important
Query purity is implemented but not directly proven by tests.
Returned-list identity ("new list") is not directly tested.
Returned appointment object identity is not directly tested.
Secondary ordering by (appointment_id) for equal datetimes is not directly tested.
Service validation paths for non-enum status and unknown practitioner are implemented but not evidenced by dedicated tests.
Optional
Explicit query test for source-list immutability.
Explicit query test for empty-result behaviour.
Console test for practitioner with no appointments.
Console test with actual completed appointments.
Stability tests ensuring repeated listing operations never alter stored history.

Overall, the implementation shown in the supplied files appears consistent with the stated contracts. The main gaps are not in the code reviewed, but in direct test coverage of purity, identity preservation and ordering edge cases.
```

| AI finding | Code/test evidence | Severity | Accept/Modify/Reject and reason | Change or no change | Actual verification |
|---|---|---|---|---|---|
|Query purity and source order not tested |test_select_does_not_change_source_order_or_objects, test_select_unsorted_result_is_not_the_source_list |Important (Copilot) |Reject. These tests already exist. Copilot did not check test_queries.py. |No change. |Run python -m pytest tests/test_queries.py -v and record the result and commit SHA. |
|Returned list is not a new list |test_select_returns_a_new_list_with_the_same_objects, test_select_returns_distinct_list_for_empty_input |Important (Copilot) |Reject. Tests already check that the returned list is different from the source. |No change. |Same test run. |
|Returned object's identity not tested |test_select_returns_a_new_list_with_the_same_objects, test_listing_returns_stored_objects_in_order |Important (Copilot) |Reject. Both tests use is to check that the actual stored objects are returned. |No change. |Same test run. |
|Equal time appointment sorting not tested |test_select_breaks_equal_times_by_appointment_id |Important (Copilot) |Reject. The test checks that appointments with equal times are sorted by ID (A1, A2, A3). |No change. |Same test run. |
|Invalid status and unknown practitioner not tested |test_listing_non_enum_status_raises_value_error, test_listing_unknown_practitioner_raises_lookup_error |Important (Copilot) |Reject. Both cases already have dedicated tests. |No change. |Same test run. |
|Empty query results not tested |test_select_status_with_no_matches_returns_new_empty_list, test_select_unmatched_practitioner_returns_empty_list |Important (Copilot) |Reject. Both empty result cases are already tested. |No change. |Same test run. |
|Console test with a COMPLETED appointment |run_menu cannot create COMPLETED appointments through the menu. |Optional (Copilot) |Reject. The menu does not support creating completed appointments, so this is outside the current workflow. The status filtering is already covered elsewhere. |No change. |Deferred. |
|Repeated console listing not tested |test_select_is_repeatable_for_unchanged_inputs |Optional (Copilot) |Reject. Query repeatability is already tested. A separate console test adds little value. |No change. |Deferred. |
|Known practitioner with no appointments at console level |Console tests show "No matching appointments", but do not specifically test a practitioner with zero appointments. |Optional (Copilot) |Defer. Small coverage gap; the known-empty case is already tested at service level (test_listing_known_practitioner_without_appointments_is_empty), so a console test adds little. |No change. |Deferred. |



Responsibility check: explain how domain invariants, shared-store collections, service coordination, pure queries and console effects remain separate: Each layer has its own responsibility. Domain objects (Patient, Practitioner and Appointment) handle their own validation, while Appointment.cancel() controls when an appointment can be cancelled. The shared store (SmartCareDataStore) holds and retrieves all records without handling business rules. Services coordinate the workflow by checking records, handling errors and calling domain methods. Queries handle filtering and sorting, returning a new list without changing the original data. Finally, the console handles user input, date and status conversion, printing messages and catching errors so the menu can continue. The tests follow the same separation, with domain, query, service and workflow tests checking each layer independently.

## F. Required reflections

1. Which integration concern was architectural rather than a filtering/sorting detail? The main architectural decision was deciding where each responsibility belongs. The query only filters and sorts appointments, so it doesn't know whether a practitioner is registered. That's handled by the service, which checks for an unknown practitioner (LookupError), validates the status enum and then passes the practitioner's ID to the query. The console simply converts the user's status input into an enum and calls the service. I also had to make sure the store and services were created once and reused throughout the session, rather than recreated every time the menu loop runs, otherwise the data would be lost.
2. Which Copilot suggestion did you reject as over-engineering, and why? I wouldn't say there was any real over-engineering in the Copilot response. Its main suggestions were about missing tests, which I rejected because those tests already existed in test_queries.py, a file its session hadn't seen. I also decided not to add the three optional console tests because they would add little extra coverage when the query behaviour was already tested. Overall, I didn't reject any suggestions for being over-engineered; I rejected them because the existing tests already covered the behaviour.
3. How did you prove cancelled appointments remain retrievable and listable in the same session? I cancelled A1, looked it up by ID and listed D1’s appointments in the same session using both the menu and automated tests. Looking up A1 still returned the original appointment with its status set to cancelled. The all-status list showed A1 alongside the newer A3, while the SCHEDULED-only list left A1 out. The tests confirm this by checking object identity (is) and comparing the store before and after. This is covered by test_listing_keeps_cancelled_history_for_default_and_cancelled and test_service_workflow_register_book_cancel_list_rebook

## G. Ten formative answers

1. What makes select_appointments pure, and what side effect breaks purity? Pure: select_appointments is pure because it only uses the arguments it receives and doesn't change anything outside the function. It would no longer be pure if it sorted the original list, modified an appointment, printed output, asked for user input or accessed a hidden store or global variable.
2. Which explicit inputs are needed, and why avoid a global store? The query needs the appointment list, practitioner ID and optional status. Using a global store would mean relying on hidden data, making it harder to test and reuse.
3. How can a new list reuse Appointment objects safely? The new list contains references to the original Appointment objects. That's fine because the query only reads them and never changes them. The tests check this using is and before-and-after snapshots.
4. Why use a named key, and what breaks equal-time ties? appointment_sort_key keeps the sorting rule in one place: (date_time, appointment_id). This means appointments with the same time are ordered by ID rather than depending on their original list order.
5. How do default and explicit status filters differ? If no status is provided, all appointments are included, even cancelled and completed ones. If a status is provided, only matching appointments are returned. The console converts text into an enum before passing it to the service.
6. How do empty, unknown practitioner and invalid filter cases differ? If a registered practitioner has no appointments, the query returns an empty list. An unknown practitioner ID raises LookupError, while blank or non-text IDs and invalid statuses raise ValueError.
7. Which console errors recover, and how is unchanged state checked? The console catches expected errors such as invalid dates, duplicate IDs, booking conflicts, repeated cancellations and unknown menu choices. It displays an error message and returns to the menu. Tests check that failed operations don't change the store or reserve IDs.
8. What is data integrity for registered participants, conflicts and history? Every appointment must reference real registered patient and practitioner objects. IDs must be unique, practitioners can't have overlapping scheduled appointments, and cancelling an appointment changes its status without deleting it. Failed operations leave the stored data unchanged.
9. What is Copilot's review role, and who verifies findings? Copilot acts as a reviewer, not the final decision-maker. We check its suggestions against the actual code and tests, then accept, modify or reject them. In this case, it reported missing tests because its session hadn't seen test_queries.py, so we rejected those findings based on the existing test evidence.
10. How do pure functions and OOP responsibilities work together? Objects manage state and their own rules, while pure functions handle filtering and sorting. Services coordinate the operations, and the console handles user input and output. This keeps responsibilities separate and makes each part easier to test.
## H. Review, completion and common handover

Issues and bounded branches: Code was developed on feature/stage9-queries and merged through PR #16. This record is on docs/stage09-record
PR/diff and another-member human reviewer: PR #16 (https://github.com/Khuzaimah876/st1-assignment-3/pull/16) was reviewed and approved by Aditya Vungarala (u3321194) on 5 November 2026, then merged by Khuzaimah876.
Review responses and Copilot comparison: The human reviewer ran the tests (132 passed), used the interactive menu including invalid inputs, checked query purity and service errors, and deliberately broke the sort key and status filter to confirm the tests caught it (3 and 9 failures). He approved with no defects found. Copilot mainly flagged missing tests, but its review had not included test_queries.py, where those tests already existed.
Integrated common Stage 9 SHA: 9d738a70ed57caba0996738d09a2149cd9aac334. This is the common version on main after merging PR #16.
Full regression command, working directory, actual count/result and evidence: python -m pytest -q, run from project/ on main at 9d738a7 → 132 passed in 0.26s. The reviewer independently ran python3 -m pytest -q (Python 3.14.1) on the PR branch → 132 passed, and Khuzaimah876 ran it on main after the merge → 132 passed.
README run instructions and scope/limitations: Run instructions are in the project README. The application still uses session-only data, case-sensitive IDs, strict YYYY-MM-DD HH:MM dates and has no patient-conflict rule.
Unresolved issues and support/action: Copilot's missing-test findings were rejected because the tests already existed. The optional console tests were deferred because they add little beyond existing coverage. The PR description's AI tool naming should be confirmed as corrected.
UG common candidate / PG future branch plan: The common Stage 9 version is protected at 9d738a70ed57caba0996738d09a2149cd9aac334. UG work continues from this version, while PG members create separate feature branches from the same SHA. PG changes do not alter the common Stage 9 candidate.

- [x] Query contracts, purity, new lists and named-key ordering verified.
- [x] Service empty/unknown/invalid cases and cancellation history verified.
- [x] Every console command and invalid-input recovery demonstrated.
- [x] Query and workflow tests plus all previous tests pass; actual evidence linked.
- [x] Human design, Copilot critique, review and integration recorded honestly.
- [x] Reflections and ten formative responses completed.
- [x] README updated; earlier code/tests/records preserved.
- [x] Common SHA protected for UG Stage 12; PG Stage 10/11 work deferred until approved.

No persistence, rescheduling or assurance implementation is part of Stage 9. UG: 6→7→8→9→12. PG: 6→7→8→9→10→11→12. Mixed groups keep one repository and protect the common candidate.
