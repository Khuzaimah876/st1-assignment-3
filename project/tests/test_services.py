"""Stage 6 tests for SmartCare services (FR-02, FR-03 support, FR-06, FR-07)."""

from datetime import datetime

import pytest

from smartcare.data_store import SmartCareDataStore
from smartcare.domain import AppointmentStatus
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
