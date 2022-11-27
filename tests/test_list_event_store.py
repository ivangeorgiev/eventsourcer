import datetime as dt
import pytest
from freezegun import freeze_time
from eventsourcer.list_event_store import ListEventStore, NotFoundError
from eventsourcer.event import Event, EventSequence

class FakeEvent(Event):
    pass

@freeze_time("2022-11-01 12:00:01")
def test_save_should_append_to_store_list():
    store = ListEventStore()
    events = EventSequence(1, 0).append(FakeEvent())
    store.save(events)

    assert store._store == [
        {
            "entity_id": 1,
            "event_type": FakeEvent.__module__ + ".FakeEvent",
            "version": 0,
            "created_at": dt.datetime.fromisoformat("2022-11-01T12:00:01"),
            "data": {}
        }
    ]


@freeze_time("2022-11-21 12:00:01")
def test_load_should_retrieve_events():
    store = ListEventStore()
    store._store.append(
        {
            "entity_id": 1,
            "event_type": FakeEvent.__module__ + ".FakeEvent",
            "version": 0,
            "created_at": dt.datetime.fromisoformat("2022-11-21T12:00:01"),
            "data": {}
        })

    actual = store.load(1)

    assert actual == EventSequence(1, 0).append(FakeEvent())

def test_load_should_raise_notfounderror_entity_not_in_store():
    store = ListEventStore()
    with pytest.raises(NotFoundError):
        store.load(10)
