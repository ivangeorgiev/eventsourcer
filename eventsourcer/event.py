from __future__ import annotations

import abc
import dataclasses
import inspect
import typing as t
from collections.abc import Iterable
from types import FunctionType

TArgs = t.Dict[str, t.Any]
EventHandler = t.Callable
EventId = str


@dataclasses.dataclass(frozen=True)
class Event:
    name: str
    args: TArgs = dataclasses.field(default_factory=dict)


class EventListener(abc.ABC):
    @abc.abstractmethod
    def notify(self, event: Event) -> None:
        """Notify listener about event"""


EventEmiter = t.Callable[[EventListener, Event], None]


def notify_listener(listener: EventListener, event: Event) -> None:
    """Invoke `notify` method on event listener."""
    assert isinstance(listener, EventListener) or hasattr(listener, "notify")
    getattr(listener, "notify")(event)


class EventRegistry:
    """Event handlers registry"""

    _handlers: dict[str, EventHandler]

    def __init__(self):
        self._handlers = {}

    def register(self, event_name: str, handler: EventHandler):
        registered_handler = self._handlers.get(event_name, None)
        if registered_handler is handler:
            return
        if registered_handler:
            raise KeyError("Event name has already been registered")
        self._handlers[event_name] = handler

    def get(self, event_name: str, default: EventHandler | None = None):
        if default is None:
            return self[event_name]
        return self._handlers.get(event_name, default)

    def apply(self, instance: t.Any, event: Event):
        self[event.name](instance, **event.args)

    def __getitem__(self, event_name: str) -> EventHandler:
        return self._handlers[event_name]

    def __bool__(self):
        return True


class EventDecorator:
    _registry: EventRegistry
    _emiter: EventEmiter

    def __init__(
        self, registry: EventRegistry | None = None, emiter: EventEmiter | None = None
    ):
        self._registry = registry or EventRegistry()
        self._emiter = emiter or notify_listener

    @t.overload
    def __call__(self, arg: FunctionType) -> t.Any:
        """Register command method as event handler, using it's name as event name"""

    @t.overload
    def __call__(self, arg: None = None) -> t.Any:
        """Register command method as event handler, using it's name as event name"""

    @t.overload
    def __call__(self, arg: str) -> t.Any:
        """Register command method as event handler for events with given event name"""

    def __call__(self, arg: str | None | FunctionType = None) -> t.Any:
        def decorator(f, name: str | None):
            def decorate(f):
                def wrapper(instance, *args, **kwargs):
                    ba = signature.bind(instance, *args, **kwargs).arguments
                    ba.pop("self")
                    ev = Event(event_name, ba)
                    self._registry.apply(instance, ev)
                    self._emiter(instance, ev)

                event_name = name or f.__name__
                self._registry.register(event_name, f)
                signature = inspect.signature(f)
                return wrapper

            if f is None:
                return decorate
            return decorate(f)

        if isinstance(arg, str):
            return decorator(None, arg)
        if isinstance(arg, (FunctionType)):
            return decorator(arg, None)
        if arg is None:
            return decorator(None, None)
        raise TypeError(f"Expected str, None or FunctionType, but got {type(arg)}")


class EventAggregate(EventListener):
    _pending_events: list

    @property
    def pending_events(self):
        if not hasattr(self, "_pending_events"):
            self._pending_events = []
        return self._pending_events

    def notify(self, event: Event) -> None:
        self.pending_events.append(event)

    def collect_events(self) -> Iterable[Event]:
        pending_events = self.pending_events
        while pending_events:
            yield pending_events.pop(0)
