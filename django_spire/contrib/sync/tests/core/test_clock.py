from __future__ import annotations

from django_spire.contrib.sync.core.clock import HybridLogicalClock


def test_monotonic() -> None:
    clock = HybridLogicalClock()
    timestamps = [clock.now() for _ in range(100)]

    assert timestamps == sorted(timestamps)
    assert len(set(timestamps)) == 100


def test_counter_increments_same_millisecond() -> None:
    clock = HybridLogicalClock()
    clock._physical = lambda: 1000

    a = clock.now()
    b = clock.now()
    c = clock.now()

    assert a < b < c
    assert (a >> 16) == (b >> 16) == (c >> 16) == 1000
    assert (a & 0xFFFF) == 0
    assert (b & 0xFFFF) == 1
    assert (c & 0xFFFF) == 2


def test_physical_advance_resets_counter() -> None:
    clock = HybridLogicalClock()

    ms = [1000]
    clock._physical = lambda: ms[0]

    clock.now()
    clock.now()

    ms[0] = 2000

    ts = clock.now()

    assert (ts >> 16) == 2000
    assert (ts & 0xFFFF) == 0


def test_receive_absorbs_future_remote() -> None:
    clock = HybridLogicalClock()
    local = clock.now()

    future_ms = (local >> 16) + 60_000
    future_ts = future_ms << 16

    after = clock.receive(future_ts)

    assert after > future_ts
    assert after > local


def test_receive_behind_remote() -> None:
    clock = HybridLogicalClock()

    first = clock.now()
    past_ts = 1 << 16

    result = clock.receive(past_ts)

    assert result > first
    assert result > past_ts


def test_receive_same_logical_increments_counter() -> None:
    clock = HybridLogicalClock()
    clock._physical = lambda: 1000

    clock.now()

    remote = 1000 << 16 | 5

    result = clock.receive(remote)

    assert (result >> 16) == 1000
    assert (result & 0xFFFF) == 6


def test_never_goes_backward() -> None:
    clock = HybridLogicalClock()

    ms = [5000]
    clock._physical = lambda: ms[0]

    a = clock.now()

    ms[0] = 3000

    b = clock.now()

    assert b > a
