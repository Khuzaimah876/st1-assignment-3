"""Stage 6 tests for SmartCare services (FR-02, FR-03 support, FR-06, FR-07)."""

from datetime import datetime

import pytest

from smartcare.data_store import SmartCareDataStore
from smartcare.domain import Appointment, AppointmentStatus
from smartcare.services import (
    AppointmentService,
    PatientService,
    PractitionerService,
)


def make_patient_service():
    """Create a patient service with one synthetic registered patient."""
    store = SmartCareDataStore()
    service = PatientService(store)
    patient = service.register_patient('P1', 'Alice Example')
    return service, patient


def make_practitioner_service():
    """Create a practitioner service with one synthetic practitioner."""
    store = SmartCareDataStore()
    service = PractitionerService(store)
    practitioner = service.register_practitioner(
        'DR1', 'Dr Sam Example', 'General Practice',
    )
    return service, practitioner


def make_appointment_service():
    """Create a service with one synthetic SCHEDULED appointment A1."""
    store = SmartCareDataStore()
    PatientService(store).register_patient('P1', 'Alice Example')
    PractitionerService(store).register_practitioner(
        'DR1', 'Dr Sam Example', 'General Practice',
    )
    service = AppointmentService(store)
    appointment = service.book_appointment(
        'A1', 'P1', 'DR1', datetime(2026, 10, 1, 9, 0),
    )
    return service, appointment


# ---------- FR-02 patient lookup ----------

def test_find_patient_returns_same_stored_object():
    service, patient = make_patient_service()
    assert service.find_patient('P1') is patient


def test_find_patient_unknown_id_raises_lookup_error():
    service, _ = make_patient_service()
    with pytest.raises(LookupError):
        service.find_patient('P999')


def test_find_patient_blank_id_raises_value_error():
    service, _ = make_patient_service()
    with pytest.raises(ValueError):
        service.find_patient('   ')


def test_find_patient_trims_id():
    service, patient = make_patient_service()
    assert service.find_patient('  P1  ') is patient


def test_find_patient_is_case_sensitive():
    service, _ = make_patient_service()
    with pytest.raises(LookupError):
        service.find_patient('p1')


def test_find_patient_non_string_id_raises_value_error():
    service, _ = make_patient_service()
    with pytest.raises(ValueError):
        service.find_patient(None)


# ---------- FR-03 supporting practitioner lookup ----------

def test_find_practitioner_returns_same_stored_object():
    service, practitioner = make_practitioner_service()
    assert service.find_practitioner('DR1') is practitioner


def test_find_practitioner_unknown_id_raises_lookup_error():
    service, _ = make_practitioner_service()
    with pytest.raises(LookupError):
        service.find_practitioner('DR999')


def test_find_practitioner_blank_id_raises_value_error():
    service, _ = make_practitioner_service()
    with pytest.raises(ValueError):
        service.find_practitioner('')


def test_find_practitioner_trims_id():
    service, practitioner = make_practitioner_service()
    assert service.find_practitioner(' DR1 ') is practitioner


def test_find_practitioner_is_case_sensitive():
    service, _ = make_practitioner_service()
    with pytest.raises(LookupError):
        service.find_practitioner('dr1')


def test_find_practitioner_non_string_id_raises_value_error():
    service, _ = make_practitioner_service()
    with pytest.raises(ValueError):
        service.find_practitioner(None)


# ---------- FR-06 / FR-07 cancellation ----------

def test_cancel_returns_same_object_with_cancelled_status():
    service, appointment = make_appointment_service()
    result = service.cancel_appointment('A1')
    assert result is appointment
    assert result.status is AppointmentStatus.CANCELLED


def test_cancelled_appointment_is_still_retrievable():
    service, appointment = make_appointment_service()
    service.cancel_appointment('A1')
    found = service.find_appointment('A1')
    assert found is appointment
    assert found.status is AppointmentStatus.CANCELLED


def test_repeated_cancel_raises_value_error_and_keeps_state():
    service, appointment = make_appointment_service()
    service.cancel_appointment('A1')
    with pytest.raises(ValueError):
        service.cancel_appointment('A1')
    assert appointment.status is AppointmentStatus.CANCELLED


def test_cancel_unknown_id_raises_lookup_error():
    service, appointment = make_appointment_service()
    with pytest.raises(LookupError):
        service.cancel_appointment('A999')
    assert appointment.status is AppointmentStatus.SCHEDULED


def test_cancel_blank_id_raises_value_error():
    service, appointment = make_appointment_service()
    with pytest.raises(ValueError):
        service.cancel_appointment('   ')
    assert appointment.status is AppointmentStatus.SCHEDULED


def test_cancelled_slot_can_be_booked_again():
    service, _ = make_appointment_service()
    service.cancel_appointment('A1')
    new = service.book_appointment(
        'A2', 'P1', 'DR1', datetime(2026, 10, 1, 9, 0),
    )
    assert new.status is AppointmentStatus.SCHEDULED



def test_cancel_completed_appointment_raises_value_error_and_keeps_state():
    store = SmartCareDataStore()
    patient = PatientService(store).register_patient('P1', 'Alice Example')
    practitioner = PractitionerService(store).register_practitioner(
        'DR1', 'Dr Sam Example', 'General Practice',
    )
    completed = Appointment(
        'A2', patient, practitioner, datetime(2026, 10, 1, 10, 0),
        AppointmentStatus.COMPLETED,
    )
    store.add_appointment(completed)
    service = AppointmentService(store)
    with pytest.raises(ValueError):
        service.cancel_appointment('A2')
    assert completed.status is AppointmentStatus.COMPLETED



def test_cancel_non_string_id_raises_value_error():
    service, appointment = make_appointment_service()
    with pytest.raises(ValueError):
        service.cancel_appointment(None)
    assert appointment.status is AppointmentStatus.SCHEDULED


# ======================================================================
# Stage 7 service tests. Each test uses one fresh SmartCareDataStore
# shared by all three services. TEST IDs (T-SVC-xx) link to record B.
# ======================================================================

WHEN = datetime(2026, 10, 1, 9, 0)


def make_services():
    """Return a fresh store, its three services and registered P1/DR1/DR2."""
    store = SmartCareDataStore()
    patients = PatientService(store)
    practitioners = PractitionerService(store)
    appointments = AppointmentService(store)
    patients.register_patient('P1', 'Alice Example')
    practitioners.register_practitioner('DR1', 'Dr Sam Example', 'General')
    practitioners.register_practitioner('DR2', 'Dr Jo Example', 'General')
    return store, patients, practitioners, appointments


# ---------- FR-01 register patient ----------

def test_register_patient_stores_the_returned_object():
    """T-SVC-01 (AC-01.1): valid data with an unused ID is stored."""
    store = SmartCareDataStore()
    service = PatientService(store)
    patient = service.register_patient('P1', 'Alice Example')
    assert service.find_patient('P1') is patient
    assert store.list_patients() == [patient]
    assert patient.name == 'Alice Example'


def test_register_trimmed_duplicate_patient_id_is_rejected():
    """T-SVC-02 (AC-01.2): ' P1 ' is the same ID as 'P1' and is rejected
    without replacing the original.
    """
    store, patients, _, _ = make_services()
    original = patients.find_patient('P1')
    with pytest.raises(ValueError):
        patients.register_patient(' P1 ', 'Replacement')
    assert store.list_patients() == [original]
    assert original.name == 'Alice Example'


def test_patient_ids_differing_only_by_case_are_distinct():
    """T-SVC-03 (FR-01, IDs case-sensitive): 'p1' is a different unused ID."""
    store, patients, _, _ = make_services()
    lower = patients.register_patient('p1', 'Lower Example')
    assert patients.find_patient('p1') is lower
    assert patients.find_patient('P1') is not lower
    assert len(store.list_patients()) == 2


def test_register_patient_blank_name_leaves_store_unchanged():
    """T-SVC-04 (FR-01 validation contract): invalid field rejected, nothing
    stored.
    """
    store = SmartCareDataStore()
    with pytest.raises(ValueError):
        PatientService(store).register_patient('P1', '   ')
    assert store.list_patients() == []
    assert store.find_patient('P1') is None


# ---------- FR-03 register practitioner ----------

def test_register_practitioner_stores_the_returned_object():
    """T-SVC-05 (FR-03): a valid practitioner is stored and found."""
    store = SmartCareDataStore()
    service = PractitionerService(store)
    practitioner = service.register_practitioner('DR1', 'Dr Sam', 'General')
    assert service.find_practitioner('DR1') is practitioner
    assert store.list_practitioners() == [practitioner]


def test_register_trimmed_duplicate_practitioner_id_is_rejected():
    """T-SVC-06 (FR-03): a trimmed duplicate ID does not overwrite."""
    store, _, practitioners, _ = make_services()
    original = practitioners.find_practitioner('DR1')
    with pytest.raises(ValueError):
        practitioners.register_practitioner('DR1 ', 'Replacement', 'Other')
    assert practitioners.find_practitioner('DR1') is original
    assert original.name == 'Dr Sam Example'
    assert len(store.list_practitioners()) == 2


# ---------- FR-04 book appointment / FR-08 find appointment ----------

def test_book_appointment_stores_scheduled_appointment():
    """T-SVC-07 (AC-03.1, AC-06.1): booking stores a SCHEDULED appointment
    linked to the registered objects; lookup returns that same object.
    """
    store, patients, practitioners, appointments = make_services()
    booked = appointments.book_appointment('A1', 'P1', 'DR1', WHEN)
    assert appointments.find_appointment('A1') is booked
    assert store.list_appointments() == [booked]
    assert booked.status is AppointmentStatus.SCHEDULED
    assert booked.patient is patients.find_patient('P1')
    assert booked.practitioner is practitioners.find_practitioner('DR1')
    assert booked.date_time == WHEN


@pytest.mark.parametrize(
    ('patient_id', 'practitioner_id'),
    [('P404', 'DR1'), ('P1', 'DR404')],
    ids=['unknown-patient', 'unknown-practitioner'],
)
def test_book_unknown_participant_is_rejected_and_nothing_stored(
    patient_id, practitioner_id,
):
    """T-SVC-08 (AC-03.2): an unknown participant raises LookupError."""
    store, _, _, appointments = make_services()
    with pytest.raises(LookupError):
        appointments.book_appointment('A1', patient_id, practitioner_id, WHEN)
    assert store.list_appointments() == []


def test_book_invalid_date_time_is_rejected_and_nothing_stored():
    """T-SVC-09 (FR-04 validation contract): seconds precision rejected."""
    store, _, _, appointments = make_services()
    with pytest.raises(ValueError):
        appointments.book_appointment(
            'A1', 'P1', 'DR1', datetime(2026, 10, 1, 9, 0, 30),
        )
    assert store.list_appointments() == []


def test_book_trimmed_duplicate_appointment_id_keeps_original():
    """T-SVC-10 (FR-04): ' A1 ' duplicates 'A1' and does not overwrite."""
    store, _, _, appointments = make_services()
    original = appointments.book_appointment('A1', 'P1', 'DR1', WHEN)
    with pytest.raises(ValueError):
        appointments.book_appointment(
            ' A1 ', 'P1', 'DR2', datetime(2026, 10, 2, 9, 0),
        )
    assert store.list_appointments() == [original]
    assert original.practitioner.practitioner_id == 'DR1'


def test_find_unknown_appointment_raises_lookup_error():
    """T-SVC-11 (FR-08 / AC-06.1 negative): absent valid ID reports absence."""
    _, _, _, appointments = make_services()
    appointments.book_appointment('A1', 'P1', 'DR1', WHEN)
    with pytest.raises(LookupError):
        appointments.find_appointment('A2')


# ---------- FR-05 practitioner conflict ----------

def test_same_practitioner_same_time_conflict_leaves_store_unchanged():
    """T-SVC-12 (AC-04.1): exact-time SCHEDULED conflict raises ValueError
    and the rejected booking is not stored.
    """
    store, patients, _, appointments = make_services()
    patients.register_patient('P2', 'Bo Example')
    first = appointments.book_appointment('A1', 'P1', 'DR1', WHEN)
    with pytest.raises(ValueError):
        appointments.book_appointment('A2', 'P2', 'DR1', WHEN)
    assert store.list_appointments() == [first]
    assert store.find_appointment('A2') is None
    assert first.status is AppointmentStatus.SCHEDULED
    assert first.patient.patient_id == 'P1'


def test_different_practitioner_same_time_is_allowed():
    """T-SVC-13 (AC-04.2): another practitioner at the same time is stored."""
    store, _, _, appointments = make_services()
    first = appointments.book_appointment('A1', 'P1', 'DR1', WHEN)
    second = appointments.book_appointment('A2', 'P1', 'DR2', WHEN)
    assert store.list_appointments() == [first, second]
    assert second.status is AppointmentStatus.SCHEDULED


def test_same_practitioner_one_minute_later_is_allowed():
    """T-SVC-14 (AC-04.1 boundary): conflict needs the exact datetime."""
    store, _, _, appointments = make_services()
    first = appointments.book_appointment('A1', 'P1', 'DR1', WHEN)
    later = appointments.book_appointment(
        'A2', 'P1', 'DR1', datetime(2026, 10, 1, 9, 1),
    )
    assert appointments.find_appointment('A2') is later
    assert store.list_appointments() == [first, later]


# ---------- FR-06 / FR-07 cancellation and retained history ----------

def test_cancelled_appointment_remains_in_listing():
    """T-SVC-15 (AC-05.2): cancelled history stays in the session listing."""
    store, _, _, appointments = make_services()
    booked = appointments.book_appointment('A1', 'P1', 'DR1', WHEN)
    appointments.cancel_appointment('A1')
    assert store.list_appointments() == [booked]
    assert store.list_appointments()[0].status is AppointmentStatus.CANCELLED


def test_cancel_changes_only_the_targeted_appointment():
    """T-SVC-16 (AC-05.1): cancelling A1 leaves A2 SCHEDULED."""
    _, _, _, appointments = make_services()
    first = appointments.book_appointment('A1', 'P1', 'DR1', WHEN)
    second = appointments.book_appointment('A2', 'P1', 'DR2', WHEN)
    appointments.cancel_appointment('A1')
    assert first.status is AppointmentStatus.CANCELLED
    assert second.status is AppointmentStatus.SCHEDULED


def test_cancelled_and_rebooked_slot_keeps_both_records():
    """T-SVC-17 (FR-05 + FR-07): a cancelled booking frees the slot and is
    still retained alongside the new booking.
    """
    store, _, _, appointments = make_services()
    old = appointments.book_appointment('A1', 'P1', 'DR1', WHEN)
    appointments.cancel_appointment('A1')
    new = appointments.book_appointment('A2', 'P1', 'DR1', WHEN)
    assert store.list_appointments() == [old, new]
    assert old.status is AppointmentStatus.CANCELLED
    assert new.status is AppointmentStatus.SCHEDULED