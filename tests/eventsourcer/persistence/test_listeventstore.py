import pytest

from eventsourcer.persistence import eventstore as es
from eventsourcer.persistence.listeventstore import ListEventStore, Event, ListEventQuery, ListEventWriter

pytestmark = [pytest.mark.system]

def test_build_should_initialize_members():
    store = ListEventStore.build()

    assert isinstance(store.decoder, es.NoneDecoder)
    assert isinstance(store.encoder, es.NoneEncoder)
    assert isinstance(store.query, ListEventQuery)
    assert isinstance(store.writer, ListEventWriter)

def test_get_should_return_events_stored_with_put():
    store = ListEventStore.build()

    event_one = Event()
    event_one.originator_id = "ABCD"

    store.put([event_one])
    retrieved = store.get("ABCD")
    assert list(retrieved) == [event_one]
