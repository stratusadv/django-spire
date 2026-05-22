from __future__ import annotations

import copy

from typing import Any


_MUTABLE_TYPES = (dict, list, set, bytearray)


class FieldUpdateTracker:
    def __init__(self) -> None:
        self._original: dict[str, Any] = {}

    def get_dirty(self, current: dict[str, Any]) -> set[str]:
        dirty: set[str] = set()

        for key, value in current.items():
            if key not in self._original or self._original[key] != value:
                dirty.add(key)

        return dirty

    def snapshot(self, fields: dict[str, Any]) -> None:
        self._original = {
            key: copy.deepcopy(value) if isinstance(value, _MUTABLE_TYPES) else value
            for key, value in fields.items()
        }
