from eventsourcing.domain import Aggregate, event

class Dog(Aggregate):
    @event('Registered')
    def __init__(self, name):
        self.name = name
        self.tricks = []

    @event('TrickAdded')
    def add_trick(self, trick):
        self.tricks.append(trick)

dog = Dog(name='Fido')

assert isinstance(dog, Dog)
assert isinstance(dog, Aggregate)

assert dog.name == 'Fido'
assert dog.tricks == []

from uuid import UUID

assert isinstance(dog.id, UUID)

dog.add_trick(trick='roll over')

assert dog.tricks == ['roll over']

events = dog.collect_events()

copy = None
for e in events:
    copy = e.mutate(copy)

assert copy == dog

