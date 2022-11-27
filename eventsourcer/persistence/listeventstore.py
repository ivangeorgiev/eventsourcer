"""EventStore implementation with POPO and list

ListEventStore stores event in memory as a list of (<originator_id>, <event>) tuples.
<originator_id> is retrieved by the writer, using the `originator_id_getter` callable.
Since this is an in-memory store, events are stored un-encoded.
"""

from collections.abc import Iterable
import operator

from .eventstore import (
    Event,
    EventQuery,
    EventStore,
    EventWriter,
    NoneDecoder,
    NoneEncoder,
)


class ListEventQuery(EventQuery[Event]):
    """List Event Query"""

    _event_list: list[Event]

    def __init__(self, event_list: list[Event]):
        self._event_list = event_list

    def execute(self, originator_id) -> Iterable[Event]:
        return (
            event
            for event_originator_id, event in self._event_list
            if event_originator_id == originator_id
        )


class ListEventWriter(EventWriter[Event]):
    """List Event Writer"""

    _event_list: list[Event]
    originator_id_getter = operator.attrgetter("originator_id")

    def __init__(self, event_list: list[Event]):
        self._event_list = event_list

    def append_all(self, sequence: Iterable[Event]):
        self._event_list.extend(
            ((self.originator_id_getter(event), event) for event in sequence)
        )


class ListEventStore(EventStore[Event]):
    """Event store implementation using python List"""

    _event_list: list[Event]

    @classmethod
    def build(cls) -> "ListEventStore":
        """Build ListEventStore instance"""
        store = cls()
        store._event_list = []
        store.decoder = NoneDecoder()
        store.encoder = NoneEncoder()
        store.query = ListEventQuery(store._event_list)
        store.writer = ListEventWriter(store._event_list)
        return store
