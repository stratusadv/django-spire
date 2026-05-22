from __future__ import annotations

from typing import Any, Protocol, TYPE_CHECKING

if TYPE_CHECKING:
    from pathlib import Path


class Reader(Protocol):
    def read(self, file_path: str | Path) -> list[dict[str, Any]]: ...
