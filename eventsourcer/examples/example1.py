from eventsourcer.event import EventAggregate, EventDecorator, EventRegistry

registry = EventRegistry()
emit = EventDecorator(registry)


class Dog(EventAggregate):
    @emit("DogCreated")
    def __init__(self, name):
        self.name = name
        self.tricks = []

    @emit("TrickAdded")
    def add_trick(self, trick):
        self.tricks.append(trick)


dog = Dog(name="Roxie")

assert dog.name == "Roxie"
assert dog.tricks == []
assert len(dog.pending_events) == 1
assert dog.pending_events[-1].name == "DogCreated"

dog.add_trick(trick="roll over")
assert len(dog.pending_events) == 2
assert dog.pending_events[-1].name == "TrickAdded"


#
projected_dog = Dog.__new__(Dog)
for ev in dog.collect_events():
    print(f"Apply event: {ev}")
    registry.apply(projected_dog, ev)
assert projected_dog.name == "Roxie"
assert projected_dog.tricks == ["roll over"]
assert not projected_dog.pending_events
