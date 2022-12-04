import abc
import dataclasses
import inspect
import typing as t
from types import FunctionType
import uuid

TArgs = t.Dict[str, t.Any]
EventHandler = t.Callable
EventId = str

event_id_factory = lambda : str(uuid.uuid4())

@dataclasses.dataclass(frozen=True)
class Event:
    name: str
    args: TArgs = dataclasses.field(default_factory=dict)
    id: EventId = dataclasses.field(default_factory=event_id_factory)


class EventListener(abc.ABC):
    @abc.abstractmethod
    def notify(self, event: Event):
        """Notify listener about event"""


EventNotifier = t.Callable[[EventListener, Event], None]


def event_notifier(listener: EventListener, event: Event) -> None:
    """Invoke `notify` method on event listener."""
    assert isinstance(listener, EventListener) or hasattr(listener, "notify")
    getattr(listener, "notify")(event)


class EventBus:
    """Event handlers registry"""

    _handlers: dict[str, EventHandler]
    _notifier: EventNotifier

    def __init__(self, notifier: EventNotifier = None):
        self._handlers = {}
        self._notifier = notifier or event_notifier

    def register(self, event_name: str, handler: EventHandler):
        registered_handler = self._handlers.get(event_name, None)
        if registered_handler is handler:
            return
        if registered_handler:
            raise KeyError("Event name has already been registered")
        self._handlers[event_name] = handler

    def get(self, event_name: str, default: EventHandler = ...):
        if default is not ...:
            return self._handlers.get(event_name, default)
        return self[event_name]

    def handle(self, instance: t.Any, event: Event):
        self[event.name](instance, **event.args)

    def trigger(self, instance: t.Any, event: Event) -> None:
        self.handle(instance, event)
        self._notifier(instance, event)

    def __getitem__(self, event_name: str) -> EventHandler:
        return self._handlers[event_name]

    def __bool__(self):
        return True


class EventDecorator:
    _bus: EventBus

    def __init__(self, registry: EventBus = None):
        self._bus = registry or EventBus()

    @t.overload
    def __call__(self, func: FunctionType) -> t.Any:
        """Register command method as event handler, using it's name as event name"""

    @t.overload
    def __call__(self, func: None = None) -> t.Any:
        """Register command method as event handler, using it's name as event name"""

    @t.overload
    def __call__(self, name: str) -> t.Any:
        """Register command method as event handler for events with given event name"""

    def __call__(self, arg: t.Union[str, None, FunctionType] = None) -> t.Any:
        def decorator(f, name: str):
            def decorate(f):
                def wrapper(instance, *args, **kwargs):
                    ba = signature.bind(instance, *args, **kwargs).arguments
                    ba.pop("self")
                    ev = Event(event_name, ba)
                    return self._bus.trigger(instance, ev)

                event_name = name or f.__name__
                self._bus.register(event_name, f)
                signature = inspect.signature(f)
                return wrapper

            if f is None:
                return decorate
            else:
                return decorate(f)

        if isinstance(arg, str):
            return decorator(None, arg)
        if isinstance(arg, (FunctionType)):
            return decorator(arg, None)
        if arg is None:
            return decorator(None, None)
        raise TypeError(f"Expected str, None or FunctionType, but got {type(arg)}")



class EventAggregateMeta(type):
    def __new__(cls, name, bases, dct):
        dct['_pending_events'] = []
        aggregate = super().__new__(cls, name, bases, dct)
        return aggregate


class EventAggregate(metaclass=EventAggregateMeta):
    _pending_events: list

    def __init__(self):
        self._pending_events = list()

    def notify(self, event: Event):
        self._pending_events.append(event)

    def collect_events(self) -> t.Iterable[Event]:
        while self._pending_events:
            yield self._pending_events.pop(0)

