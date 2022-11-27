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


class EventDecoder(ABC, Generic[StoredEventT]):
    """Generic event decoder"""

    @abstractmethod
    def decode(self, obj: StoredEventT) -> Event:
        """Decode event from store representation"""


class Writer(Generic[StoredEventT]):
    """Generic event store writer"""

    @abstractmethod
    def write(self, events: Iterable[StoredEventT]):
        """Writes a sequence of stored events to the store"""


class Reader(Generic[StoredEventT]):
    """Generic event store reader"""

    @abstractmethod
    def read(self, originator_id) -> Iterable[StoredEventT]:
        """Reads a sequence of stored events from the store"""


class EventStore(Generic[StoredEventT]):
    """Event store"""

    encoder: EventEncoder[StoredEventT]
    decoder: EventDecoder[StoredEventT]
    writer: Writer[StoredEventT]
    reader: Reader[StoredEventT]

    def get(self, originator_id) -> Iterable[Event]:
        """Get events orriginated at originator_id"""
        return (
            self.decoder.decode(stored) for stored in self.reader.read(originator_id)
        )

    def put(self, events: Iterable[Event]):
        """Append events to event store"""
        self.writer.write((self.encoder.encode(event) for event in events))
