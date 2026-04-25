from __future__ import annotations

import threading
import time

from django_spire.contrib.sync.core.exceptions import ClockOverflowError


_COUNTER_BITS = 16
_COUNTER_MASK = (1 << _COUNTER_BITS) - 1
_SPINS_MAX = 100


class HybridLogicalClock:
    def __init__(self) -> None:
        self._last = 0
        self._lock = threading.Lock()

    def _physical(self) -> int:
        return int(time.time() * 1000)

    def now(self) -> int:
        for _ in range(_SPINS_MAX):
            with self._lock:
                physical_time = self._physical()
                wall_old = self._last >> _COUNTER_BITS
                counter_old = self._last & _COUNTER_MASK

                if physical_time > wall_old:
                    wall, counter = physical_time, 0
                else:
                    wall, counter = wall_old, counter_old + 1

                if counter <= _COUNTER_MASK:
                    self._last = (wall << _COUNTER_BITS) | counter
                    return self._last

            time.sleep(0.001)

        message = (
            f'HLC counter overflow: unable to advance '
            f'after {_SPINS_MAX} attempts'
        )

        raise ClockOverflowError(message)

    def receive(self, remote: int) -> int:
        for _ in range(_SPINS_MAX):
            with self._lock:
                physical_time = self._physical()
                wall_old = self._last >> _COUNTER_BITS
                counter_old = self._last & _COUNTER_MASK
                wall_remote = remote >> _COUNTER_BITS
                counter_remote = remote & _COUNTER_MASK

                wall = max(physical_time, wall_old, wall_remote)

                if wall == wall_old == wall_remote:
                    counter = max(counter_old, counter_remote) + 1
                elif wall == wall_old:
                    counter = counter_old + 1
                elif wall == wall_remote:
                    counter = counter_remote + 1
                else:
                    counter = 0

                if counter <= _COUNTER_MASK:
                    self._last = (wall << _COUNTER_BITS) | counter
                    return self._last

            time.sleep(0.001)

        message = (
            f'HLC counter overflow: unable to advance '
            f'after {_SPINS_MAX} attempts'
        )

        raise ClockOverflowError(message)

    def update(self, remote: int) -> None:
        self.receive(remote)
