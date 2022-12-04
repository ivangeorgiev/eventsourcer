# %%
from abc import abstractmethod
from dataclasses import asdict, dataclass
from datetime import datetime
from enum import Enum
from functools import singledispatch
from typing import ClassVar, Dict, List, Type
import uuid

CustomerId = uuid.UUID
ProductId = uuid.UUID
OrderId = uuid.UUID


@dataclass(frozen=True)
class Event:
    _subclasses: ClassVar[Dict[str, Type]] = {}

    created_at: datetime
    version: int

    def __init_subclass__(cls) -> None:
        print(f"Registered event {cls.__name__}")
        Event._subclasses[cls.__name__] = cls

    @classmethod
    def subclass_for_name(cls, name: str) -> Type:
        return cls._subclasses[name]

    def as_dict(self) -> dict:
        dict_repr = asdict(self)
        dict_repr.pop("created_at")
        dict_repr.pop("version")
        return dict_repr

    def mutate(self, instance):
        instance.version = self.version
        return instance


@dataclass(frozen=True)
class OrderDrafted(Event):
    order_id: OrderId
    customer_id: CustomerId

    def mutate(self, instance):
        assert instance is None
        instance = OrderState(self.order_id, self.customer_id)
        return instance


@dataclass(frozen=True)
class OrderConfirmed(Event):
    pass


@dataclass(frozen=True)
class EventStream:
    origin_id: uuid.UUID
    events: List[Event]
    version: int


@dataclass(frozen=True)
class EventSequence:
    aggregate_id: uuid.UUID
    events: List[Event]
    version: int


class OrderStatus(Enum):
    NEW = "new"
    CONFIRMED = "confirmed"


@dataclass(frozen=True)
class AggregateChanges:
    aggregate_id: uuid.UUID
    events: List[Event]
    expected_version: int

# %%
class IllegalStatusChange(Exception):
    pass

# %%


class OrderState:
    id: OrderId
    customer_id: CustomerId
    satus: OrderStatus
    version: int

    @dataclass(frozen=True)
    class OrderDrafted(Event):
        order_id: OrderId
        customer_id: CustomerId

        def mutate(self, instance: "OrderState"):
            assert instance is None
            instance = OrderState(id=OrderId)
            instance.customer_id = self.customer_id
            instance.status = OrderStatus.NEW
            return super().mutate(instance)

    @dataclass(frozen=True)
    class OrderConfirmed(Event):
        def mutate(self, instance: "OrderState"):
            instance.status = OrderStatus.CONFIRMED
            return super().mutate(instance)

    def __init__(self, id: OrderId):
        self._lines: Dict[ProductId, int] = {}
        self.id = id


class OrderAggregate:
    order: OrderState = None
    _pending_events: List[Event]

    def __init__(self) -> None:
        self._pending_events = []

    def notify(self, event: Event) -> None:
        self._pending_events.append(event)
        self.order = event.mutate(self.order)

    @classmethod
    def from_events(cls, events: EventSequence):
        aggregate = cls()

        for event in events.events:
            aggregate.order = event.mutate(aggregate.order)
        return aggregate

    @classmethod
    def draft(cls, order_id: OrderId, customer_id: CustomerId):
        aggregate = cls()
        aggregate.notify(
            OrderState.OrderDrafted(
                datetime.now(),
                0,
                order_id,
                customer_id,
            )
        )
        return aggregate

    @property
    def id(self):
        return self._id

    @property
    def _next_version(self):
        return self.order.version + 1

    @property
    def changes(self) -> AggregateChanges:
        return AggregateChanges(self._id, self._pending_events[:], self._version)

    def confirm(self) -> None:
        if self.order.status != OrderStatus.NEW:
            raise IllegalStatusChange("Only NEW order can be confirmed!")
        event = OrderState.OrderConfirmed(datetime.now(), self._next_version)
        self.notify(event)


# %%

order_id = uuid.uuid4()
order_drafted = OrderState.OrderDrafted(datetime.now(), 0, order_id, None)
events = EventSequence(order_id, [order_drafted], 0)

order = OrderAggregate.from_events(events)

# %%
order
order.order.status
# %%

order = OrderAggregate.draft(uuid.uuid4(), '123')

print(order.order.status)
print(order.order.version)
# %%
order.confirm()

# %%
print(order.order.status)
print(order.order.version)
# %%
