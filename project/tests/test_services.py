"""Stage 6 tests for SmartCare service lookups (FR-02, FR-03 support)."""

import pytest

from smartcare.data_store import SmartCareDataStore
from smartcare.services import PatientService, PractitionerService


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


def test_find_patient_non_string_id_raises_value_error():
    service, _ = make_patient_service()
    with pytest.raises(ValueError):
        service.find_patient(None)


def test_find_practitioner_non_string_id_raises_value_error():
    service, _ = make_practitioner_service()
    with pytest.raises(ValueError):
        service.find_practitioner(None)
