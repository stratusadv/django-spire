from __future__ import annotations

from typing import Any, Protocol, TYPE_CHECKING

if TYPE_CHECKING:
    from pathlib import Path


class Writer(Protocol):
    def write(self, file_path: str | Path, records: list[dict[str, Any]]) -> None: ...
