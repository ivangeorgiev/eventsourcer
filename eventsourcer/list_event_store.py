import datetime as dt
import typing as t

from .event import Event, EventSequence, TEntityId
from .event_store import EventStore


class NotFoundError(Exception):
    pass


class ListEventStore(EventStore[TEntityId]):
    _store = t.List[t.Dict]

    def __init__(self) -> None:
        self._store = []

    def load(self, entity_id: TEntityId) -> EventSequence[TEntityId]:
        events = []
        for record in self._store:
            if record["entity_id"] != entity_id:
                continue
            args = record["data"].copy()
            args["version"] = record["version"]
            args["created_at"] = record["created_at"]
            event = Event.subclass_for_name(record["event_type"])(**args)
            events.append(event)
        if not events:
            raise NotFoundError()
        result = EventSequence(entity_id, event.version)
        result.events.extend(events)
        return result

    def save(self, events: EventSequence[TEntityId]):
        for event in events.events:
            event_class = event.__class__
            event_data = event.as_dict()
            event_data.pop("version")
            event_data.pop("created_at")
            self._store.append(
                {
                    "entity_id": events.entity_id,
                    "event_type": event_class.__module__ + "." + event_class.__name__,
                    "data": event_data,
                    "created_at": event.created_at,
                    "version": event.version,
                }
            )
