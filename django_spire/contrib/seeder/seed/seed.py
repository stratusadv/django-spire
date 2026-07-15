from typing import Any


class Seed:
    def __init__(self, fields_values: dict[str, Any]) -> None:
        self._fields_values = fields_values

    def __getitem__(self, key: str) -> Any:
        return self._fields_values[key]

    def __setitem__(self, key: str, value: Any) -> None:
        self._fields_values[key] = value

    def __delitem__(self, key: str) -> None:
        del self._fields_values[key]

    def __repr__(self) -> str:
        return repr(self._fields_values)

    def to_dict(self) -> dict[str, Any]:
        return self._fields_values
