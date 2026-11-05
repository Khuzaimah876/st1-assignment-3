"""Stage 9 query tests: pure select_appointments, the named sort key and
validated service listing (QRY-01 to QRY-04, FP-01 to FP-03).

Pure-query tests build appointments directly and use no store. Service
tests use a fresh store per test. Data is fixed and synthetic.
"""

from datetime import datetime

import pytest

from smartcare import queries
from smartcare.data_store import SmartCareDataStore
from smartcare.domain import (
    Appointment,
    AppointmentStatus,
    Patient,
    Practitioner,
)
from smartcare.queries import appointment_sort_key, select_appointments
from smartcare.services import (
    AppointmentService,
    PatientService,
    PractitionerService,
)

NINE = datetime(2026, 10, 1, 9, 0)
TEN = datetime(2026, 10, 1, 10, 0)
ELEVEN = datetime(2026, 10, 1, 11, 0)

SCHEDULED = AppointmentStatus.SCHEDULED
CANCELLED = AppointmentStatus.CANCELLED
COMPLETED = AppointmentStatus.COMPLETED

PATIENT = Patient('P1', 'Alex Example')
DR1 = Practitioner('D1', 'Taylor Example', 'General')
DR2 = Practitioner('D2', 'Morgan Example', 'General')


def appt(appointment_id, practitioner, date_time, status=SCHEDULED):
    """Build a standalone appointment for the pure-query tests."""
    return Appointment(appointment_id, PATIENT, practitioner, date_time,
                       status)


def snapshot(appointments):
    """Order, identity and fields of every appointment in a list."""
    return [
        (id(a), a.appointment_id, a.patient, a.practitioner, a.date_time,
         a.status)
        for a in appointments
    ]


# --- FP-03: the named sort key ---------------------------------------------

def test_sort_key_is_date_time_then_appointment_id() -> None:
    """The key is exactly (date_time, appointment_id)."""
    assert appointment_sort_key(appt('A7', DR1, TEN)) == (TEN, 'A7')


def test_sort_key_orders_by_time_before_id() -> None:
    """An earlier time wins even when its ID sorts later."""
    early_late_id = appt('A9', DR1, NINE)
    late_early_id = appt('A1', DR1, TEN)
    assert appointment_sort_key(early_late_id) < appointment_sort_key(
        late_early_id,
    )


def test_sort_key_breaks_equal_time_by_id() -> None:
    """At the same time the smaller appointment ID comes first."""
    assert appointment_sort_key(appt('A1', DR1, NINE)) < appointment_sort_key(
        appt('A2', DR1, NINE),
    )


def test_sort_key_does_not_change_the_appointment() -> None:
    """Calling the key leaves the appointment's fields untouched."""
    a = appt('A1', DR1, NINE)
    before = snapshot([a])
    appointment_sort_key(a)
    appointment_sort_key(a)
    assert snapshot([a]) == before


def test_select_uses_the_named_key_for_ordering(monkeypatch) -> None:
    """Replacing the module's key changes the order, so it really is used.

    The spy orders by ID only; the sources are listed so that ID order
    differs from the date/time order the real key would give.
    """
    calls = []

    def id_only_key(appointment):
        calls.append(appointment.appointment_id)
        return appointment.appointment_id

    monkeypatch.setattr(queries, 'appointment_sort_key', id_only_key)
    late_a = appt('A1', DR1, ELEVEN)
    early_b = appt('A2', DR1, NINE)
    result = select_appointments([early_b, late_a], 'D1')
    assert result == [late_a, early_b]
    assert sorted(calls) == ['A1', 'A2']


# --- QRY-01: practitioner selection ----------------------------------------

def test_select_returns_only_the_requested_practitioner() -> None:
    """Another practitioner's appointment is a control and is excluded."""
    mine = appt('A1', DR1, NINE)
    control = appt('A2', DR2, NINE)
    assert select_appointments([mine, control], 'D1') == [mine]
    assert select_appointments([mine, control], 'D2') == [control]


def test_select_unmatched_practitioner_returns_empty_list() -> None:
    """A practitioner with no appointments gives an empty result."""
    assert select_appointments([appt('A1', DR1, NINE)], 'D9') == []


def test_select_practitioner_match_is_exact_and_case_sensitive() -> None:
    """The pure helper compares IDs exactly: 'd1' is not 'D1'."""
    assert select_appointments([appt('A1', DR1, NINE)], 'd1') == []


# --- QRY-02: status filter -------------------------------------------------

def mixed_statuses():
    """One appointment per status for the same practitioner."""
    return (
        appt('A1', DR1, NINE, SCHEDULED),
        appt('A2', DR1, TEN, CANCELLED),
        appt('A3', DR1, ELEVEN, COMPLETED),
    )


def test_select_default_status_includes_every_status() -> None:
    """Omitted status keeps scheduled, cancelled and completed."""
    scheduled, cancelled, completed = mixed_statuses()
    result = select_appointments([completed, cancelled, scheduled], 'D1')
    assert result == [scheduled, cancelled, completed]


def test_select_explicit_none_status_includes_every_status() -> None:
    """status=None behaves like omitting it."""
    items = list(mixed_statuses())
    assert select_appointments(items, 'D1', None) == items


@pytest.mark.parametrize('wanted, position', [
    (SCHEDULED, 0), (CANCELLED, 1), (COMPLETED, 2),
])
def test_select_explicit_status_keeps_only_that_status(
    wanted, position,
) -> None:
    """Each enum status selects exactly its own appointment."""
    items = list(mixed_statuses())
    assert select_appointments(items, 'D1', wanted) == [items[position]]


def test_select_status_with_no_matches_returns_new_empty_list() -> None:
    """A status nobody has gives [] as a new list, not an error."""
    source = [appt('A1', DR1, NINE, SCHEDULED)]
    result = select_appointments(source, 'D1', CANCELLED)
    assert result == []
    assert result is not source


def test_select_status_filter_applies_to_the_practitioner_only() -> None:
    """Status and practitioner filters combine."""
    mine = appt('A1', DR1, NINE, CANCELLED)
    other = appt('A2', DR2, NINE, CANCELLED)
    assert select_appointments([mine, other], 'D1', CANCELLED) == [mine]


# --- QRY-03: ordering ------------------------------------------------------

def test_select_orders_by_date_time_ascending() -> None:
    """Unsorted input comes back earliest first."""
    a = appt('A1', DR1, ELEVEN)
    b = appt('A2', DR1, NINE)
    c = appt('A3', DR1, TEN)
    assert select_appointments([a, b, c], 'D1') == [b, c, a]


def test_select_breaks_equal_times_by_appointment_id() -> None:
    """Cancelled/completed fixtures share a time without a booking
    conflict; the smaller ID comes first.
    """
    a3 = appt('A3', DR1, NINE, COMPLETED)
    a1 = appt('A1', DR1, NINE, SCHEDULED)
    a2 = appt('A2', DR1, NINE, CANCELLED)
    assert select_appointments([a3, a1, a2], 'D1') == [a1, a2, a3]


def test_select_time_beats_id_in_ordering() -> None:
    """Date/time is compared before the ID tie-break."""
    late_small_id = appt('A1', DR1, TEN)
    early_big_id = appt('A9', DR1, NINE)
    assert select_appointments([late_small_id, early_big_id], 'D1') == [
        early_big_id, late_small_id,
    ]


# --- FP-01 / FP-02: purity, new containers, unchanged objects --------------

def test_select_does_not_change_source_order_or_objects() -> None:
    """Source order, identity and fields are the same after the query."""
    source = [appt('A2', DR1, TEN), appt('A1', DR1, NINE),
              appt('A3', DR2, NINE)]
    before = snapshot(source)
    select_appointments(source, 'D1')
    select_appointments(source, 'D1', SCHEDULED)
    assert snapshot(source) == before


def test_select_returns_a_new_list_with_the_same_objects() -> None:
    """The result is a distinct container holding the same references."""
    a = appt('A1', DR1, NINE)
    b = appt('A2', DR1, TEN)
    source = [a, b]                      # already sorted
    result = select_appointments(source, 'D1')
    assert result is not source
    assert result[0] is a and result[1] is b


def test_select_returns_distinct_list_for_empty_input() -> None:
    """Empty input gives a new empty list each time."""
    source = []
    first = select_appointments(source, 'D1')
    second = select_appointments(source, 'D1')
    assert first == [] and second == []
    assert first is not source
    assert first is not second


def test_select_unsorted_result_is_not_the_source_list() -> None:
    """Sorting happens on a new list, never the argument."""
    source = [appt('A2', DR1, TEN), appt('A1', DR1, NINE)]
    result = select_appointments(source, 'D1')
    assert result is not source
    assert [a.appointment_id for a in source] == ['A2', 'A1']
    assert [a.appointment_id for a in result] == ['A1', 'A2']


def test_select_is_repeatable_for_unchanged_inputs() -> None:
    """The same inputs give the same result every time."""
    source = list(mixed_statuses())
    first = select_appointments(source, 'D1', None)
    second = select_appointments(source, 'D1', None)
    assert first == second
    assert first is not second


def test_select_does_no_input_output(capsys) -> None:
    """A pure query prints nothing."""
    select_appointments([appt('A1', DR1, NINE)], 'D1')
    captured = capsys.readouterr()
    assert captured.out == '' and captured.err == ''


def test_returned_list_can_change_without_affecting_the_source() -> None:
    """Editing the result container leaves the source untouched."""
    source = [appt('A1', DR1, NINE)]
    result = select_appointments(source, 'D1')
    result.clear()
    assert len(source) == 1


# --- Service listing (QRY-04) ----------------------------------------------

def make_session():
    """Fresh store with P1, D1 and D2 registered, plus its services."""
    store = SmartCareDataStore()
    PatientService(store).register_patient('P1', 'Alex Example')
    practitioners = PractitionerService(store)
    practitioners.register_practitioner('D1', 'Taylor Example', 'General')
    practitioners.register_practitioner('D2', 'Morgan Example', 'General')
    return store, AppointmentService(store)


def stored_state(store):
    """Comparable snapshot of every stored record."""
    return (
        [(p.patient_id, p.name) for p in store.list_patients()],
        [(p.practitioner_id, p.name) for p in store.list_practitioners()],
        [(a.appointment_id, a.patient.patient_id,
          a.practitioner.practitioner_id, a.date_time, a.status)
         for a in store.list_appointments()],
    )


def test_listing_known_practitioner_without_appointments_is_empty() -> None:
    """No appointments gives a new empty list and no error."""
    _, service = make_session()
    first = service.list_practitioner_appointments('D1')
    second = service.list_practitioner_appointments('D1')
    assert first == [] and second == []
    assert first is not second


def test_listing_no_matching_status_is_empty_not_an_error() -> None:
    """A known practitioner with no cancelled bookings gets []."""
    _, service = make_session()
    service.book_appointment('A1', 'P1', 'D1', NINE)
    assert service.list_practitioner_appointments('D1', CANCELLED) == []


def test_listing_unknown_practitioner_raises_lookup_error() -> None:
    """A valid but unknown ID is absence, not an invalid ID."""
    _, service = make_session()
    with pytest.raises(LookupError):
        service.list_practitioner_appointments('D9')


@pytest.mark.parametrize('bad_id', ['', '   ', None, 5])
def test_listing_blank_or_invalid_id_raises_value_error(bad_id) -> None:
    """Blank and non-text IDs follow the existing ID contract."""
    _, service = make_session()
    with pytest.raises(ValueError):
        service.list_practitioner_appointments(bad_id)


@pytest.mark.parametrize('bad_status', ['scheduled', 'SCHEDULED', 1, True])
def test_listing_non_enum_status_raises_value_error(bad_status) -> None:
    """Text is not an enum: a known practitioner still gets ValueError."""
    _, service = make_session()
    service.book_appointment('A1', 'P1', 'D1', NINE)
    with pytest.raises(ValueError):
        service.list_practitioner_appointments('D1', bad_status)


def test_listing_case_sensitive_practitioner_id() -> None:
    """'d1' is not 'D1' at the service either."""
    _, service = make_session()
    with pytest.raises(LookupError):
        service.list_practitioner_appointments('d1')


def test_listing_trimmed_practitioner_id_still_finds_appointments() -> None:
    """Accepted surrounding spaces must not give a misleading empty list."""
    _, service = make_session()
    booked = service.book_appointment('A1', 'P1', 'D1', NINE)
    assert service.list_practitioner_appointments('  D1  ') == [booked]


def test_listing_returns_stored_objects_in_order() -> None:
    """Results are the actual stored objects, ordered by time then ID."""
    store, service = make_session()
    late = service.book_appointment('A1', 'P1', 'D1', TEN)
    early = service.book_appointment('A2', 'P1', 'D1', NINE)
    result = service.list_practitioner_appointments('D1')
    assert result == [early, late]
    assert result[0] is store.find_appointment('A2')
    assert result[1] is store.find_appointment('A1')


def test_listing_excludes_other_practitioners() -> None:
    """Another practitioner's bookings never appear (control)."""
    _, service = make_session()
    mine = service.book_appointment('A1', 'P1', 'D1', NINE)
    service.book_appointment('A2', 'P1', 'D2', NINE)
    assert service.list_practitioner_appointments('D1') == [mine]


def test_listing_keeps_cancelled_history_for_default_and_cancelled() -> None:
    """Cancelled appointments stay listable; SCHEDULED-only omits them."""
    store, service = make_session()
    first = service.book_appointment('A1', 'P1', 'D1', NINE)
    second = service.book_appointment('A2', 'P1', 'D1', TEN)
    service.cancel_appointment('A1')
    assert service.list_practitioner_appointments('D1') == [first, second]
    assert service.list_practitioner_appointments('D1', CANCELLED) == [first]
    assert service.list_practitioner_appointments('D1', SCHEDULED) == [second]
    assert store.find_appointment('A1') is first


def test_listing_result_is_a_new_container() -> None:
    """Changing the returned list does not change the store."""
    store, service = make_session()
    service.book_appointment('A1', 'P1', 'D1', NINE)
    before = stored_state(store)
    result = service.list_practitioner_appointments('D1')
    result.clear()
    assert stored_state(store) == before


@pytest.mark.parametrize('practitioner_id, status', [
    ('D9', None), ('', None), ('D1', 'scheduled'),
])
def test_failed_listing_leaves_records_unchanged(
    practitioner_id, status,
) -> None:
    """A rejected request changes no stored record."""
    store, service = make_session()
    service.book_appointment('A1', 'P1', 'D1', NINE)
    service.cancel_appointment('A1')
    before = stored_state(store)
    with pytest.raises((ValueError, LookupError)):
        service.list_practitioner_appointments(practitioner_id, status)
    assert stored_state(store) == before
