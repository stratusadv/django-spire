from __future__ import annotations

import threading

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


def test_concurrent_now_monotonic() -> None:
    clock = HybridLogicalClock()
    results: list[int] = []
    lock = threading.Lock()
    barrier = threading.Barrier(8)

    def collect_timestamps() -> None:
        barrier.wait()
        local: list[int] = []

        for _ in range(500):
            local.append(clock.now())

        with lock:
            results.extend(local)

    threads = [
        threading.Thread(target=collect_timestamps)
        for _ in range(8)
    ]

    for t in threads:
        t.start()

    for t in threads:
        t.join(timeout=30)

    assert len(results) == 4000
    assert len(set(results)) == len(results)


def test_concurrent_receive_monotonic() -> None:
    clock = HybridLogicalClock()
    results: list[int] = []
    lock = threading.Lock()
    barrier = threading.Barrier(4)

    def receive_and_collect(base: int) -> None:
        barrier.wait()
        local: list[int] = []

        for i in range(200):
            remote = (base + i) << 16
            local.append(clock.receive(remote))

        with lock:
            results.extend(local)

    threads = [
        threading.Thread(target=receive_and_collect, args=(1000 * i,))
        for i in range(4)
    ]

    for t in threads:
        t.start()

    for t in threads:
        t.join(timeout=30)

    assert len(results) == 800
    assert len(set(results)) == len(results)


def test_interleaved_now_and_receive() -> None:
    clock = HybridLogicalClock()
    results: list[int] = []
    lock = threading.Lock()
    barrier = threading.Barrier(4)

    def call_now() -> None:
        barrier.wait()
        local: list[int] = []

        for _ in range(300):
            local.append(clock.now())

        with lock:
            results.extend(local)

    def call_receive(base: int) -> None:
        barrier.wait()
        local: list[int] = []

        for i in range(300):
            remote = (base + i) << 16
            local.append(clock.receive(remote))

        with lock:
            results.extend(local)

    threads = [
        threading.Thread(target=call_now),
        threading.Thread(target=call_now),
        threading.Thread(target=call_receive, args=(5000,)),
        threading.Thread(target=call_receive, args=(9000,)),
    ]

    for t in threads:
        t.start()

    for t in threads:
        t.join(timeout=30)

    assert len(results) == 1200
    assert len(set(results)) == len(results)
