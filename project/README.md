# SmartCare

A small in-memory appointment application for clinic staff, built for Software Technology 1 Assignment 3.
Requirements baseline: SmartCare A3 2026 revision 2. Runtime uses only the Python standard library; the
development dependency is pytest 8.3.5. Release: SmartCare v1.0 (course release, UG common scope). See the root README for the exact release SHA.

## Run and test

From this directory (`project/`), in the approved Python environment (tested with Python 3.13.1; you can use `python3` on macOS if `python` is not found):

```sh
python -m pip install -r requirements-dev.txt   # if needed
python main.py                # supplied demonstration
python main.py --interactive  # interactive menu
python -m pytest -q           # full cumulative test suite
```

## Interactive menu

| Choice | Action |
| --- | --- |
| 1 / 2 | Register a patient (ID, name) / find a patient by ID |
| 3 / 4 | Register a practitioner (ID, name, specialty) / find a practitioner by ID |
| 5 | Book an appointment (appointment ID, patient ID, practitioner ID, date/time) |
| 6 / 7 | Cancel an appointment by ID / find an appointment by ID |
| 8 | List a practitioner's appointments; blank status = all, or `scheduled`, `cancelled`, `completed` |
| 0 | Exit (session data is discarded) |

Date/time must be exactly `YYYY-MM-DD HH:MM` (local time, minute precision). Invalid menu choices, blank or
unknown IDs, duplicate registrations, unknown booking participants, malformed or impossible dates, unknown
appointments, repeated cancellation and invalid statuses are reported and the menu continues; a rejected
operation changes no stored record.

## Structure

- `smartcare/domain.py`: `Patient`, `Practitioner`, `Appointment`, `AppointmentStatus`; validation and guarded cancellation.
- `smartcare/data_store.py`: in-memory collections and lookups for one session.
- `smartcare/services.py`: register/find/book/cancel and validated practitioner listing.
- `smartcare/queries.py`: pure `appointment_sort_key` and `select_appointments` (explicit inputs, new sorted list, no side effects).
- `smartcare/console.py`: prompts, parsing, display and recovery; calls the services only.
- `main.py`: chooses the demo or the interactive menu.
- `tests/`: starter, domain, services, regression, query and workflow tests (including console and subprocess tests).

Cancelling an appointment changes its status to `CANCELLED`; the same object stays retrievable and listable in the session.

## Scope and limitations

- Data exists only in the running session and is lost on exit. Between-session persistence (FR-10) is retired and not implemented.
- No authentication, patient-conflict, duration-overlap, past-date or clinic-hours rules are implemented.
- Use synthetic data only; never enter real patient or personal information.
- Stages 10 and 11 (PG) are not part of this common application.


## AI use

GitHub Copilot was used to assist with drafting some code and documentation, as well as the required review, test design and debugging activities. 
.All suggestions were checked against the requirements, code and test results.
Some were adjusted or rejected where necessary, as explained in the relevant stage records. The team reviewed and tested the work and takes responsibility for everything submitted.
