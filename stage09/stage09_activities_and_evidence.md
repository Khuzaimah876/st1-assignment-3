# Stage 9 activities and evidence

Common UG and PG record. All Assignment 3 stage materials are provided from the beginning. Complete this stage only after the previous applicable stage has been integrated, verified and recorded. Use this supplied record in stage09/ in your EXISTING repository. Preserve project/, all earlier tests, records and responses. Do not download another starter or copy staff solutions. Use the Stage 9 handout and Overview/revision 2 baseline. Keep responses concise and link accessible artefacts; do not paste entire logs or private peer ratings.

Group: <!-- complete -->
Members and responsibilities: <!-- complete -->
Stage 8 integrated SHA, command, working directory and actual result: <!-- complete -->

## A. Tutorial activities

### A1 Session state classification

| Information | Type | Why |
|Information|Required session/domain or transient state?|Requirement or reason|
| Patient identity |Required session/domain state |FR-01/02 and BR-01: appointments must point at a real registered patient (BR-04) |
| Appointment history |Required |FR-07/08 and BR-06/07: a cancelled appointment stays retrievable for the session. |
| Temporary menu choice |Transient |It only drives one pass of the menu loop. No requirement needs it afterwards. |
| Practitioner specialty |Required |FR-03 makes specialty part of a practitioner’s registration, and the Practitioner object stores it. | 
| Debug print output |Transient |It’s diagnostic text for a developer. Nothing in the requirements depends on it. |
| Appointment status |Required |SCHEDULED, CANCELLED and COMPLETED (BR-08) drive cancellation, conflicts and filtering. |

What is intentionally lost on exit? <!-- All patients, practitioners and appointments are kept in memory only, so everything is lost when the program closes. Transient items such as the menu choice and debug output are never kept at all. -->

### A2 Interface and domain data plan

Plan before AI. This replaces schema/key design; no database tables are required.

| Function or component | Explicit inputs and types | Outputs | Responsibility and validation | Domain source / existing constraint |
|---|---|---|---|---|
| appointment_sort_key |One Appointment |A (datetime, str) pair: date/time, then appointment ID |Describes the ordering only. It checks nothing, because the domain already validated the appointment when it was built. It has no side effects. |Appointment.date_time is naive and minute precision. appointment_id is a trimmed string. |
| select_appointments |list[Appointment], practitioner_id: str, status: AppointmentStatus None |A new, sorted list[Appointment] holding the same objects |Filters by practitioner, then by status if one is given, then sorts with the named key. It assumes valid inputs and doesn’t decide whether the practitioner is registered. It doesn’t mutate the source or print. |Uses appointment.practitioner.practitioner_id and the AppointmentStatus enum. |
| Service listing |practitioner_id: str, status: AppointmentStatus None |A new sorted list. [] is a valid result. |Validates the ID and checks the practitioner exists. It checks the status is an enum or None, then gets the appointments from the store and calls the query with the registered ID. |The existing ID contract and the store’s lookup. |
| Console |Typed text: menu choice, IDs, date/time, status text |Printed messages |Prompts, converts status text to an enum and date text with parse_date_time, then calls services and prints. It catches ValueError and LookupError so the loop continues. It holds no business rules. |The strict YYYY-MM-DD HH:MM parser and the service contracts. |

Relate patient ID/name, practitioner ID/name/specialty, and appointment ID/actual participants/date_time/status to the existing contracts: <!-- Patient and practitioner: IDs are strings, trimmed, non-blank and case-sensitive. Names and specialty are required and non-blank. Appointment ID: unique among appointments. Participants: an appointment holds the actual registered Patient and Practitioner objects, not their ID strings. Time: date_time is a naive local datetime with no seconds. Status: a AppointmentStatus enum value, never plain text. -->

### A3 Responsibility violations

| Conceptual case | Violation | Correct boundary and reason |
|---|---|---|
| Appointment.cancel reads input |A domain object is doing user interaction. Its rule now can’t run without someone typing, so it’s hard to test and can’t be reused by any other interface NFR-02/03. |Appointment.cancel only checks is this SCHEDULED? and changes the status, raising ValueError if not. The console asks for the ID, and the service finds the appointment and calls cancel |
| Service prints/reads the menu |The service is mixing workflow coordination with presentation. A test of booking would have to fake keyboard input or capture output. |The service takes plain arguments and returns objects or raises ValueError or LookupError. Only the console prompts and prints. |
| Query sorts its source in place |appointments.sort(...) changes the caller’s list, which is a hidden side effect. It breaks the rule that source order stays unchanged QRY-03, FP-01, FP-02, and the next caller sees a surprise. |The query builds a new list and returns it, for example with sorted(...), so the source is left alone. |
| Store prints Appointment saved |The store’s job is only to hold the session’s collections. Printing is presentation, so it creates hidden output that clutters tests and ties storage to one kind of screen. |The store stores and returns. If a message is wanted, the console prints it after the service call succeeds. |

### A4 Sorting comparison

For `appointments.sort(key=appointment_sort_key)` and `result = sorted(appointments, key=appointment_sort_key)`, predict source order, return value and result identity. Give a meaningful mutation check: <!-- appointments.sort(key=appointment_sort_key) sorts the original list in place and returns None. The source order changes, and anyone using that list sees the change. result = sorted(appointments, key=appointment_sort_key) creates and returns a new sorted list. The original list stays unchanged, and result is not appointments is True. Both lists still contain the same Appointment objects. Mutation check: Start with an unsorted appointments list and save a copy of its original order. After running the query, check that the source list still matches the copy and that the result is a different list. This catches accidental changes to the original list. -->

Score-example prediction and explanation of passing the named key: <!-- For scores = [('Bea', 8), ('Ali', 8), ('Chen', 5)], using sorted(scores, key=score_key) with (score, name) as the key gives: [('Chen', 5), ('Ali', 8), ('Bea', 8)] Chen comes first because 5 is the lowest score. Ali comes before Bea because their scores are equal, so the name breaks the tie. Using key=score_key passes the function to sorted(), which calls it for each item. Using key=score_key() calls the function immediately instead, which is incorrect. -->

### A5 Exit question

Explain cancellation versus deletion, and checks for same-session lookup, all-status listing and SCHEDULED-only exclusion: <!-- Cancellation changes the appointment’s status to CANCELLED and keeps the same object in the store, instead of deleting it, because FR-07 and BR-06/07 require cancelled history to stay available for the session, and because deleting it would lose the record of what was booked. To show this, I’d cancel an appointment and look it up by ID to check I get the same object (is) with CANCELLED status, then list the practitioner’s appointments with no status filter to check the cancelled one still appears in the right order, and check the store’s collection still holds it. A SCHEDULED-only list should omit it because its status no longer matches that filter (QRY-02), so I’d list with SCHEDULED and confirm it’s absent, then with CANCELLED and confirm it’s present. The store keeps everything, and the query decides what to show. -->

## B. Human design and contracts

Complete before GitHub Copilot. Record any interface/integrity decision and its reasoning: <!-- response -->

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

Cover QRY-01–04, FP-01–03, UI-01–02 and relevant FR-01–09. Explain empty versus unknown versus invalid, enum conversion, actual object identity, error handling and unchanged state on rejection: <!-- The queries and menu cover FR-01 to FR-09, QRY-01 to QRY-04, FP-01 to FP-03 and UI-01 to UI-02. The service handles registration, lookup, booking, conflicts and cancellation, while Stage 9 adds appointment listing and the menu. There are three different outcomes: empty means the practitioner exists but has no matching appointments, so an empty list is returned. Unknown means the practitioner ID does not exist, so a LookupError is raised. Invalid means the input is incorrect, such as a blank ID or invalid status, so a ValueError is raised. Status text is converted into an AppointmentStatus enum at the menu level. The service only accepts an enum or None, preventing invalid text from silently passing through. The queries return the actual stored Appointment objects, not copies. Tests use is to confirm object identity. They also use sorted() and appointment_sort_key to return a new sorted list without changing the original. Finally, the menu catches expected errors and displays a message instead of crashing. Tests also check that rejected operations leave the stored data unchanged and do not reserve appointment IDs. -->

## C. Implementation and query verification

| Requirement / test ID | Code location | Case and meaningful assertion | Actual result | Evidence link |
|---|---|---|---|---|
|QRY-01 practitioner isolation |queries.py select_appointments |D1 and D2 appointments in one list; the D1 result equals [mine] and excludes the D2 control (test_select_returns_only_the_requested_practitioner, test_listing_excludes_other_practitioners) |your run |permalink |
|QRY-02 default all and each enum |select_appointments |None or omitted status returns all three statuses; each enum returns exactly its own appointment; an unmatched status returns a new [] (test_select_default_status_includes_every_status, test_select_explicit_status_keeps_only_that_status, test_select_status_with_no_matches_returns_new_empty_list) |your run |permalink |
|QRY-03 order and tie-break |appointment_sort_key, select_appointments |Unsorted input comes back earliest first. Equal-time cancelled/completed fixtures come back A1, A2, A3 by ID. Time is compared before ID (test_select_orders_by_date_time_ascending, test_select_breaks_equal_times_by_appointment_id, test_select_time_beats_id_in_ordering) |your run |permalink |
|FP-03 named-key reuse |appointment_sort_key |The key equals (date_time, appointment_id). A spy key that orders by ID changes the result order, so the query really uses it (test_sort_key_is_date_time_then_appointment_id, test_select_uses_the_named_key_for_ordering) |your run |permalink |
|FP-01 repeated calls and no I/O |select_appointments |Two calls on unchanged input give equal results, and capsys shows nothing was printed (test_select_is_repeatable_for_unchanged_inputs, test_select_does_no_input_output) |your run |permalink |
|FP-02 fresh lists |select_appointments |Empty, already-sorted and unsorted inputs each return a list that is not the source and holds the same objects (test_select_returns_distinct_list_for_empty_input, test_select_returns_a_new_list_with_the_same_objects, test_select_unsorted_result_is_not_the_source_list) |your run |permalink |
|Source unchanged |select_appointments, appointment_sort_key |Order, identity and fields are snapshotted before the call and compared after (test_select_does_not_change_source_order_or_objects, test_sort_key_does_not_change_the_appointment) |your run |permalink |
|QRY-04 known-empty |services.py list_practitioner_appointments |Known practitioner with no appointments, or no matching status, returns a new [] and no error (test_listing_known_practitioner_without_appointments_is_empty, test_listing_no_matching_status_is_empty_not_an_error) |your run |permalink |
|QRY-04 unknown and invalid |list_practitioner_appointments |Unknown ID raises LookupError; blank or non-text ID raises ValueError; a non-enum status such as 'scheduled' raises ValueError (test_listing_unknown_practitioner_raises_lookup_error, test_listing_blank_or_invalid_id_raises_value_error, test_listing_non_enum_status_raises_value_error) |your run |permalink |
|Retained history and identity |list_practitioner_appointments, store |After cancellation the default and CANCELLED lists include the same object, and the SCHEDULED list omits it. Padded IDs still match (test_listing_keeps_cancelled_history_for_default_and_cancelled, test_listing_returns_stored_objects_in_order, test_listing_trimmed_practitioner_id_still_finds_appointments) |your run |permalink |


|Rejection leaves state unchanged |list_practitioner_appointments |Records snapshotted before and after a failed request are equal (test_failed_listing_leaves_records_unchanged) |your run |permalink |

Include practitioner isolation, every enum status/default all, equal-time ID tie-break, named-key reuse, repeated calls, empty/already-sorted fresh lists, unchanged source order/fields, known-empty/unknown/invalid service cases and retained history.

Purity explanation from code inspection, including absence of hidden state and I/O: <!-- select_appointments is pure because everything it uses comes in through its arguments and everything it produces goes out through its return value. It has no module-level variable, no store reference and no input() or print(). It loops over the list it’s given and only reads each appointment’s practitioner ID and status. It collects matches into a new local list and returns sorted(...) of that list, so the caller’s list and the objects in it are never modified. appointment_sort_key just reads two fields and returns them, with no side effects. -->
What the tests do and do not establish: <!-- The tests show that for the inputs I chose, the query selects the right practitioner and status, orders correctly, returns a new list holding the same objects, leaves the source order and fields unchanged, prints nothing, and gives the same answer on repeat calls. The service tests show that unknown, invalid and empty cases are kept apart and that failed requests leave the records unchanged. They don’t prove purity in general, because I can only check the cases I thought of, and a hidden global or side effect in a case I didn’t test could go unnoticed, which is why the code inspection is also needed. They also don’t prove the requirements themselves are the right ones (validation versus verification), and they say nothing about the interactive console. That is what D covers. -->

## D. Integrated console and workflow evidence

| Scenario / acceptance ID | Reproducible inputs / artefact | Expected result | Observed result and state check | Evidence link |
|---|---|---|---|---|
| UI-01 full menu workflow | | | | |
| UI-02 invalid-input recovery | | | | |
| Automated service workflow | | | | |

Include registration/find, booking, conflict rejection, different-practitioner booking, cancellation, retrieval, listing/filtering, freed slot and exit; duplicate/unknown/blank IDs, malformed/impossible date, invalid status, unknown choice and repeated cancellation. Identify before/after state and subsequent successful action.

## E. GitHub Copilot review and human decisions

Human design completed before AI: <!-- reference -->
Actual prompt/context supplied: <!-- paste or accessible reference -->
Actual response: <!-- accessible reference -->

| AI finding | Code/test evidence | Severity | Accept/Modify/Reject and reason | Change or no change | Actual verification |
|---|---|---|---|---|---|
| | | | | | |

Responsibility check: explain how domain invariants, shared-store collections, service coordination, pure queries and console effects remain separate: <!-- response -->

## F. Required reflections

1. Which integration concern was architectural rather than a filtering/sorting detail? <!-- response -->
2. Which Copilot suggestion did you reject as over-engineering, and why? <!-- response -->
3. How did you prove cancelled appointments remain retrievable and listable in the same session? <!-- response -->

## G. Ten formative answers

1. What makes select_appointments pure, and what side effect breaks purity? <!-- response -->
2. Which explicit inputs are needed, and why avoid a global store? <!-- response -->
3. How can a new list reuse Appointment objects safely? <!-- response -->
4. Why use a named key, and what breaks equal-time ties? <!-- response -->
5. How do default and explicit status filters differ? <!-- response -->
6. How do empty, unknown practitioner and invalid filter cases differ? <!-- response -->
7. Which console errors recover, and how is unchanged state checked? <!-- response -->
8. What is data integrity for registered participants, conflicts and history? <!-- response -->
9. What is Copilot's review role, and who verifies findings? <!-- response -->
10. How do pure functions and OOP responsibilities work together? <!-- response -->
## H. Review, completion and common handover

Issues and bounded branches: <!-- links -->
PR/diff and another-member human reviewer: <!-- actual links/name -->
Review responses and Copilot comparison: <!-- links -->
Integrated common Stage 9 SHA: <!-- complete -->
Full regression command, working directory, actual count/result and evidence: <!-- complete -->
README run instructions and scope/limitations: <!-- link -->
Unresolved issues and support/action: <!-- complete -->
UG common candidate / PG future branch plan: <!-- complete -->

- [ ] Query contracts, purity, new lists and named-key ordering verified.
- [ ] Service empty/unknown/invalid cases and cancellation history verified.
- [ ] Every console command and invalid-input recovery demonstrated.
- [ ] Query and workflow tests plus all previous tests pass; actual evidence linked.
- [ ] Human design, Copilot critique, review and integration recorded honestly.
- [ ] Reflections and ten formative responses completed.
- [ ] README updated; earlier code/tests/records preserved.
- [ ] Common SHA protected for UG Stage 12; PG Stage 10/11 work deferred until approved.

No persistence, rescheduling or assurance implementation is part of Stage 9. UG: 6→7→8→9→12. PG: 6→7→8→9→10→11→12. Mixed groups keep one repository and protect the common candidate.
