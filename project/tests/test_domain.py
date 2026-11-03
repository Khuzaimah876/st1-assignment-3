"""Stage 7 domain tests for Patient, Practitioner and Appointment.

Each test builds its own fresh objects with fixed synthetic data, so the
tests do not depend on order, wall-clock time or external services.
TEST IDs (T-DOM-xx) link to the Stage 7 traceability matrix (record B).
"""

from datetime import datetime, timezone

import pytest

from smartcare.domain import (
    Appointment,
    AppointmentStatus,
    Patient,
    Practitioner,
)

WHEN = datetime(2026, 10, 1, 9, 0)


def make_participants() -> tuple[Patient, Practitioner]:
    """Return a fresh synthetic patient and practitioner."""
    patient = Patient('P1', 'Alex Example')
    practitioner = Practitioner('D1', 'Taylor Example', 'General Practice')
    return patient, practitioner


# ---------- Patient (FR-01 partial domain evidence) ----------

def test_patient_stores_trimmed_id_and_name() -> None:
    """T-DOM-01: valid patient fields are stored, trimmed."""
    patient = Patient('  P1  ', '  Alex Example  ')
    assert patient.patient_id == 'P1'
    assert patient.name == 'Alex Example'


@pytest.mark.parametrize('bad_id', ['', '   ', '\t', None, 101])
def test_blank_patient_id_is_rejected(bad_id) -> None:
    """T-DOM-02: blank, whitespace-only or non-string patient ID raises
    ValueError (reference intention 1).
    """
    with pytest.raises(ValueError):
        Patient(bad_id, 'Alex Example')


@pytest.mark.parametrize('bad_name', ['', '   ', None])
def test_blank_patient_name_is_rejected(bad_name) -> None:
    """T-DOM-03: a whitespace-only or missing patient name raises
    ValueError.
    """
    with pytest.raises(ValueError):
        Patient('P1', bad_name)


def test_patient_id_is_read_only() -> None:
    """T-DOM-04: patient identity cannot be reassigned after
    construction.
    """
    patient = Patient('P1', 'Alex Example')
    with pytest.raises(AttributeError):
        patient.patient_id = 'P2'
    assert patient.patient_id == 'P1'


# ---------- Practitioner (FR-03 partial domain evidence) ----------

def test_practitioner_stores_trimmed_fields() -> None:
    """T-DOM-05: valid practitioner ID, name and specialty are stored."""
    practitioner = Practitioner(' D1 ', ' Taylor Example ', ' Cardiology ')
    assert practitioner.practitioner_id == 'D1'
    assert practitioner.name == 'Taylor Example'
    assert practitioner.specialty == 'Cardiology'


@pytest.mark.parametrize(
    ('practitioner_id', 'name', 'specialty'),
    [
        ('   ', 'Taylor Example', 'General Practice'),
        ('D1', '   ', 'General Practice'),
        ('D1', 'Taylor Example', '   '),
        ('D1', 'Taylor Example', None),
    ],
)
def test_practitioner_blank_required_field_is_rejected(
    practitioner_id,
    name,
    specialty,
) -> None:
    """T-DOM-06: each required practitioner field rejects blank input."""
    with pytest.raises(ValueError):
        Practitioner(practitioner_id, name, specialty)


# ---------- Appointment construction ----------

def test_new_appointment_starts_scheduled() -> None:
    """T-DOM-07: a new appointment starts SCHEDULED and keeps the actual
    participant objects and time (reference intention 2).
    """
    patient, practitioner = make_participants()
    appointment = Appointment(' A1 ', patient, practitioner, WHEN)
    assert appointment.status is AppointmentStatus.SCHEDULED
    assert appointment.appointment_id == 'A1'
    assert appointment.patient is patient
    assert appointment.practitioner is practitioner
    assert appointment.date_time == WHEN


def test_appointment_blank_id_is_rejected() -> None:
    """T-DOM-08: a whitespace-only appointment ID raises ValueError."""
    patient, practitioner = make_participants()
    with pytest.raises(ValueError):
        Appointment('   ', patient, practitioner, WHEN)


def test_appointment_requires_patient_and_practitioner_objects() -> None:
    """T-DOM-09: IDs or swapped objects are not accepted as participants."""
    patient, practitioner = make_participants()
    with pytest.raises(ValueError):
        Appointment('A1', 'P1', practitioner, WHEN)
    with pytest.raises(ValueError):
        Appointment('A1', patient, 'D1', WHEN)
    with pytest.raises(ValueError):
        Appointment('A1', practitioner, patient, WHEN)


@pytest.mark.parametrize(
    'bad_time',
    [
        '2026-10-01 09:00',
        datetime(2026, 10, 1, 9, 0, 1),
        datetime(2026, 10, 1, 9, 0, 0, 1),
        datetime(2026, 10, 1, 9, 0, tzinfo=timezone.utc),
    ],
    ids=['string', 'seconds', 'microseconds', 'timezone-aware'],
)
def test_appointment_rejects_invalid_date_time(bad_time) -> None:
    """T-DOM-10: only a local naive datetime at minute precision is
    accepted.
    """
    patient, practitioner = make_participants()
    with pytest.raises(ValueError):
        Appointment('A1', patient, practitioner, bad_time)


def test_appointment_rejects_invalid_status() -> None:
    """T-DOM-11: status must be an AppointmentStatus member, not text."""
    patient, practitioner = make_participants()
    with pytest.raises(ValueError):
        Appointment('A1', patient, practitioner, WHEN, 'scheduled')


# ---------- Appointment cancellation (FR-06 domain guard) ----------

def test_cancel_changes_status() -> None:
    """T-DOM-12: cancelling SCHEDULED changes status to CANCELLED
    (reference intention 3).
    """
    patient, practitioner = make_participants()
    appointment = Appointment('A1', patient, practitioner, WHEN)
    appointment.cancel()
    assert appointment.status is AppointmentStatus.CANCELLED
    assert appointment.appointment_id == 'A1'
    assert appointment.date_time == WHEN


def test_repeated_cancellation_is_rejected() -> None:
    """T-DOM-13: a second cancel raises ValueError and the status stays
    CANCELLED (reference intention 4).
    """
    patient, practitioner = make_participants()
    appointment = Appointment('A1', patient, practitioner, WHEN)
    appointment.cancel()
    with pytest.raises(ValueError):
        appointment.cancel()
    assert appointment.status is AppointmentStatus.CANCELLED


def test_completed_appointment_cannot_be_cancelled() -> None:
    """T-DOM-14: cancelling COMPLETED raises ValueError and the status
    stays COMPLETED.
    """
    patient, practitioner = make_participants()
    appointment = Appointment(
        'A1',
        patient,
        practitioner,
        WHEN,
        AppointmentStatus.COMPLETED,
    )
    with pytest.raises(ValueError):
        appointment.cancel()
    assert appointment.status is AppointmentStatus.COMPLETED


def test_appointment_status_cannot_be_assigned_directly() -> None:
    """T-DOM-15: status changes only through cancel(), not assignment."""
    patient, practitioner = make_participants()
    appointment = Appointment('A1', patient, practitioner, WHEN)
    with pytest.raises(AttributeError):
        appointment.status = AppointmentStatus.CANCELLED
    assert appointment.status is AppointmentStatus.SCHEDULED