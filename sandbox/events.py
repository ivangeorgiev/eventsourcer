# %%
import inspect
from types import FunctionType
from typing import Any, Callable, NamedTuple, Union, overload


class Event(NamedTuple):
    name: str
    args: dict


class eventMeta(type):
    handlers: dict[str, Callable] = {}

    @overload
    def __call__(self, func: FunctionType) -> Any:
        ...

    @overload
    def __call__(self, func: None = None) -> Any:
        ...

    @overload
    def __call__(self, name: str) -> Any:
        ...

    def __call__(self, arg: Union[str, None, FunctionType] = None) -> Any:
        def decorator(f, name: str):
            def decorate(f):
                def wrapper(instance, *args, **kwargs):
                    ba = signature.bind(instance, *args, **kwargs).arguments
                    ba.pop("self")
                    ev = Event(event_name, ba)
                    if hasattr(instance, "push_event"):
                        instance.push_event(ev)
                    return self.apply(instance, ev)

                event_name = name or f.__name__
                self.handlers[event_name or f.__name__] = f
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

    @classmethod
    def apply(cls, instance, ev: Event):
        return cls.handlers[ev.name](instance, **ev.args)


class event(metaclass=eventMeta):
    @classmethod
    def apply(cls, instance: any, ev: Event):
        cls.__class__.apply(instance, ev)


# %%


class EventAware:
    _pending_events: list[Event] = None

    def push_event(self, event: Event):
        if self._pending_events is None:
            self._pending_events = []
        self._pending_events.append(event)

    def collect_events(self):
        while self._pending_events:
            yield self._pending_events.pop(0)


class Aggregate(EventAware):
    pass


class Dog(EventAware):
    @event("DogCreated")
    def __init__(self, name):
        self.name = name
        self.tricks = []

    @event("TrickAdded")
    def add_trick(self, trick):
        self.tricks.append(trick)



# %%

dog = Dog(name="Fido")

assert dog.name == "Fido"
assert dog.tricks == []
dog.add_trick(trick="roll over")

# %%
assert dog.tricks == ["roll over"]

assert dog._pending_events == [
    Event(name="DogCreated", args={"name": "Fido"}),
    Event(name="TrickAdded", args={"trick": "roll over"}),
]

# %%

restored_dog = Dog.__new__(Dog)
for ev in dog.collect_events():
    print(f"Apply event: {ev}")
    event.apply(restored_dog, ev)
assert restored_dog.name == "Fido"
assert restored_dog.tricks == ["roll over"]
assert not restored_dog._pending_events

# %%

roxie = Dog.__new__(Dog)
event.apply(roxie, Event("DogCreated", {"name": "Roxie"}))
assert roxie.name == "Roxie"

event.apply(roxie, Event("TrickAdded", {"trick": "climb"}))
assert roxie.tricks == ["climb"]

assert not roxie._pending_events

# %%

