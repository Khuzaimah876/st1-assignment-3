"""Stage 8 regression tests: one focused test per repaired defect."""

from datetime import datetime

import pytest

from smartcare.data_store import SmartCareDataStore
from smartcare.domain import AppointmentStatus
from smartcare.services import (
    AppointmentService,
    PatientService,
    PractitionerService,
)

WHEN = datetime(2026, 10, 1, 9, 0)


def make_store():
    """Fresh synthetic store with P1, DR1 and DR2 registered."""
    store = SmartCareDataStore()
    PatientService(store).register_patient('P1', 'Ari Example')
    practitioners = PractitionerService(store)
    practitioners.register_practitioner('DR1', 'Dee Example', 'General')
    practitioners.register_practitioner('DR2', 'Rae Example', 'General')
    return store, AppointmentService(store)


def test_f8_01_conflict_applies_only_to_same_practitioner():
    """F8-01 (FR-05, AC-04.1, AC-04.2): same practitioner + same time is
    rejected and not stored; a different practitioner at that time is allowed.
    """
    store, service = make_store()
    first = service.book_appointment('A1', 'P1', 'DR1', WHEN)

    assert store.has_practitioner_conflict('DR1', WHEN) is True
    assert store.has_practitioner_conflict('DR2', WHEN) is False

    with pytest.raises(ValueError):
        service.book_appointment('A2', 'P1', 'DR1', WHEN)
    assert store.list_appointments() == [first]

    other = service.book_appointment('A3', 'P1', 'DR2', WHEN)
    assert store.list_appointments() == [first, other]


def test_f8_02_cancelled_appointment_is_retained_and_retrievable():
    """F8-02 (FR-07, AC-05.2, FR-08): a cancelled appointment stays stored
    and lookup by ID returns the same object with status CANCELLED.
    """
    store, service = make_store()
    booked = service.book_appointment('A1', 'P1', 'DR1', WHEN)
    service.cancel_appointment('A1')

    assert store.list_appointments() == [booked]
    assert store.find_appointment('A1') is booked
    assert service.find_appointment('A1') is booked
    assert booked.status is AppointmentStatus.CANCELLED
    with pytest.raises(ValueError):
        service.cancel_appointment('A1')
    assert booked.status is AppointmentStatus.CANCELLED
