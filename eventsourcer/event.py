import dataclasses
import datetime as dt
import typing as t

TEntityId = t.TypeVar("TEntityId")

@dataclasses.dataclass(frozen=True)
class Event:
    _subclasses: t.ClassVar[t.Dict[str,t.Type]] = {}

    version: int = 0
    created_at: dt.datetime = dataclasses.field(default_factory=lambda: dt.datetime.utcnow())

    def __init_subclass__(cls) -> None:
        """Register subclasses"""
        Event._subclasses[cls.__module__ + "." + cls.__name__] = cls

    @classmethod
    def subclass_for_name(cls, name: str) -> t.Type:
        """Get subclass by name"""
        return Event._subclasses[name]

    def as_dict(self):
        return dataclasses.asdict(self)

@dataclasses.dataclass(frozen=True)
class EventSequence(t.Generic[TEntityId]):
    entity_id: TEntityId
    version: int
    _events: t.List[Event] = dataclasses.field(default_factory=list, init=False)

    @property
    def events(self) -> t.Sequence[Event]:
        return self._events

    def append(self, event: Event) -> "EventSequence":
        self._events.append(event)
        return self
