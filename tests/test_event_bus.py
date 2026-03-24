"""Tests for the EventBus publish-subscribe system."""

from bubbletrack.event_bus import EventBus


class TestSubscribeAndEmit:
    """Verify basic subscribe + emit functionality."""

    def test_subscribe_and_emit(self):
        bus = EventBus()
        results = []
        bus.subscribe("frame_changed", lambda idx: results.append(idx))
        bus.emit("frame_changed", 5)
        assert results == [5]

    def test_multiple_subscribers(self):
        bus = EventBus()
        a, b = [], []
        bus.subscribe("fit_done", lambda r: a.append(r))
        bus.subscribe("fit_done", lambda r: b.append(r))
        bus.emit("fit_done", 3.14)
        assert a == [3.14]
        assert b == [3.14]

    def test_emit_with_kwargs(self):
        bus = EventBus()
        results = []
        bus.subscribe("export", lambda path, fmt: results.append((path, fmt)))
        bus.emit("export", "/tmp/out.mat", fmt="mat")
        assert results == [("/tmp/out.mat", "mat")]


class TestUnsubscribe:
    """Verify subscription removal via token."""

    def test_unsubscribe_stops_delivery(self):
        bus = EventBus()
        results = []
        token = bus.subscribe("x", lambda v: results.append(v))
        bus.emit("x", 1)
        bus.unsubscribe(token)
        bus.emit("x", 2)
        assert results == [1]

    def test_subscribe_returns_unique_tokens(self):
        bus = EventBus()
        t1 = bus.subscribe("a", lambda: None)
        t2 = bus.subscribe("a", lambda: None)
        t3 = bus.subscribe("b", lambda: None)
        assert len({t1, t2, t3}) == 3


class TestEdgeCases:
    """Verify robustness under edge conditions."""

    def test_emit_unknown_event_is_noop(self):
        bus = EventBus()
        bus.emit("nonexistent", 42)  # should not raise

    def test_handler_error_does_not_break_other_handlers(self):
        bus = EventBus()
        results = []

        def bad_handler(v):
            raise ValueError("boom")

        bus.subscribe("x", bad_handler)
        bus.subscribe("x", lambda v: results.append(v))
        bus.emit("x", 42)
        assert results == [42]  # second handler still called
