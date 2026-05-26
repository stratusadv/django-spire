from __future__ import annotations

from typing import Any


class SyncOracle:
    def __init__(self) -> None:
        self._field_state: dict[tuple[str, str, str], tuple[Any, int]] = {}

    def record_write(
        self,
        model_label: str,
        key: str,
        data: dict[str, Any],
        timestamps: dict[str, int],
    ) -> None:
        for field, ts in timestamps.items():
            state_key = (model_label, key, field)
            current = self._field_state.get(state_key)

            if current is None or ts > current[1]:
                self._field_state[state_key] = (data.get(field), ts)

    def expected_data(self, model_label: str, key: str) -> dict[str, Any] | None:
        data: dict[str, Any] = {}

        for (m, k, field), (value, _) in self._field_state.items():
            if m == model_label and k == key:
                data[field] = value

        if not data:
            return None

        data['id'] = key
        return data

    def expected_keys(self, model_label: str) -> set[str]:
        return {k for m, k, _ in self._field_state if m == model_label}
