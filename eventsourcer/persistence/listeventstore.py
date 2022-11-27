"""EventStore implementation with POPO and list"""

import operator
from collections.abc import Callable, Iterable
from typing import Any, NamedTuple

from .eventstore import Event, EventDecoder, EventEncoder, EventStore, Reader, Writer

ORIGINATOR_ID_ATTR = "originator_id"

OriginatorIdT = Any


class ListStoredEvent(NamedTuple):
    originator_id: OriginatorIdT
    event: Event


EventStoreList = list[ListStoredEvent]


class ListEventEncoder(EventEncoder):
    originator_id_getter: Callable[[Event], Any]

    def __init__(self, originator_id_attr: str = ORIGINATOR_ID_ATTR):
        self.originator_id_getter = operator.attrgetter(originator_id_attr)

    def encode(self, event: Event) -> ListStoredEvent:
        return ListStoredEvent(self.originator_id_getter(event), event)


class ListEventDecoder(EventDecoder[ListStoredEvent]):
    def decode(self, obj: ListStoredEvent) -> Event:
        return obj.event


class ListEventReader(Reader[ListStoredEvent]):
    """List Event Query"""

    _event_list: EventStoreList

    def __init__(self, event_list: EventStoreList):
        self._event_list = event_list

    def read(self, originator_id) -> Iterable[ListStoredEvent]:
        return (
            event for event in self._event_list if event.originator_id == originator_id
        )


class ListEventWriter(Writer[ListStoredEvent]):
    """List Event Writer"""

    _event_list: EventStoreList

    def __init__(self, event_list: EventStoreList):
        self._event_list = event_list

    def write(self, events: Iterable[ListStoredEvent]):
        self._event_list.extend(events)


class ListEventStore(EventStore[ListStoredEvent]):
    """
    EventStore implementation with POPO and list

    ListEventStore stores events in-memory as a list of named tuples.
    <originator_id> is retrieved by the encoder, using the `originator_id_getter` callable.
    Since this is an in-memory store, events are not further encoded.

    To create `ListEventStore` instances, use the provided `build()` factory method.

    Example:
    ---------
    ```python
    # Build ListEventStore instance:
    store = ListEventStore.build()

    # Add events to the event store:
    store.put(events)

    # Retrieve events originated at 'abcd':
    store.get('abcd')
    ```
    """

    _event_list: EventStoreList

    @classmethod
    def build(cls, originator_id_attr: str = ORIGINATOR_ID_ATTR) -> "ListEventStore":
        """Build ListEventStore instance"""
        store = cls()
        store._event_list = []
        store.decoder = ListEventDecoder()
        store.encoder = ListEventEncoder(originator_id_attr)
        store.reader = ListEventReader(store._event_list)
        store.writer = ListEventWriter(store._event_list)
        return store
