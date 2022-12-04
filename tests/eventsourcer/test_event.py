from unittest.mock import Mock, patch
import pytest

from eventsourcer import event as ev

pytestmark = pytest.mark.unit


class Test_event_notifier:
    def test_should_call_listener_notify(self):
        class Listener(ev.EventListener):
            notified: ev.Event = None

            def notify(self, event: ev.Event):
                self.notified = event

        listener = Listener()
        event = Mock()

        ev.notify_listener(listener, event)

        assert listener.notified is event

    def test_should_call_notify_ductyping(self):
        class Listener:
            notified: ev.Event = None

            def notify(self, event: ev.Event):
                self.notified = event

        listener = Listener()
        event = Mock()

        ev.notify_listener(listener, event)

        assert listener.notified is event

    def test_should_raise_assertionerror_not_listener(self):
        class Listener:
            pass

        listener = Listener()
        event = Mock()

        with pytest.raises(AssertionError):
            ev.notify_listener(listener, event)


class TestEventRegistry:
    @pytest.fixture(name="registry")
    def given_registry(self):
        return ev.EventRegistry()

    def test_should_initialize_defaults(self):
        registry = ev.EventRegistry()
        assert isinstance(registry, ev.EventRegistry)
        assert registry._handlers == {}

    def test_register_should_add_handler(self, registry: ev.EventRegistry):
        handler = Mock()

        registry.register("my_event", handler)

        assert registry._handlers["my_event"] is handler

    def test_register_should_raise_keyerror_event_with_different_handler_already_register(
        slef, registry: ev.EventRegistry
    ):
        handler1 = Mock()
        handler2 = Mock()
        registry.register("my_event", handler1)

        with pytest.raises(KeyError):
            registry.register("my_event", handler2)

    def test_register_should_accept_full_dulicate_registrtion(
        self, registry: ev.EventRegistry
    ):
        handler = Mock()
        registry.register("my_event", handler)

        registry.register("my_event", handler)

        assert registry._handlers["my_event"] is handler

    def test_dict_access_should_return_registered_handler(
        self, registry: ev.EventRegistry
    ):
        handler = Mock()
        registry.register("my_event", handler)

        assert registry["my_event"] is handler

    def test_get_should_return_registered_handler(self, registry: ev.EventRegistry):
        handler = Mock()
        registry.register("my_event", handler)

        assert registry.get("my_event") is handler

    def test_get_should_return_passed_default_for_unregistered_handler(
        self, registry: ev.EventRegistry
    ):
        handler = Mock()

        assert registry.get("my_event", handler) is handler

    def test_get_should_raise_keyerror_default_not_passed_for_unregistered_handler(
        self, registry: ev.EventRegistry
    ):
        with pytest.raises(KeyError):
            registry.get("my_event")

    def test_bool_should_be_true(self, registry: ev.EventRegistry):
        assert bool(registry)

    def test_handle_should_invoke_handler_with_event_args(
        self, registry: ev.EventRegistry
    ):
        instance = Mock()
        handler = Mock()
        event = ev.Event("my_event", {"a": 1})
        registry.register("my_event", handler)

        registry.apply(instance, event)

        handler.assert_called_once_with(instance, **event.args)


class TestEventDecorator:
    @pytest.fixture(name="registry")
    def given_registry(self):
        return ev.EventRegistry()

    @pytest.fixture(name="decorator")
    def given_decorator(self, registry):
        return ev.EventDecorator(registry)

    def test_should_initialize_instance_with_defaults(self):
        decorator = ev.EventDecorator()
        assert isinstance(decorator._registry, ev.EventRegistry)

    def test_should_initialize_instance_with_passed_values(self):
        registry = Mock()
        decorator = ev.EventDecorator(registry)
        assert decorator._registry is registry

    def test_decorate_without_brackets_should_register_handler(
        self, decorator: ev.EventDecorator, registry: ev.EventRegistry
    ):
        def fake_command():
            pass

        decorator(fake_command)

        assert registry["fake_command"] is fake_command

    def test_decorate_with_empty_brackets_should_register_handler(
        self, decorator: ev.EventDecorator, registry: ev.EventRegistry
    ):
        def fake_command():
            pass

        decorator()(fake_command)

        assert registry["fake_command"] is fake_command

    def test_decorate_with_name_should_register_handler(
        self, decorator: ev.EventDecorator, registry: ev.EventRegistry
    ):
        def fake_command():
            pass

        decorator("my_event")(fake_command)

        assert registry["my_event"] is fake_command

    def test_should_call_handler_and_notfier_when_called(
        self, decorator: ev.EventDecorator, registry: ev.EventRegistry
    ):
        emiter = Mock()
        decorator = ev.EventDecorator(emiter=emiter)

        class MyClass:
            @decorator
            def command(self, age, name):
                self.age = age
                self.name = name

        instance = MyClass()
        instance.command(10, name="John")

        emiter.assert_called_once_with(
            instance, ev.Event("command", args={"age": 10, "name": "John"})
        )
        assert instance.name == "John"
        assert instance.age == 10


class TestEventAggregate:
    @pytest.fixture(name="aggregate")
    def given_aggregate(self):
        return ev.EventAggregate()

    def test_instances_should_have_members_initilized_by_metaclass(self):
        aggregate = ev.EventAggregate()
        assert isinstance(aggregate.pending_events, list)

    def test_notify_should_append_event_to_pending_events(
        self, aggregate: ev.EventAggregate
    ):
        event = Mock()
        aggregate.notify(event)

        assert aggregate.pending_events == [event]

    def test_collect_events_should_return_iterable_with_events(
        self, aggregate: ev.EventAggregate
    ):
        event = Mock()

        aggregate.notify(event)

        assert list(aggregate.collect_events()) == [event]
