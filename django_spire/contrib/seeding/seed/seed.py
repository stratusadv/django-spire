from typing import Any


class Seed:  # noqa: PLW1641
    def __init__(self, fields_values: dict[str, Any]) -> None:
        self._fields_values = dict(fields_values)

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Seed):
            return NotImplemented

        return self._fields_values == other._fields_values

    def __getitem__(self, key: str) -> Any:
        return self._fields_values[key]

    def __setitem__(self, key: str, value: Any) -> None:
        self._fields_values[key] = value

    def __delitem__(self, key: str) -> None:
        del self._fields_values[key]

    def __repr__(self) -> str:
        return repr(self._fields_values)

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Seed):
            return NotImplemented
        return self._fields_values == other._fields_values

    def __hash__(self) -> int:
        return hash(id(self._fields_values))

    def to_dict(self) -> dict[str, Any]:
        return dict(self._fields_values)
