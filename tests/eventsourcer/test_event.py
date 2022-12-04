from unittest.mock import Mock, patch
import pytest

from eventsourcer import event as ev


class Test_event_notifier:
    def test_should_call_listener_notify(self):
        class Listener(ev.EventListener):
            notified: ev.Event = None

            def notify(self, event: ev.Event):
                self.notified = event

        listener = Listener()
        event = Mock()

        ev.event_notifier(listener, event)

        assert listener.notified is event

    def test_should_call_notify_ductyping(self):
        class Listener:
            notified: ev.Event = None

            def notify(self, event: ev.Event):
                self.notified = event

        listener = Listener()
        event = Mock()

        ev.event_notifier(listener, event)

        assert listener.notified is event

    def test_should_raise_assertionerror_not_listener(self):
        class Listener:
            pass

        listener = Listener()
        event = Mock()

        with pytest.raises(AssertionError):
            ev.event_notifier(listener, event)


class TestEventBus:
    @pytest.fixture(name="bus")
    def given_bus(self):
        return ev.EventBus()

    def test_should_initialize_defaults(self):
        bus = ev.EventBus()
        assert isinstance(bus, ev.EventBus)
        assert isinstance(bus._handlers, dict)
        assert bus._notifier is ev.event_notifier

    def test_should_initialize_with_args(self):
        notifier = Mock()

        bus = ev.EventBus(notifier)

        assert bus._notifier is notifier

    def test_register_should_add_handler(self, bus: ev.EventBus):
        handler = Mock()

        bus.register("my_event", handler)

        assert bus._handlers["my_event"] is handler

    def test_register_should_raise_keyerror_event_with_different_handler_already_register(
        slef, bus: ev.EventBus
    ):
        handler1 = Mock()
        handler2 = Mock()
        bus.register("my_event", handler1)

        with pytest.raises(KeyError):
            bus.register("my_event", handler2)

    def test_register_should_accept_full_dulicate_registrtion(self, bus: ev.EventBus):
        handler = Mock()
        bus.register("my_event", handler)

        bus.register("my_event", handler)

        assert bus._handlers["my_event"] is handler

    def test_dict_access_should_return_registered_handler(self, bus: ev.EventBus):
        handler = Mock()
        bus.register("my_event", handler)

        assert bus["my_event"] is handler

    def test_get_should_return_registered_handler(self, bus: ev.EventBus):
        handler = Mock()
        bus.register("my_event", handler)

        assert bus.get("my_event") is handler

    def test_get_should_return_passed_default_for_unregistered_handler(
        self, bus: ev.EventBus
    ):
        handler = Mock()

        assert bus.get("my_event", handler) is handler

    def test_get_should_raise_keyerror_default_not_passed_for_unregistered_handler(
        self, bus: ev.EventBus
    ):
        with pytest.raises(KeyError):
            bus.get("my_event")

    def test_bool_should_be_true(self, bus: ev.EventBus):
        assert bool(bus)

    def test_handle_should_invoke_handler_with_event_args(self, bus: ev.EventBus):
        instance = Mock()
        handler = Mock()
        event = ev.Event("my_event", {"a": 1})
        bus.register("my_event", handler)

        bus.handle(instance, event)

        handler.assert_called_once_with(instance, **event.args)

    def test_emit_should_notify(self):
        instance = Mock()
        handler = Mock()
        notifier = Mock()
        bus = ev.EventBus(notifier)
        event = ev.Event("my_event", {"a": 1})
        bus.register("my_event", handler)

        with patch.object(bus, "handle") as handle_mock:
            bus.emit(instance, event)
            handle_mock.assert_called_once_with(instance, event)

        notifier.assert_called_once_with(instance, event)


class TestEventDecorator:
    @pytest.fixture(name="bus")
    def given_bus(self):
        return ev.EventBus()

    @pytest.fixture(name="decorator")
    def given_decorator(self, bus):
        return ev.EventDecorator(bus)

    def test_should_initialize_instance_with_defaults(self):
        decorator = ev.EventDecorator()
        assert isinstance(decorator._bus, ev.EventBus)

    def test_should_initialize_instance_with_passed_values(self):
        bus = Mock()
        decorator = ev.EventDecorator(bus)
        assert decorator._bus is bus

    def test_decorate_without_brackets_should_register_handler(
        self, decorator: ev.EventDecorator, bus: ev.EventBus
    ):
        def fake_command():
            pass

        decorator(fake_command)

        assert bus["fake_command"] is fake_command

    def test_decorate_with_empty_brackets_should_register_handler(
        self, decorator: ev.EventDecorator, bus: ev.EventBus
    ):
        def fake_command():
            pass

        decorator()(fake_command)

        assert bus["fake_command"] is fake_command

    def test_decorate_with_name_should_register_handler(
        self, decorator: ev.EventDecorator, bus: ev.EventBus
    ):
        def fake_command():
            pass

        decorator("my_event")(fake_command)

        assert bus["my_event"] is fake_command


class TestEventAggregate:
    @pytest.fixture(name="aggregate")
    def given_aggregate(self):
        return ev.EventAggregate()

    def test_instances_should_have_members_initilized_by_metaclass(self):
        aggregate = ev.EventAggregate()
        assert isinstance(aggregate._pending_events, list)

    def test_notify_should_append_event_to_pending_events(
        self, aggregate: ev.EventAggregate
    ):
        event = Mock()
        aggregate.notify(event)

        assert aggregate._pending_events == [event]

    def test_collect_events_should_return_iterable_with_events(
        self, aggregate: ev.EventAggregate
    ):
        event = Mock()
        assert aggregate._pending_events == []

        aggregate.notify(event)

        assert list(aggregate.collect_events()) == [event]
