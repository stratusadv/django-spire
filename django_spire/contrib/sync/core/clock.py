from __future__ import annotations

import threading
import time

from django_spire.contrib.sync.core.exceptions import (
    ClockOverflowError,
    InvalidParameterError,
)


_COUNTER_BITS = 16
_COUNTER_MASK = (1 << _COUNTER_BITS) - 1
_SPINS_MAX = 100

if _COUNTER_BITS < 1 or _COUNTER_BITS > 62:
    message = '_COUNTER_BITS must be in [1, 62], got {_COUNTER_BITS}'
    raise ValueError(message)

if _SPINS_MAX < 1:
    message = f'_SPINS_MAX must be >= 1, got {_SPINS_MAX}'
    raise ValueError(message)


class HybridLogicalClock:
    def __init__(self) -> None:
        self._last = 0
        self._lock = threading.Lock()

    def _physical(self) -> int:
        physical_time = int(time.time() * 1000)

        if physical_time < 0:
            message = 'A physical clock returned a negative timestamp'
            raise ClockOverflowError(message)

        return physical_time

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
                    previous = self._last
                    self._last = (wall << _COUNTER_BITS) | counter

                    if self._last <= previous:
                        message = (
                            f'HLC monotonicity violated: '
                            f'{self._last} <= {previous}'
                        )

                        raise ClockOverflowError(message)

                    return self._last

            time.sleep(0.001)

        message = (
            f'HLC counter overflow: unable to advance '
            f'after {_SPINS_MAX} attempts'
        )

        raise ClockOverflowError(message)

    def receive(self, remote: int) -> int:
        if remote < 0:
            message = (
                f'The remote timestamp must be non-negative, '
                f'got {remote}'
            )

            raise InvalidParameterError(message)

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
                    previous = self._last
                    self._last = (wall << _COUNTER_BITS) | counter

                    if self._last <= previous:
                        message = (
                            f'HLC monotonicity violated: '
                            f'{self._last} <= {previous}'
                        )

                        raise ClockOverflowError(message)

                    return self._last

            time.sleep(0.001)

        message = (
            f'HLC counter overflow: unable to advance '
            f'after {_SPINS_MAX} attempts'
        )
        raise ClockOverflowError(message)

    def update(self, remote: int) -> None:
        self.receive(remote)
