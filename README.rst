============
eventsourcer
============


.. image:: https://img.shields.io/pypi/v/eventsourcer.svg
        :target: https://pypi.python.org/pypi/eventsourcer

.. image:: https://img.shields.io/travis/ivangeorgiev/eventsourcer.svg
        :target: https://travis-ci.com/ivangeorgiev/eventsourcer

.. image:: https://readthedocs.org/projects/eventsourcer/badge/?version=latest
        :target: https://eventsourcer.readthedocs.io/en/latest/?version=latest
        :alt: Documentation Status




Python Eventsourcing


* Free software: GNU General Public License v3
* Documentation: https://eventsourcer.readthedocs.io.


Features
--------

* TODO

Example
--------

.. code-block::python

    from eventsourcer.event import EventDecorator, EventAggregate, EventRegistry

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


Credits
-------

This package was created with Cookiecutter_ and the `audreyr/cookiecutter-pypackage`_ project template.

.. _Cookiecutter: https://github.com/audreyr/cookiecutter
.. _`audreyr/cookiecutter-pypackage`: https://github.com/audreyr/cookiecutter-pypackage
