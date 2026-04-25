from __future__ import annotations

from typing import Protocol, TYPE_CHECKING

if TYPE_CHECKING:
    from pathlib import Path


class Store(Protocol):
    def upload(
        self,
        key: str,
        source_path: Path,
        content_type: str | None = None,
    ) -> str: ...
