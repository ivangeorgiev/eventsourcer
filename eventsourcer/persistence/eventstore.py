"""General purpose event store implementation."""

from abc import ABC, abstractmethod
from collections.abc import Iterable
from typing import Any, Generic, TypeVar

StoredEventT = TypeVar("StoredEventT")


class Event:
    """Generic event"""

    originator_id: Any


class EventEncoder(Generic[StoredEventT], ABC):
    """Generic event encoder"""

    @abstractmethod
    def encode(self, event: Event) -> StoredEventT:
        """Encode event into store representation"""


class NoneEncoder(EventEncoder[Event]):
    """No change encoder"""

    def encode(self, event: Event) -> Event:
        return event


class EventDecoder(ABC, Generic[StoredEventT]):
    """Generic event decoder"""

    @abstractmethod
    def decode(self, obj: StoredEventT) -> Event:
        """Decode event from store representation"""


class NoneDecoder(EventDecoder[Event]):
    """No change decoder"""

    def decode(self, obj: Event) -> Event:
        return obj


class EventWriter(Generic[StoredEventT]):
    """Generic event writer"""

    @abstractmethod
    def append_all(self, sequence: Iterable[StoredEventT]):
        """Append a sequence of events to the store"""


class EventQuery(Generic[StoredEventT]):
    """Generic event query"""

    @abstractmethod
    def execute(self, originator_id) -> Iterable[StoredEventT]:
        """Get event sequence from the store"""


class EventStore(Generic[StoredEventT]):
    """Event store"""

    encoder: EventEncoder[StoredEventT]
    decoder: EventDecoder[StoredEventT]
    writer: EventWriter[StoredEventT]
    query: EventQuery[StoredEventT]

    def get(self, originator_id) -> Iterable[Event]:
        """Get events orriginated at originator_id"""
        return (
            self.decoder.decode(stored) for stored in self.query.execute(originator_id)
        )

    def put(self, events: Iterable[Event]):
        """Append events to event store"""
        self.writer.append_all((self.encoder.encode(event) for event in events))
