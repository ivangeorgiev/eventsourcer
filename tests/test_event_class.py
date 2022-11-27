"""Tests for Event class"""

import pytest
from eventsourcer.event import Event


class FakeEvent(Event):
    pass


def test_should_register_subclass():
    assert Event._subclasses["tests.test_event_class.FakeEvent"] is FakeEvent


def test_subclass_for_name_should_return_subclass():
    assert Event.subclass_for_name("tests.test_event_class.FakeEvent") is FakeEvent


def test_subclass_for_name_should_raise_keyerror_not_found():
    with pytest.raises(KeyError):
        Event.subclass_for_name("not-existing")
