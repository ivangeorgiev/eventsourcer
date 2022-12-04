from ast import Dict
from dataclasses import asdict, dataclass
from datetime import datetime
from enum import Enum
from typing import ClassVar, List, Type
import uuid

CustomerId = uuid.UUID
ProductId = uuid.UUID


@dataclass(frozen=True)
class Event:
    _subclasses: ClassVar[Dict[str, Type]]

    created_at: datetime
    version: int

    def __init_subclass__(cls) -> None:
        Event._subclasses[cls.__name__] = cls

    @classmethod
    def subclass_for_name(cls, name: str) -> Type:
        return cls._subclasses[name]

    def as_dict(self) -> dict:
        dict_repr = asdict(self)
        dict_repr.pop("created_at")
        dict_repr.pop("version")
        return dict_repr


@dataclass(frozen=True)
class OrderDrafted(Event):
    customer_id: CustomerId


@dataclass(frozen=True)
class OrderConfirmed(Event):
    pass


@dataclass(frozen=True)
class EventStream:
    origin_id: uuid.UUID
    events: List[Event]
    version: int


class OrderStatus(Enum):
    NEW = "new"
    CONFIRMED = "confirmed"


@dataclass(frozen=True)
class AggregateChanges:
    aggregate_id: uuid.UUID
    events: List[Event]
    epected_version: int

class IllegalStatusChange(Exception):
    pass

class Order:
    def __init__(self, event_stream: EventStream) -> None:
        self._id = event_stream.origin_id
        self._version = event_stream.version
        self._customer_id = 0
        self._status = OrderStatus.NEW
        self._lines: Dict[ProductId, int] = {}
        for event in event_stream.events:
            self._apply(event)

        self._pending_events = []

    @property
    def id(self):
        return self._id

    @property
    def next_version(self):
        return self._version + 1

    @property
    def changes(self) -> AggregateChanges:
        return AggregateChanges(self._id, self._pending_events[:], self._version)

    def _apply(self, event: Event) -> None:
        if isinstance(event, OrderDrafted):
            self._customer_id = event.customer_id
            self._status = OrderStatus.NEW
        elif isinstance(event, OrderConfirmed):
            self._status = OrderStatus.CONFIRMED
        else:
            raise ValueError(f"Unknown event {event}")

    @classmethod
    def draft(cls, id: uuid.UUID, customer_id: CustomerId) -> "Order":
        instance = cls(EventStream(id=id, version=0, events=[]))
        instance._pending_events = [
            OrderDrafted(
                datetime.now(),
                0,
                customer_id,
            )
        ]
        return instance

    def confirm(self) -> None:
        if self._status != OrderStatus.NEW:
            raise IllegalStatusChange("Only NEW order can be confirmed!")
        event = OrderConfirmed[datetime.now(), self._next_version]
        self._apply(event)
        self._pending_events.append(event)
