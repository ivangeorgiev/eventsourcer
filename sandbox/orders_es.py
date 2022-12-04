# %%
import inspect
from types import FunctionType
from typing import overload
from eventsourcing.domain import event

import pytest

class EventDecorator:
    name: str
    func: FunctionType

    def __init__(self, name: str = None):
        self.name = name

    def decorate(self, func: FunctionType):
        self.func = func
        if not self.name:
            self.name = func.__name__
        return self

    def __call__(self, *args, **kwargs):
        print(f"EVENT: {self.name}(*{args}, **{kwargs})")
        return self.func(*args, **kwargs)

# @overload
# def event(func: FunctionType):
#     ...

@overload
def event(func: FunctionType):
    ...

@overload
def event(func: None = None):
    ...

@overload
def event(name: str):
    ...


# @overload
# def event(*args, **kwargs):
#     ...

# @overload
# def event(arg:None = None,)

def event(arg=None):
    if isinstance(arg, (FunctionType)):
        decorator = EventDecorator(arg.__name__)
        return decorator.decorate(arg)
    else:
        decorator = EventDecorator(arg)
        return decorator.decorate

@event
def f1(name):
    print(f"Hello {name}")

# %%
print(f1)
f1("Ivan")

# %%

@event()
def f2(name):
    print(f"Good night {name}")
print(f2)
f2("Ivan")

# %%
@event("MorningCame")
def f3(name):
    print(f"Good morning {name}")
print(f3)
f3("Ivan")



# %%
def a(x, y, z=1, m=3, n=4):
    ...

params = inspect.signature(a).parameters
print(params.items())

a = inspect.signature(a).bind(*('X', 'Y'))
a.apply_defaults()
print(a.arguments)
# %%



class event:
    pass


class Dog:
    @event('Registered')
    def __init__(self, name):
        self.name = name
        self.tricks = []

    @event('TrickAdded')
    def add_trick(self, trick):
        self.tricks.append(trick)


