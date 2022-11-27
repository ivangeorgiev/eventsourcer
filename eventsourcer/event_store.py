import abc
import typing as t

from .event import EventSequence, TEntityId


class EventStore(t.Generic[TEntityId], abc.ABC):
    @abc.abstractmethod
    def load(self, entity_id: TEntityId) -> EventSequence[TEntityId]:
        """Load event stream for an entity from event store"""

    @abc.abstractmethod
    def save(self, events: EventSequence[TEntityId]):
        """Append list of events to event stream"""

