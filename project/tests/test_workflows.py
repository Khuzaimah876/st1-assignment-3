"""Stage 9 workflow tests: an integrated service sequence and the real
console menu (UI-01, UI-02).

Service tests share one fresh store per test. Console tests drive
run_menu with reproducible scripted input (monkeypatched input()) and,
separately, run `python main.py --interactive` in a subprocess.
Data is fixed and synthetic.
"""

import subprocess
import sys
from datetime import datetime
from pathlib import Path

import pytest

from smartcare.console import run_menu
from smartcare.data_store import SmartCareDataStore
from smartcare.domain import AppointmentStatus
from smartcare.services import (
    AppointmentService,
    PatientService,
    PractitionerService,
)

NINE = datetime(2026, 10, 1, 9, 0)
PROJECT_DIR = Path(__file__).resolve().parents[1]


def stored_state(store):
    """Comparable snapshot of every stored record."""
    return (
        [(p.patient_id, p.name) for p in store.list_patients()],
        [(p.practitioner_id, p.name, p.specialty)
         for p in store.list_practitioners()],
        [(a.appointment_id, a.patient.patient_id,
          a.practitioner.practitioner_id, a.date_time, a.status)
         for a in store.list_appointments()],
    )


# --- Integrated service sequence -------------------------------------------

def test_service_workflow_register_book_cancel_list_rebook() -> None:
    """UI-01 at service level: conflicts rejected, history kept, slot freed."""
    store = SmartCareDataStore()
    patients = PatientService(store)
    practitioners = PractitionerService(store)
    appointments = AppointmentService(store)

    patient = patients.register_patient('P1', 'Alex Example')
    d1 = practitioners.register_practitioner('D1', 'Taylor Example', 'General')
    d2 = practitioners.register_practitioner('D2', 'Morgan Example', 'General')
    assert patients.find_patient('P1') is patient
    assert practitioners.find_practitioner('D1') is d1
    assert practitioners.find_practitioner('D2') is d2

    first = appointments.book_appointment('A1', 'P1', 'D1', NINE)

    # Same practitioner at the same time is rejected without any change.
    before = stored_state(store)
    with pytest.raises(ValueError):
        appointments.book_appointment('A2', 'P1', 'D1', NINE)
    assert stored_state(store) == before

    # The same patient with another practitioner at that time is allowed.
    other = appointments.book_appointment('A2', 'P1', 'D2', NINE)
    assert other.practitioner is d2

    cancelled = appointments.cancel_appointment('A1')
    assert cancelled is first
    assert appointments.find_appointment('A1').status is (
        AppointmentStatus.CANCELLED
    )
    assert appointments.list_practitioner_appointments('D1') == [first]
    assert appointments.list_practitioner_appointments(
        'D1', AppointmentStatus.SCHEDULED,
    ) == []

    freed = appointments.book_appointment('A3', 'P1', 'D1', NINE)
    assert appointments.list_practitioner_appointments('D1') == [first, freed]
    assert appointments.list_practitioner_appointments(
        'D1', AppointmentStatus.SCHEDULED,
    ) == [freed]


def test_service_rejections_preserve_state_and_reserve_nothing() -> None:
    """Duplicate, unknown, conflict and invalid-time rejections change
    nothing and an invalid booking does not reserve its ID.
    """
    store = SmartCareDataStore()
    PatientService(store).register_patient('P1', 'Alex Example')
    PractitionerService(store).register_practitioner(
        'D1', 'Taylor Example', 'General',
    )
    appointments = AppointmentService(store)
    appointments.book_appointment('A1', 'P1', 'D1', NINE)
    before = stored_state(store)

    with pytest.raises(ValueError):          # duplicate appointment ID
        appointments.book_appointment('A1', 'P1', 'D1',
                                      datetime(2026, 10, 2, 9, 0))
    with pytest.raises(LookupError):         # unknown patient
        appointments.book_appointment('A2', 'P9', 'D1',
                                      datetime(2026, 10, 2, 9, 0))
    with pytest.raises(LookupError):         # unknown practitioner
        appointments.book_appointment('A2', 'P1', 'D9',
                                      datetime(2026, 10, 2, 9, 0))
    with pytest.raises(ValueError):          # conflict
        appointments.book_appointment('A2', 'P1', 'D1', NINE)
    with pytest.raises(ValueError):          # seconds are not allowed
        appointments.book_appointment('A2', 'P1', 'D1',
                                      datetime(2026, 10, 2, 9, 0, 30))
    assert stored_state(store) == before

    booked = appointments.book_appointment('A2', 'P1', 'D1',
                                           datetime(2026, 10, 2, 9, 0))
    assert booked.appointment_id == 'A2'


# --- Console harness -------------------------------------------------------

def run_console(monkeypatch, capsys, lines, store=None, ends_with_exit=True):
    """Run run_menu with scripted input; return (output, store).

    When the script runs out, input() raises EOFError like a closed
    stdin. Unless a test expects that, the session must have ended with
    the exit command, so a script that stops early cannot pass silently.
    """
    store = SmartCareDataStore() if store is None else store
    script = iter(lines)

    def scripted_input(prompt=''):
        try:
            return next(script)
        except StopIteration:
            raise EOFError from None

    monkeypatch.setattr('builtins.input', scripted_input)
    run_menu(store)
    out = capsys.readouterr().out
    if ends_with_exit:
        assert 'Goodbye' in out
    return out, store


def test_console_ui01_demonstration_sequence(monkeypatch, capsys) -> None:
    """Every menu command works end to end in one session."""
    lines = [
        '1', 'P1', 'Alex Example',
        '3', 'D1', 'Taylor Example', 'General',
        '3', 'D2', 'Morgan Example', 'General',
        '2', 'P1', '4', 'D1', '4', 'D2',
        '5', 'A1', 'P1', 'D1', '2026-10-01 09:00',
        '5', 'A2', 'P1', 'D1', '2026-10-01 09:00',     # conflict
        '5', 'A2', 'P1', 'D2', '2026-10-01 09:00',     # other practitioner
        '6', 'A1',
        '7', 'A1',
        '8', 'D1', '',
        '8', 'D1', 'scheduled',
        '5', 'A3', 'P1', 'D1', '2026-10-01 09:00',     # freed slot
        '8', 'D1', '',
        '0',
    ]
    out, store = run_console(monkeypatch, capsys, lines)

    assert 'Registered patient P1: Alex Example' in out
    assert 'Registered practitioner D1: Taylor Example (General)' in out
    assert 'Patient P1: Alex Example' in out
    assert 'Practitioner D2: Morgan Example (General)' in out
    assert 'Booked: A1: P1 with D1, 2026-10-01 09:00, scheduled' in out
    assert 'Error: Practitioner already has a SCHEDULED appointment' in out
    assert 'Booked: A2: P1 with D2, 2026-10-01 09:00, scheduled' in out
    assert 'Cancelled: A1: P1 with D1, 2026-10-01 09:00, cancelled' in out
    assert 'No matching appointments.' in out     # D1 SCHEDULED-only list
    assert 'Booked: A3: P1 with D1, 2026-10-01 09:00, scheduled' in out
    assert 'Goodbye' in out

    statuses = {a.appointment_id: a.status for a in store.list_appointments()}
    assert statuses == {
        'A1': AppointmentStatus.CANCELLED,
        'A2': AppointmentStatus.SCHEDULED,
        'A3': AppointmentStatus.SCHEDULED,
    }


def test_console_all_status_list_shows_cancelled_then_new(
    monkeypatch, capsys,
) -> None:
    """The all-status listing keeps the cancelled history and is ordered."""
    lines = [
        '1', 'P1', 'Alex Example',
        '3', 'D1', 'Taylor Example', 'General',
        '5', 'A2', 'P1', 'D1', '2026-10-01 09:00',
        '5', 'A1', 'P1', 'D1', '2026-10-01 10:00',
        '6', 'A2',
        '8', 'D1', '',
        '0',
    ]
    out, _ = run_console(monkeypatch, capsys, lines)
    listing = out.split('Cancelled:')[1]
    first = listing.index('A2: P1 with D1, 2026-10-01 09:00, cancelled')
    second = listing.index('A1: P1 with D1, 2026-10-01 10:00, scheduled')
    assert first < second


def test_console_recovers_from_invalid_input_without_changing_state(
    monkeypatch, capsys,
) -> None:
    """UI-02: each rejection is reported, state is intact, session goes on."""
    store = SmartCareDataStore()
    lines = [
        'x',                                            # unknown choice
        '',                                             # empty choice
        '2', '   ',                                     # blank patient ID
        '2', 'P9',                                      # unknown patient
        '1', 'P1', 'Alex Example',                      # register
        '1', 'P1', 'Replacement',                       # duplicate
        '3', 'D1', 'Taylor Example', 'General',
        '5', 'A1', 'P1', 'D9', '2026-10-01 09:00',      # unknown practitioner
        '5', 'A1', 'P1', 'D1', '2026-10-01T09:00',      # malformed time
        '5', 'A1', 'P1', 'D1', '2026-02-30 09:00',      # impossible date
        '7', 'A1',                                      # A1 not reserved/exists
        '5', 'A1', 'P1', 'D1', '2026-10-01 09:00',      # valid booking
        '7', 'A9',                                      # unknown appointment
        '6', 'A1',
        '6', 'A1',                                      # repeated cancel
        '8', 'D1', 'done',                              # invalid status
        '8', 'D9', '',                                  # unknown practitioner
        '8', 'D1', 'cancelled',                         # still works after
        '0',
    ]
    out, store = run_console(monkeypatch, capsys, lines, store)

    assert out.count("Unknown choice") == 2
    assert 'Error: Patient ID cannot be blank' in out
    assert 'Error: Patient not found' in out
    assert 'Error: Practitioner not found' in out
    assert 'Use date/time format YYYY-MM-DD HH:MM' in out
    assert 'Invalid calendar date/time' in out
    assert 'Error: Appointment not found' in out
    assert 'Status must be scheduled, cancelled or completed' in out
    assert 'Traceback' not in out

    # Only the intended records exist, with original data.
    assert [(p.patient_id, p.name) for p in store.list_patients()] == [
        ('P1', 'Alex Example'),
    ]
    appointments = store.list_appointments()
    assert [a.appointment_id for a in appointments] == ['A1']
    assert appointments[0].status is AppointmentStatus.CANCELLED


def test_console_failed_booking_does_not_reserve_the_id(
    monkeypatch, capsys,
) -> None:
    """A rejected booking leaves the ID free for a later valid booking."""
    lines = [
        '1', 'P1', 'Alex Example',
        '3', 'D1', 'Taylor Example', 'General',
        '5', 'A1', 'P1', 'D1', 'not a date',
        '5', 'A1', 'P1', 'D1', '2026-10-01 09:00',
        '0',
    ]
    out, store = run_console(monkeypatch, capsys, lines)
    assert 'Booked: A1' in out
    assert len(store.list_appointments()) == 1


def test_console_status_text_is_converted_at_the_boundary(
    monkeypatch, capsys,
) -> None:
    """scheduled/cancelled/completed text filters; blank means all."""
    lines = [
        '1', 'P1', 'Alex Example',
        '3', 'D1', 'Taylor Example', 'General',
        '5', 'A1', 'P1', 'D1', '2026-10-01 09:00',
        '8', 'D1', 'scheduled',
        '8', 'D1', 'completed',
        '8', 'D1', '  SCHEDULED ',
        '0',
    ]
    out, _ = run_console(monkeypatch, capsys, lines)
    assert out.count('A1: P1 with D1, 2026-10-01 09:00, scheduled') >= 3
    assert out.count('No matching appointments.') == 1


def test_console_exits_cleanly_when_input_ends(monkeypatch, capsys) -> None:
    """End of input (no '0') exits the loop instead of crashing."""
    out, _ = run_console(
        monkeypatch, capsys, ['1', 'P1', 'Alex Example'], ends_with_exit=False,
    )
    assert 'Registered patient P1' in out
    assert 'Input ended' in out


def test_console_uses_the_session_store_it_is_given(
    monkeypatch, capsys,
) -> None:
    """The same store lasts the whole session: later commands see it."""
    store = SmartCareDataStore()
    lines = ['1', 'P1', 'Alex Example', '2', 'P1', '0']
    out, _ = run_console(monkeypatch, capsys, lines, store)
    assert out.count('Patient P1: Alex Example') == 1   # found, not just made
    assert store.find_patient('P1') is not None


# --- Real program through a subprocess -------------------------------------

def run_program(arguments, text=''):
    """Run main.py from project/ and return the finished process."""
    return subprocess.run(
        [sys.executable, 'main.py', *arguments],
        cwd=PROJECT_DIR,
        input=text,
        capture_output=True,
        text=True,
        timeout=30,
    )


def test_subprocess_interactive_session_end_to_end() -> None:
    """The real entry point runs a reproducible scripted session."""
    script = '\n'.join([
        '1', 'P1', 'Alex Example',
        '3', 'D1', 'Taylor Example', 'General',
        '5', 'A1', 'P1', 'D1', '2026-10-01 09:00',
        '6', 'A1',
        '7', 'A1',
        '8', 'D1', '',
        '0', '',
    ])
    result = run_program(['--interactive'], script)
    assert result.returncode == 0
    assert result.stderr == ''
    assert 'Cancelled: A1: P1 with D1, 2026-10-01 09:00, cancelled' in (
        result.stdout
    )
    assert 'Goodbye' in result.stdout


def test_subprocess_new_session_starts_empty() -> None:
    """Data is session-only: a second run does not know the first's records."""
    first = run_program(['--interactive'], '1\nP1\nAlex Example\n0\n')
    assert 'Registered patient P1' in first.stdout
    second = run_program(['--interactive'], '2\nP1\n0\n')
    assert 'Error: Patient not found' in second.stdout


def test_subprocess_demo_still_runs() -> None:
    """The supplied demonstration entry point is unchanged."""
    result = run_program([])
    assert result.returncode == 0
    assert 'A1: P1 with DR1, 2026-10-01 09:00, scheduled' in result.stdout
    assert 'Session-only data' in result.stdout
